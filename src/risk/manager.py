from loguru import logger
from typing import Optional


class RiskManager:
    def __init__(self, risk_percent: float = 1.0, initial_capital: float = 10000.0):
        self.risk_percent = risk_percent / 100.0
        self.capital = initial_capital
        self.max_capital = initial_capital
        self.current_positions = 0
        self.max_positions = 3
        logger.info(f"RiskManager initialized: {risk_percent}% risk, capital: {initial_capital}")
    
    def calculate_position_size(
        self, 
        entry_price: float, 
        sl_price: float, 
        symbol: str = "EURUSD"
    ) -> float:
        # Calcola il rischio per pip
        risk_amount = self.capital * self.risk_percent
        
        # Calcola distanza SL in pips
        pip_value = 0.0001 if 'JPY' not in symbol else 0.01
        sl_distance_pips = abs(entry_price - sl_price) / pip_value
        
        if sl_distance_pips == 0:
            return 0.0
        
        # Valore per pip per lotto standard (100,000 unità)
        value_per_pip = pip_value * 100000
        
        # Calcola il numero di lotti
        lots = risk_amount / (sl_distance_pips * value_per_pip)
        
        # Arrotonda a 0.01 lotti (micro lotti)
        lots = round(lots, 2)
        
        # Limita tra 0.01 e 10 lotti
        lots = max(0.01, min(lots, 10.0))
        
        logger.info(f"Position size calculated: {lots} lots (Risk: ${risk_amount:.2f})")
        return lots
    
    def can_open_position(self) -> bool:
        if self.current_positions >= self.max_positions:
            logger.warning(f"Max positions reached: {self.current_positions}/{self.max_positions}")
            return False
        
        # Verifica drawdown massimo (50%)
        if self.capital < self.max_capital * 0.5:
            logger.error(f"Max drawdown reached. Capital: {self.capital}")
            return False
        
        return True
    
    def update_capital(self, new_capital: float):
        self.capital = new_capital
        self.max_capital = max(self.max_capital, new_capital)
        logger.info(f"Capital updated: {self.capital:.2f}")
    
    def open_position(self):
        if self.can_open_position():
            self.current_positions += 1
            logger.info(f"Position opened. Total: {self.current_positions}")
    
    def close_position(self, profit: float):
        self.current_positions = max(0, self.current_positions - 1)
        self.update_capital(self.capital + profit)
        logger.info(f"Position closed. Profit: {profit:.2f}, Total positions: {self.current_positions}")