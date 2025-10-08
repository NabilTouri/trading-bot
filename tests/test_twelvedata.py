# Crea file test_twelvedata.py
from twelvedata import TDClient
from config.settings import settings
from pathlib import Path
from loguru import logger

log_path = Path("logs")
log_path.mkdir(exist_ok=True)
logger.add(
    log_path / "twelvedata.log",
    rotation="1 day",
    retention="30 days",
)

td = TDClient(apikey=settings.twelvedata_api_key)

try:
    ts = td.time_series(
        symbol="EUR/USD",
        interval="5min",
        outputsize=10
    )
    
    df = ts.as_pandas()
    logger.success("✓ TwelveData funziona!")
    logger.info(df.head())

except Exception as e:
    logger.error(f"✗ Errore: {e}")