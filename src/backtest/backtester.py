import backtrader as bt
import pandas as pd
from datetime import datetime
from loguru import logger
from src.strategy.ema_vwap_strategy import EMAVWAPStrategy


class EMAVWAPBTStrategy(bt.Strategy):
    params = (
        ('ema_fast', 9),
        ('ema_slow', 21),
        ('atr_period', 14),
        ('atr_sl_multiplier', 2.0),
        ('atr_tp_multiplier', 3.0),
        ('risk_percent', 1.0),
    )
    
    def __init__(self):
        self.ema_fast = bt.indicators.EMA(self.data.close, period=self.params.ema_fast)
        self.ema_slow = bt.indicators.EMA(self.data.close, period=self.params.ema_slow)
        self.atr = bt.indicators.ATR(self.data, period=self.params.atr_period)
        
        # VWAP calculation
        typical_price = (self.data.high + self.data.low + self.data.close) / 3
        self.vwap = bt.indicators.SumN(typical_price * self.data.volume, period=20) / \
                    bt.indicators.SumN(self.data.volume, period=20)
        
        self.order = None
        self.trades_count = 0
    
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                logger.info(f'BUY EXECUTED: {order.executed.price:.5f}')
            elif order.issell():
                logger.info(f'SELL EXECUTED: {order.executed.price:.5f}')
            self.order = None
    
    def notify_trade(self, trade):
        if trade.isclosed:
            logger.info(f'TRADE PROFIT: {trade.pnl:.2f}')
            self.trades_count += 1
    
    def next(self):
        if self.order:
            return
        
        # Condizioni per LONG
        if self.ema_fast[0] > self.ema_slow[0] and \
           self.data.close[0] > self.vwap[0] and \
           not self.position:
            
            # Calcola position size basato su risk management
            risk_amount = self.broker.getvalue() * (self.params.risk_percent / 100)
            sl_distance = self.params.atr_sl_multiplier * self.atr[0]
            size = risk_amount / sl_distance
            size = max(0.01, min(size, 10.0))  # Limita tra 0.01 e 10
            
            # Calcola SL e TP
            sl_price = self.data.close[0] - (self.params.atr_sl_multiplier * self.atr[0])
            tp_price = self.data.close[0] + (self.params.atr_tp_multiplier * self.atr[0])
            
            self.order = self.buy(size=size)
            self.sell(size=size, exectype=bt.Order.Stop, price=sl_price)
            self.sell(size=size, exectype=bt.Order.Limit, price=tp_price)
        
        # Condizioni per SHORT
        elif self.ema_fast[0] < self.ema_slow[0] and \
             self.data.close[0] < self.vwap[0] and \
             not self.position:
            
            risk_amount = self.broker.getvalue() * (self.params.risk_percent / 100)
            sl_distance = self.params.atr_sl_multiplier * self.atr[0]
            size = risk_amount / sl_distance
            size = max(0.01, min(size, 10.0))
            
            sl_price = self.data.close[0] + (self.params.atr_sl_multiplier * self.atr[0])
            tp_price = self.data.close[0] - (self.params.atr_tp_multiplier * self.atr[0])
            
            self.order = self.sell(size=size)
            self.buy(size=size, exectype=bt.Order.Stop, price=sl_price)
            self.buy(size=size, exectype=bt.Order.Limit, price=tp_price)


class Backtester:
    def __init__(
        self, 
        initial_capital: float = 10000.0,
        commission: float = 0.0001
    ):
        self.initial_capital = initial_capital
        self.commission = commission
        self.cerebro = None
    
    def run(
        self, 
        data: pd.DataFrame, 
        strategy_params: dict = None
    ) -> dict:
        self.cerebro = bt.Cerebro()
        
        # Converti DataFrame in formato Backtrader
        bt_data = bt.feeds.PandasData(
            dataname=data,
            datetime=None,
            open='Open',
            high='High',
            low='Low',
            close='Close',
            volume='Volume',
            openinterest=-1
        )
        
        self.cerebro.adddata(bt_data)
        
        # Aggiungi strategia
        if strategy_params:
            self.cerebro.addstrategy(EMAVWAPBTStrategy, **strategy_params)
        else:
            self.cerebro.addstrategy(EMAVWAPBTStrategy)
        
        # Setup broker
        self.cerebro.broker.setcash(self.initial_capital)
        self.cerebro.broker.setcommission(commission=self.commission)
        
        # Aggiungi analizzatori
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        
        logger.info(f'Starting Portfolio Value: {self.cerebro.broker.getvalue():.2f}')
        
        # Esegui backtest
        results = self.cerebro.run()
        strat = results[0]
        
        final_value = self.cerebro.broker.getvalue()
        logger.info(f'Final Portfolio Value: {final_value:.2f}')
        
        # Estrai metriche
        sharpe = strat.analyzers.sharpe.get_analysis()
        drawdown = strat.analyzers.drawdown.get_analysis()
        trades = strat.analyzers.trades.get_analysis()
        returns = strat.analyzers.returns.get_analysis()
        
        return {
            'initial_value': self.initial_capital,
            'final_value': final_value,
            'total_return': ((final_value - self.initial_capital) / self.initial_capital) * 100,
            'sharpe_ratio': sharpe.get('sharperatio', 0),
            'max_drawdown': drawdown.max.drawdown,
            'total_trades': trades.total.closed if hasattr(trades.total, 'closed') else 0,
            'won_trades': trades.won.total if hasattr(trades, 'won') else 0,
            'lost_trades': trades.lost.total if hasattr(trades, 'lost') else 0,
            'win_rate': (trades.won.total / trades.total.closed * 100) 
                       if hasattr(trades.total, 'closed') and trades.total.closed > 0 else 0
        }