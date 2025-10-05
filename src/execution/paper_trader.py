import pandas as pd
from datetime import datetime
from loguru import logger
from typing import Optional, List, Dict


class Position:
    def __init__(
        self, 
        symbol: str, 
        direction: str, 
        entry_price: float, 
        size: float, 
        sl: float, 
        tp: float
    ):
        self.symbol = symbol
        self.direction = direction
        self.entry_price = entry_price
        self.size = size
        self.sl = sl
        self.tp = tp
        self.entry_time = datetime.now()
        self.exit_price = None
        self.exit_time = None
        self.profit = 0.0
        self.status = 'open'
    
    def check_exit(self, current_price: float, high: float, low: float) -> bool:
        if self.direction == 'long':
            if low <= self.sl:
                self.close(self.sl, 'stop_loss')
                return True
            if high >= self.tp:
                self.close(self.tp, 'take_profit')
                return True
        else:  # short
            if high >= self.sl:
                self.close(self.sl, 'stop_loss')
                return True
            if low <= self.tp:
                self.close(self.tp, 'take_profit')
                return True
        return False
    
    def close(self, exit_price: float, reason: str):
        self.exit_price = exit_price
        self.exit_time = datetime.now()
        self.status = reason
        
        if self.direction == 'long':
            self.profit = (exit_price - self.entry_price) * self.size * 100000
        else:
            self.profit = (self.entry_price - exit_price) * self.size * 100000
        
        logger.info(f"Position closed: {reason} | Profit: ${self.profit:.2f}")


class PaperTrader:
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions: List[Position] = []
        self.closed_positions: List[Position] = []
        self.trades_log: List[Dict] = []
    
    def open_position(
        self, 
        symbol: str, 
        direction: str, 
        entry_price: float, 
        size: float, 
        sl: float, 
        tp: float
    ) -> bool:
        position = Position(symbol, direction, entry_price, size, sl, tp)
        self.positions.append(position)
        
        logger.info(
            f"Paper trade opened: {direction.upper()} {size} lots {symbol} "
            f"@ {entry_price} | SL: {sl} | TP: {tp}"
        )
        return True
    
    def update(self, symbol: str, current_bar: pd.Series):
        for position in self.positions[:]:
            if position.symbol == symbol:
                if position.check_exit(
                    current_bar['Close'], 
                    current_bar['High'], 
                    current_bar['Low']
                ):
                    self.capital += position.profit
                    self.positions.remove(position)
                    self.closed_positions.append(position)
                    
                    self.trades_log.append({
                        'symbol': position.symbol,
                        'direction': position.direction,
                        'entry_time': position.entry_time,
                        'exit_time': position.exit_time,
                        'entry_price': position.entry_price,
                        'exit_price': position.exit_price,
                        'size': position.size,
                        'profit': position.profit,
                        'status': position.status
                    })
    
    def get_open_positions(self, symbol: str = None) -> List[Position]:
        if symbol:
            return [p for p in self.positions if p.symbol == symbol]
        return self.positions
    
    def get_statistics(self) -> Dict:
        if not self.closed_positions:
            return {}
        
        profits = [p.profit for p in self.closed_positions]
        winning_trades = [p for p in self.closed_positions if p.profit > 0]
        losing_trades = [p for p in self.closed_positions if p.profit <= 0]
        
        return {
            'initial_capital': self.initial_capital,
            'final_capital': self.capital,
            'total_return': ((self.capital - self.initial_capital) / self.initial_capital) * 100,
            'total_trades': len(self.closed_positions),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': (len(winning_trades) / len(self.closed_positions)) * 100 if self.closed_positions else 0,
            'average_profit': sum(profits) / len(profits) if profits else 0,
            'max_profit': max(profits) if profits else 0,
            'max_loss': min(profits) if profits else 0
        }