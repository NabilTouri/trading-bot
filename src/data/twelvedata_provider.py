from twelvedata import TDClient
import pandas as pd
from datetime import datetime
from loguru import logger
from typing import Optional


class TwelveDataProvider:
    def __init__(self, api_key: str):
        self.client = TDClient(apikey=api_key)
        logger.info("TwelveData provider initialized")
    
    def get_historical_data(
        self, 
        symbol: str, 
        interval: str, 
        start: str, 
        end: str
    ) -> Optional[pd.DataFrame]:
        try:
            # Converti simbolo forex per TwelveData (EUR/USD)
            td_symbol = f"{symbol[:3]}/{symbol[3:]}"
            
            ts = self.client.time_series(
                symbol=td_symbol,
                interval=interval,
                start_date=start,
                end_date=end,
                outputsize=5000
            )
            
            df = ts.as_pandas()
            
            if df is None or df.empty:
                logger.warning(f"No data retrieved for {symbol}")
                return None
            
            df.index = pd.to_datetime(df.index)
            df.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            }, inplace=True)
            
            logger.info(f"Retrieved {len(df)} bars for {symbol} from TwelveData")
            return df[['Open', 'High', 'Low', 'Close', 'Volume']]
            
        except Exception as e:
            logger.error(f"Error fetching data from TwelveData: {e}")
            return None