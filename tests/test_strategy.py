import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.strategy.ema_vwap_strategy import EMAVWAPStrategy
from src.strategy.indicators import calculate_ema, calculate_vwap, calculate_atr


@pytest.fixture
def sample_data():
    dates = pd.date_range(start='2024-01-01', periods=100, freq='5min')
    np.random.seed(42)
    
    data = pd.DataFrame({
        'Open': np.random.uniform(1.08, 1.10, 100),
        'High': np.random.uniform(1.08, 1.10, 100),
        'Low': np.random.uniform(1.08, 1.10, 100),
        'Close': np.random.uniform(1.08, 1.10, 100),
        'Volume': np.random.randint(100, 1000, 100)
    }, index=dates)
    
    # Assicura che High >= Low
    data['High'] = data[['Open', 'High', 'Close']].max(axis=1)
    data['Low'] = data[['Open', 'Low', 'Close']].min(axis=1)
    
    return data


def test_calculate_ema(sample_data):
    ema = calculate_ema(sample_data['Close'], 9)
    
    assert len(ema) == len(sample_data)
    assert not ema.isna().all()
    assert ema.iloc[-1] > 0


def test_calculate_vwap(sample_data):
    vwap = calculate_vwap(sample_data)
    
    assert len(vwap) == len(sample_data)
    assert vwap.iloc[-1] > 0


def test_calculate_atr(sample_data):
    atr = calculate_atr(sample_data, 14)
    
    assert len(atr) == len(sample_data)
    assert atr.iloc[-1] > 0


def test_strategy_initialization():
    strategy = EMAVWAPStrategy(
        ema_fast=9,
        ema_slow=21,
        atr_period=14,
        atr_sl_multiplier=2.0,
        atr_tp_multiplier=3.0
    )
    
    assert strategy.ema_fast == 9
    assert strategy.ema_slow == 21
    assert strategy.atr_period == 14


def test_generate_signals(sample_data):
    strategy = EMAVWAPStrategy()
    df_with_signals = strategy.generate_signals(sample_data)
    
    assert 'EMA_Fast' in df_with_signals.columns
    assert 'EMA_Slow' in df_with_signals.columns
    assert 'VWAP' in df_with_signals.columns
    assert 'ATR' in df_with_signals.columns
    assert 'Long_Signal' in df_with_signals.columns
    assert 'Short_Signal' in df_with_signals.columns


def test_calculate_stops():
    strategy = EMAVWAPStrategy(
        atr_sl_multiplier=2.0,
        atr_tp_multiplier=3.0
    )
    
    # Test LONG
    sl, tp = strategy.calculate_stops(1.09000, 0.00050, 'long')
    assert sl == 1.08900  # 1.09 - (2 * 0.0005)
    assert tp == 1.09150  # 1.09 + (3 * 0.0005)
    
    # Test SHORT
    sl, tp = strategy.calculate_stops(1.09000, 0.00050, 'short')
    assert sl == 1.09100  # 1.09 + (2 * 0.0005)
    assert tp == 1.08850  # 1.09 - (3 * 0.0005)


def test_get_current_signal(sample_data):
    strategy = EMAVWAPStrategy()
    signal = strategy.get_current_signal(sample_data)
    
    # Il segnale può essere None o un dict con le chiavi corrette
    if signal is not None:
        assert 'direction' in signal
        assert 'entry_price' in signal
        assert 'sl' in signal
        assert 'tp' in signal
        assert 'atr' in signal
        assert signal['direction'] in ['long', 'short']