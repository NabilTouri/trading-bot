# Crea file test_twelvedata.py
from twelvedata import TDClient
from config.settings import settings

td = TDClient(apikey=settings.twelvedata_api_key)

try:
    ts = td.time_series(
        symbol="EUR/USD",
        interval="5min",
        outputsize=10
    )
    
    df = ts.as_pandas()
    print("✓ TwelveData funziona!")
    print(df.head())
    
except Exception as e:
    print(f"✗ Errore: {e}")