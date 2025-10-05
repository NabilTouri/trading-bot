import pytest
from src.risk.manager import RiskManager


def test_risk_manager_initialization():
    rm = RiskManager(risk_percent=1.0, initial_capital=10000.0)
    
    assert rm.capital == 10000.0
    assert rm.risk_percent == 0.01
    assert rm.current_positions == 0
    assert rm.max_positions == 3


def test_calculate_position_size():
    rm = RiskManager(risk_percent=1.0, initial_capital=10000.0)
    
    # Test per EURUSD
    entry = 1.09000
    sl = 1.08900
    size = rm.calculate_position_size(entry, sl, "EURUSD")
    
    assert size > 0
    assert size <= 10.0
    assert size >= 0.01


def test_calculate_position_size_jpy():
    rm = RiskManager(risk_percent=1.0, initial_capital=10000.0)
    
    # Test per coppie JPY (pip value diverso)
    entry = 150.00
    sl = 149.50
    size = rm.calculate_position_size(entry, sl, "USDJPY")
    
    assert size > 0
    assert size <= 10.0


def test_can_open_position():
    rm = RiskManager(risk_percent=1.0, initial_capital=10000.0)
    
    assert rm.can_open_position() is True
    
    # Simula apertura massima posizioni
    rm.current_positions = 3
    assert rm.can_open_position() is False


def test_max_drawdown_limit():
    rm = RiskManager(risk_percent=1.0, initial_capital=10000.0)
    
    # Simula perdita del 60% (oltre il limite del 50%)
    rm.capital = 4000.0
    assert rm.can_open_position() is False


def test_update_capital():
    rm = RiskManager(risk_percent=1.0, initial_capital=10000.0)
    
    rm.update_capital(12000.0)
    assert rm.capital == 12000.0
    assert rm.max_capital == 12000.0
    
    rm.update_capital(11000.0)
    assert rm.capital == 11000.0
    assert rm.max_capital == 12000.0  # Max non diminuisce


def test_open_close_position():
    rm = RiskManager(risk_percent=1.0, initial_capital=10000.0)
    
    rm.open_position()
    assert rm.current_positions == 1
    
    rm.close_position(profit=100.0)
    assert rm.current_positions == 0
    assert rm.capital == 10100.0