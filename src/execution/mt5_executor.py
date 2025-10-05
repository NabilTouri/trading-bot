from src.data.mt5_provider import MT5Provider
from loguru import logger
from typing import Optional, List, Dict


class MT5Executor:
    def __init__(self, mt5_provider: MT5Provider):
        self.provider = mt5_provider
        self.active_orders: Dict[str, int] = {}
    
    def execute_trade(
        self, 
        symbol: str, 
        direction: str, 
        size: float, 
        sl: float, 
        tp: float
    ) -> Optional[int]:
        if not self.provider.connected:
            logger.error("MT5 not connected")
            return None
        
        # Verifica se c'è già una posizione aperta
        if symbol in self.active_orders:
            logger.warning(f"Position already open for {symbol}")
            return None
        
        order_type = 'buy' if direction == 'long' else 'sell'
        order_id = self.provider.place_order(
            symbol=symbol,
            order_type=order_type,
            volume=size,
            sl=sl,
            tp=tp,
            comment="EMA_VWAP_Bot"
        )
        
        if order_id:
            self.active_orders[symbol] = order_id
            logger.info(f"Trade executed on MT5: {order_type} {size} {symbol}")
        
        return order_id
    
    def close_position(self, symbol: str) -> bool:
        if symbol not in self.active_orders:
            logger.warning(f"No active position for {symbol}")
            return False
        
        # In MT5, le posizioni con SL/TP si chiudono automaticamente
        # Questo metodo è per chiusure manuali se necessario
        del self.active_orders[symbol]
        logger.info(f"Position closed for {symbol}")
        return True
    
    def get_active_positions(self) -> List[str]:
        return list(self.active_orders.keys())