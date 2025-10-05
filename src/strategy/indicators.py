import pandas as pd
import numpy as np
from typing import Tuple


def calculate_ema(data: pd.Series, period: int) -> pd.Series:
    return data.ewm(span=period, adjust=False).mean()


def calculate_vwap(df: pd.DataFrame) -> pd.Series:
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    return (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    
    return atr


def add_all_indicators(
    df: pd.DataFrame, 
    ema_fast: int = 9, 
    ema_slow: int = 21, 
    atr_period: int = 14
) -> pd.DataFrame:
    df = df.copy()
    df['EMA_Fast'] = calculate_ema(df['Close'], ema_fast)
    df['EMA_Slow'] = calculate_ema(df['Close'], ema_slow)
    df['VWAP'] = calculate_vwap(df)
    df['ATR'] = calculate_atr(df, atr_period)
    return df