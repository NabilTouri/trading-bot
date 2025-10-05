import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger
from typing import Optional


class MT5Provider:
    def __init__(self, login: int, password: str, server: str):
        self.login = login
        self.password = password
        self.server = server
        self.connected = False
    
    def connect(self) -> bool:
        if not mt5.initialize():
            logger.error("MT5 initialization failed")
            return False
        
        if not mt5.login(self.login, self.password, self.server):
            logger.error(f"MT5 login failed: {mt5.last_error()}")
            return False
        
        self.connected = True
        logger.info(f"Connected to MT5: {self.server}")
        return True
    
    def disconnect(self):
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info("Disconnected from MT5")
    
    def get_historical_data(
        self, 
        symbol: str, 
        timeframe: int, 
        start: datetime, 
        end: datetime
    ) -> Optional[pd.DataFrame]:
        if not self.connected:
            logger.error("Not connected to MT5")
            return None
        
        # Converti timeframe minuti a MT5 timeframe
        tf_map = {
            1: mt5.TIMEFRAME_M1,
            5: mt5.TIMEFRAME_M5,
            15: mt5.TIMEFRAME_M15,
            30: mt5.TIMEFRAME_M30,
            60: mt5.TIMEFRAME_H1,
        }
        
        mt5_timeframe = tf_map.get(timeframe, mt5.TIMEFRAME_M5)
        
        rates = mt5.copy_rates_range(symbol, mt5_timeframe, start, end)
        
        if rates is None or len(rates) == 0:
            logger.warning(f"No data retrieved for {symbol}")
            return None
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'tick_volume': 'Volume'
        }, inplace=True)
        
        logger.info(f"Retrieved {len(df)} bars for {symbol}")
        return df[['Open', 'High', 'Low', 'Close', 'Volume']]
    
    def get_account_info(self) -> dict:
        if not self.connected:
            return {}
        
        account = mt5.account_info()
        if account is None:
            return {}
        
        return {
            'balance': account.balance,
            'equity': account.equity,
            'margin': account.margin,
            'free_margin': account.margin_free,
            'profit': account.profit
        }
    
    def place_order(
        self, 
        symbol: str, 
        order_type: str, 
        volume: float, 
        sl: float, 
        tp: float,
        comment: str = ""
    ) -> Optional[int]:
        if not self.connected:
            logger.error("Not connected to MT5")
            return None
        
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).ask if order_type == 'buy' else mt5.symbol_info_tick(symbol).bid
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_BUY if order_type == 'buy' else mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 234000,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Order failed: {result.retcode} - {result.comment}")
            return None
        
        logger.info(f"Order placed: {order_type} {volume} {symbol} @ {price}")
        return result.order