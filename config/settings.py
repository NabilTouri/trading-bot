from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # MT5 Configuration
    mt5_login: int
    mt5_password: str
    mt5_server: str
    
    # TwelveData Configuration
    twelvedata_api_key: str
    
    # Trading Configuration
    symbols: List[str] = ["EURUSD", "GBPUSD", "USDJPY"]
    timeframe: int = 5  # minuti
    risk_percent: float = 1.0
    initial_capital: float = 10000.0
    
    # Strategy Parameters
    ema_fast: int = 9
    ema_slow: int = 21
    atr_period: int = 14
    atr_sl_multiplier: float = 2.0
    atr_tp_multiplier: float = 3.0
    
    # Execution
    mode: str = "paper"  # backtest, paper, live
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()