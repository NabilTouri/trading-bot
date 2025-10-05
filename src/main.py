import sys
import argparse
from datetime import datetime, timedelta
from loguru import logger
import pandas as pd
from pathlib import Path

from config.settings import settings
from src.data.mt5_provider import MT5Provider
from src.data.twelvedata_provider import TwelveDataProvider
from src.strategy.ema_vwap_strategy import EMAVWAPStrategy
from src.risk.manager import RiskManager
from src.execution.paper_trader import PaperTrader
from src.execution.mt5_executor import MT5Executor
from src.backtest.backtester import Backtester


# Setup logging
log_path = Path("logs")
log_path.mkdir(exist_ok=True)
logger.add(
    "logs/trading_bot.log",
    rotation="1 day",
    retention="30 days",
    level=settings.log_level
)


def run_backtest(args):
    logger.info("=== BACKTEST MODE ===")
    
    # Inizializza data provider
    mt5 = MT5Provider(settings.mt5_login, settings.mt5_password, settings.mt5_server)
    
    if not mt5.connect():
        logger.error("Failed to connect to MT5")
        return
    
    try:
        # Recupera dati storici
        start_date = datetime.strptime(args.start, '%Y-%m-%d')
        end_date = datetime.strptime(args.end, '%Y-%m-%d')
        
        for symbol in settings.symbols:
            logger.info(f"Backtesting {symbol}...")
            
            data = mt5.get_historical_data(
                symbol=symbol,
                timeframe=settings.timeframe,
                start=start_date,
                end=end_date
            )
            
            if data is None or data.empty:
                logger.warning(f"No data for {symbol}, skipping")
                continue
            
            # Esegui backtest
            backtester = Backtester(
                initial_capital=settings.initial_capital,
                commission=0.0001
            )
            
            strategy_params = {
                'ema_fast': settings.ema_fast,
                'ema_slow': settings.ema_slow,
                'atr_period': settings.atr_period,
                'atr_sl_multiplier': settings.atr_sl_multiplier,
                'atr_tp_multiplier': settings.atr_tp_multiplier,
                'risk_percent': settings.risk_percent
            }
            
            results = backtester.run(data, strategy_params)
            
            # Stampa risultati
            logger.info(f"\n{'='*50}")
            logger.info(f"BACKTEST RESULTS - {symbol}")
            logger.info(f"{'='*50}")
            logger.info(f"Initial Capital: ${results['initial_value']:.2f}")
            logger.info(f"Final Capital: ${results['final_value']:.2f}")
            logger.info(f"Total Return: {results['total_return']:.2f}%")
            logger.info(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
            logger.info(f"Max Drawdown: {results['max_drawdown']:.2f}%")
            logger.info(f"Total Trades: {results['total_trades']}")
            logger.info(f"Win Rate: {results['win_rate']:.2f}%")
            logger.info(f"{'='*50}\n")
    
    finally:
        mt5.disconnect()


def run_paper_trading():
    logger.info("=== PAPER TRADING MODE ===")
    
    # Inizializza componenti
    mt5 = MT5Provider(settings.mt5_login, settings.mt5_password, settings.mt5_server)
    strategy = EMAVWAPStrategy(
        ema_fast=settings.ema_fast,
        ema_slow=settings.ema_slow,
        atr_period=settings.atr_period,
        atr_sl_multiplier=settings.atr_sl_multiplier,
        atr_tp_multiplier=settings.atr_tp_multiplier
    )
    risk_manager = RiskManager(
        risk_percent=settings.risk_percent,
        initial_capital=settings.initial_capital
    )
    paper_trader = PaperTrader(initial_capital=settings.initial_capital)
    
    if not mt5.connect():
        logger.error("Failed to connect to MT5")
        return
    
    try:
        import time
        
        while True:
            for symbol in settings.symbols:
                # Verifica se c'è già una posizione aperta
                open_positions = paper_trader.get_open_positions(symbol)
                if open_positions:
                    continue
                
                # Recupera dati recenti
                end_date = datetime.now()
                start_date = end_date - timedelta(days=7)
                
                data = mt5.get_historical_data(
                    symbol=symbol,
                    timeframe=settings.timeframe,
                    start=start_date,
                    end=end_date
                )
                
                if data is None or len(data) < 50:
                    continue
                
                # Aggiorna posizioni esistenti
                paper_trader.update(symbol, data.iloc[-1])
                
                # Genera segnale
                signal = strategy.get_current_signal(data)
                
                if signal and risk_manager.can_open_position():
                    # Calcola position size
                    size = risk_manager.calculate_position_size(
                        signal['entry_price'],
                        signal['sl'],
                        symbol
                    )
                    
                    # Apri posizione paper
                    paper_trader.open_position(
                        symbol=symbol,
                        direction=signal['direction'],
                        entry_price=signal['entry_price'],
                        size=size,
                        sl=signal['sl'],
                        tp=signal['tp']
                    )
                    
                    risk_manager.open_position()
            
            # Stampa statistiche ogni 10 iterazioni
            stats = paper_trader.get_statistics()
            if stats:
                logger.info(f"Current Capital: ${paper_trader.capital:.2f} | "
                          f"Trades: {stats.get('total_trades', 0)} | "
                          f"Win Rate: {stats.get('win_rate', 0):.1f}%")
            
            # Attendi prossimo ciclo (es: ogni 1 minuto)
            time.sleep(60)
    
    except KeyboardInterrupt:
        logger.info("Paper trading stopped by user")
        
        # Stampa statistiche finali
        stats = paper_trader.get_statistics()
        if stats:
            logger.info(f"\n{'='*50}")
            logger.info("PAPER TRADING FINAL STATISTICS")
            logger.info(f"{'='*50}")
            logger.info(f"Initial Capital: ${stats['initial_capital']:.2f}")
            logger.info(f"Final Capital: ${stats['final_capital']:.2f}")
            logger.info(f"Total Return: {stats['total_return']:.2f}%")
            logger.info(f"Total Trades: {stats['total_trades']}")
            logger.info(f"Win Rate: {stats['win_rate']:.2f}%")
            logger.info(f"Average Profit: ${stats['average_profit']:.2f}")
            logger.info(f"{'='*50}\n")
    
    finally:
        mt5.disconnect()


def run_live_trading():
    logger.info("=== LIVE TRADING MODE ===")
    logger.warning("ATTENZIONE: Stai per eseguire trading reale!")
    
    response = input("Sei sicuro di voler continuare? (yes/no): ")
    if response.lower() != 'yes':
        logger.info("Live trading cancelled")
        return
    
    # Inizializza componenti
    mt5 = MT5Provider(settings.mt5_login, settings.mt5_password, settings.mt5_server)
    strategy = EMAVWAPStrategy(
        ema_fast=settings.ema_fast,
        ema_slow=settings.ema_slow,
        atr_period=settings.atr_period,
        atr_sl_multiplier=settings.atr_sl_multiplier,
        atr_tp_multiplier=settings.atr_tp_multiplier
    )
    risk_manager = RiskManager(
        risk_percent=settings.risk_percent,
        initial_capital=settings.initial_capital
    )
    executor = MT5Executor(mt5)
    
    if not mt5.connect():
        logger.error("Failed to connect to MT5")
        return
    
    try:
        import time
        
        while True:
            # Aggiorna capitale dal conto reale
            account_info = mt5.get_account_info()
            if account_info:
                risk_manager.update_capital(account_info['balance'])
            
            for symbol in settings.symbols:
                # Verifica se c'è già una posizione aperta
                if symbol in executor.get_active_positions():
                    continue
                
                # Recupera dati recenti
                end_date = datetime.now()
                start_date = end_date - timedelta(days=7)
                
                data = mt5.get_historical_data(
                    symbol=symbol,
                    timeframe=settings.timeframe,
                    start=start_date,
                    end=end_date
                )
                
                if data is None or len(data) < 50:
                    continue
                
                # Genera segnale
                signal = strategy.get_current_signal(data)
                
                if signal and risk_manager.can_open_position():
                    # Calcola position size
                    size = risk_manager.calculate_position_size(
                        signal['entry_price'],
                        signal['sl'],
                        symbol
                    )
                    
                    # Esegui trade reale
                    order_id = executor.execute_trade(
                        symbol=symbol,
                        direction=signal['direction'],
                        size=size,
                        sl=signal['sl'],
                        tp=signal['tp']
                    )
                    
                    if order_id:
                        risk_manager.open_position()
            
            # Attendi prossimo ciclo
            time.sleep(60)
    
    except KeyboardInterrupt:
        logger.info("Live trading stopped by user")
    
    finally:
        mt5.disconnect()


def main():
    parser = argparse.ArgumentParser(description='Forex Intraday Trading Bot')
    parser.add_argument(
        '--mode', 
        type=str, 
        default=settings.mode,
        choices=['backtest', 'paper', 'live'],
        help='Trading mode'
    )
    parser.add_argument('--start', type=str, help='Backtest start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, help='Backtest end date (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    logger.info(f"Starting Forex Trading Bot in {args.mode} mode")
    
    if args.mode == 'backtest':
        if not args.start or not args.end:
            logger.error("Backtest mode requires --start and --end dates")
            sys.exit(1)
        run_backtest(args)
    elif args.mode == 'paper':
        run_paper_trading()
    elif args.mode == 'live':
        run_live_trading()


if __name__ == "__main__":
    main()