import pandas as pd
from typing import Optional, Tuple
from loguru import logger
from src.strategy.indicators import add_all_indicators


class EMAVWAPStrategy:
    def __init__(
        self,
        ema_fast: int = 9,
        ema_slow: int = 21,
        atr_period: int = 14,
        atr_sl_multiplier: float = 2.0,
        atr_tp_multiplier: float = 3.0
    ):
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        self.atr_period = atr_period
        self.atr_sl_multiplier = atr_sl_multiplier
        self.atr_tp_multiplier = atr_tp_multiplier
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = add_all_indicators(
            df, 
            self.ema_fast, 
            self.ema_slow, 
            self.atr_period
        )
        
        # Segnali di entrata
        df['Long_Signal'] = (
            (df['EMA_Fast'] > df['EMA_Slow']) & 
            (df['Close'] > df['VWAP'])
        )
        
        df['Short_Signal'] = (
            (df['EMA_Fast'] < df['EMA_Slow']) & 
            (df['Close'] < df['VWAP'])
        )
        
        # Identifica crossover per evitare segnali continui
        df['Long_Entry'] = (
            df['Long_Signal'] & 
            ~df['Long_Signal'].shift(1).fillna(False)
        )
        
        df['Short_Entry'] = (
            df['Short_Signal'] & 
            ~df['Short_Signal'].shift(1).fillna(False)
        )
        
        return df
    
    def calculate_stops(
        self, 
        entry_price: float, 
        atr: float, 
        direction: str
    ) -> Tuple[float, float]:
        if direction == 'long':
            sl = entry_price - (self.atr_sl_multiplier * atr)
            tp = entry_price + (self.atr_tp_multiplier * atr)
        else:  # short
            sl = entry_price + (self.atr_sl_multiplier * atr)
            tp = entry_price - (self.atr_tp_multiplier * atr)
        
        return round(sl, 5), round(tp, 5)
    
    def get_current_signal(self, df: pd.DataFrame) -> Optional[dict]:
        if len(df) < max(self.ema_slow, self.atr_period) + 1:
            return None
        
        df = self.generate_signals(df)
        last_row = df.iloc[-1]
        
        if last_row['Long_Entry']:
            sl, tp = self.calculate_stops(
                last_row['Close'], 
                last_row['ATR'], 
                'long'
            )
            return {
                'direction': 'long',
                'entry_price': last_row['Close'],
                'sl': sl,
                'tp': tp,
                'atr': last_row['ATR']
            }
        
        if last_row['Short_Entry']:
            sl, tp = self.calculate_stops(
                last_row['Close'], 
                last_row['ATR'], 
                'short'
            )
            return {
                'direction': 'short',
                'entry_price': last_row['Close'],
                'sl': sl,
                'tp': tp,
                'atr': last_row['ATR']
            }
        
        return None