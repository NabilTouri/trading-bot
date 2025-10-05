import pytest
import pandas as pd
from src.execution.paper_trader import PaperTrader, Position


@pytest.fixture
def paper_trader():
    return PaperTrader(initial_capital=10000.0)


def test_paper_trader_initialization(paper_trader):
    assert paper_trader.capital == 10000.0
    assert paper_trader.initial_capital == 10000.0
    assert len(paper_trader.positions) == 0
    assert len(paper_trader.closed_positions) == 0


def test_open_position(paper_trader):
    result = paper_trader.open_position(
        symbol="EURUSD",
        direction="long",
        entry_price=1.09000,
        size=0.1,
        sl=1.08900,
        tp=1.09150
    )
    
    assert result is True
    assert len(paper_trader.positions) == 1
    assert paper_trader.positions[0].symbol == "EURUSD"
    assert paper_trader.positions[0].direction == "long"


def test_position_stop_loss():
    position = Position(
        symbol="EURUSD",
        direction="long",
        entry_price=1.09000,
        size=0.1,
        sl=1.08900,
        tp=1.09150
    )
    
    # Simula hit dello stop loss
    bar = pd.Series({
        'Close': 1.08850,
        'High': 1.09000,
        'Low': 1.08800
    })
    
    hit = position.check_exit(bar['Close'], bar['High'], bar['Low'])
    
    assert hit is True
    assert position.status == 'stop_loss'
    assert position.profit < 0


def test_position_take_profit():
    position = Position(
        symbol="EURUSD",
        direction="long",
        entry_price=1.09000,
        size=0.1,
        sl=1.08900,
        tp=1.09150
    )
    
    # Simula hit del take profit
    bar = pd.Series({
        'Close': 1.09150,
        'High': 1.09200,
        'Low': 1.09000
    })
    
    hit = position.check_exit(bar['Close'], bar['High'], bar['Low'])
    
    assert hit is True
    assert position.status == 'take_profit'
    assert position.profit > 0


def test_paper_trader_update(paper_trader):
    paper_trader.open_position(
        symbol="EURUSD",
        direction="long",
        entry_price=1.09000,
        size=0.1,
        sl=1.08900,
        tp=1.09150
    )
    
    # Simula barra che triggera TP
    bar = pd.Series({
        'Close': 1.09150,
        'High': 1.09200,
        'Low': 1.09000
    })
    
    initial_positions = len(paper_trader.positions)
    paper_trader.update("EURUSD", bar)
    
    assert len(paper_trader.positions) == initial_positions - 1
    assert len(paper_trader.closed_positions) == 1
    assert paper_trader.capital > 10000.0


def test_get_statistics(paper_trader):
    # Aggiungi alcune posizioni chiuse simulate
    for i in range(5):
        paper_trader.open_position(
            symbol="EURUSD",
            direction="long",
            entry_price=1.09000,
            size=0.1,
            sl=1.08900,
            tp=1.09150
        )
        
        bar = pd.Series({
            'Close': 1.09150 if i % 2 == 0 else 1.08900,
            'High': 1.09200,
            'Low': 1.08800
        })
        
        paper_trader.update("EURUSD", bar)
    
    stats = paper_trader.get_statistics()
    
    assert 'total_trades' in stats
    assert 'win_rate' in stats
    assert 'total_return' in stats
    assert stats['total_trades'] == 5