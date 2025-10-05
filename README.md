# Forex Intraday Trading Bot

Bot di trading automatico per Forex con strategia EMA/VWAP, risk management e supporto MT5.

## Caratteristiche

- **Strategia**: EMA(9/21) crossover + VWAP + ATR per SL/TP
- **Risk Management**: 1% capitale per trade
- **Data Providers**: MetaTrader5 e TwelveData
- **Backtest**: Framework backtrader integrato
- **Execution**: Paper trading e live trading MT5
- **Containerizzato**: Docker ready

## Installazione

### Con Poetry
```bash
poetry install
poetry shell
```

### Con Docker
```bash
docker-compose up -d
```

## Configurazione

Copia `.env.example` in `.env` e configura:
```bash
cp .env.example .env
```

Parametri principali:
- `MT5_LOGIN`, `MT5_PASSWORD`, `MT5_SERVER`: Credenziali MT5
- `TWELVEDATA_API_KEY`: API key TwelveData
- `RISK_PERCENT`: % capitale per trade (default: 1.0)
- `SYMBOLS`: Coppie forex da tradare

## Utilizzo

### Backtest
```bash
python src/main.py --mode backtest --start 2024-01-01 --end 2024-12-31
```

### Paper Trading
```bash
python src/main.py --mode paper
```

### Live Trading
```bash
python src/main.py --mode live
```

## Testing
```bash
pytest tests/ -v --cov=src
```

## Strategia

### Segnali di Entrata
- **LONG**: EMA(9) > EMA(21) + Prezzo > VWAP
- **SHORT**: EMA(9) < EMA(21) + Prezzo < VWAP

### Gestione Posizione
- **Stop Loss**: Prezzo entrata ± (2 × ATR)
- **Take Profit**: Prezzo entrata ± (3 × ATR)
- **Position Sizing**: Basato su 1% del capitale

## Struttura

```
src/
├── data/           # Provider dati (MT5, TwelveData)
├── strategy/       # Logica strategia e indicatori
├── risk/          # Risk management
├── execution/     # Paper trading e MT5 executor
└── backtest/      # Backtesting engine
```

## Logs

I log sono salvati in `logs/trading_bot.log` con rotazione automatica.

## Sicurezza

- Mai committare file `.env`
- Usa account demo per testing
- Verifica sempre i risultati del backtest prima del live

## License

MIT