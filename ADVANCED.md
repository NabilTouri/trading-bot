# Forex Intraday Trading Bot - Documentazione Avanzata

## Architettura del Sistema

### 1. Data Layer
- **MT5Provider**: Connessione diretta a MetaTrader5 per dati real-time e storici
- **TwelveDataProvider**: API REST per dati alternativi e backup

### 2. Strategy Layer
- **EMAVWAPStrategy**: Implementazione della strategia di trading
  - EMA(9/21) crossover per trend
  - VWAP per conferma del momentum
  - ATR per posizionamento dinamico di SL/TP

### 3. Risk Management Layer
- Sizing basato su rischio percentuale fisso
- Limitazione numero posizioni simultanee
- Protezione da drawdown eccessivo

### 4. Execution Layer
- **PaperTrader**: Simulazione completa senza rischio
- **MT5Executor**: Esecuzione su conto reale/demo

### 5. Backtest Layer
- Framework backtrader per analisi storica
- Metriche complete (Sharpe, Drawdown, Win Rate)

## Strategia di Trading Dettagliata

### Logica di Entrata

#### Long Entry
```
Condizioni:
1. EMA(9) > EMA(21)              # Trend rialzista
2. Prezzo > VWAP                 # Momentum positivo
3. Nessuna posizione aperta      # Evita over-trading
4. Risk management OK            # Verifica capitale
```

#### Short Entry
```
Condizioni:
1. EMA(9) < EMA(21)              # Trend ribassista
2. Prezzo < VWAP                 # Momentum negativo
3. Nessuna posizione aperta
4. Risk management OK
```

### Gestione della Posizione

#### Stop Loss
```python
SL_Long = Entry_Price - (2.0 × ATR)
SL_Short = Entry_Price + (2.0 × ATR)
```

#### Take Profit
```python
TP_Long = Entry_Price + (3.0 × ATR)
TP_Short = Entry_Price - (3.0 × ATR)
```

#### Position Sizing
```python
Risk_Amount = Capital × (Risk_Percent / 100)
SL_Distance_Pips = |Entry_Price - SL_Price| / Pip_Value
Position_Size = Risk_Amount / (SL_Distance_Pips × Value_Per_Pip)
```

## Configurazione Avanzata

### Parametri Ottimizzabili

```python
# Strategy Parameters
EMA_FAST = 9          # Periodo EMA veloce (range: 5-15)
EMA_SLOW = 21         # Periodo EMA lenta (range: 15-50)
ATR_PERIOD = 14       # Periodo ATR (range: 10-20)
ATR_SL_MULT = 2.0     # Moltiplicatore SL (range: 1.5-3.0)
ATR_TP_MULT = 3.0     # Moltiplicatore TP (range: 2.0-4.0)

# Risk Parameters
RISK_PERCENT = 1.0    # % capitale per trade (range: 0.5-2.0)
MAX_POSITIONS = 3     # Posizioni simultanee (range: 1-5)
MAX_DRAWDOWN = 0.5    # Drawdown massimo 50%

# Timeframes
TIMEFRAME = 5         # 5 minuti (supporta: 1, 5, 15, 30, 60)
```

### Ottimizzazione dei Parametri

```bash
# Esegui backtest con parametri diversi
python src/main.py --mode backtest \\
    --start 2024-01-01 --end 2024-12-31 \\
    --ema-fast 12 --ema-slow 26 \\
    --atr-sl 2.5 --atr-tp 3.5
```

## Deployment

### 1. Setup Locale

```bash
# Installa dipendenze
poetry install

# Configura .env
cp .env.example .env
nano .env

# Esegui tests
poetry run pytest

# Avvia paper trading
poetry run python src/main.py --mode paper
```

### 2. Docker Deployment

```bash
# Build immagine
docker-compose build

# Avvia in background
docker-compose up -d

# Monitora logs
docker-compose logs -f

# Stop
docker-compose down
```

### 3. Cloud Deployment (AWS/GCP)

```bash
# Push immagine a registry
docker tag forex-trading-bot:latest gcr.io/project/forex-bot
docker push gcr.io/project/forex-bot

# Deploy su Cloud Run / ECS
gcloud run deploy forex-bot --image gcr.io/project/forex-bot
```

## Monitoring e Logging

### Log Levels
- **DEBUG**: Dettagli tecnici completi
- **INFO**: Eventi operativi normali
- **WARNING**: Situazioni anomale non critiche
- **ERROR**: Errori che richiedono attenzione

### Metriche da Monitorare
1. Win Rate (>50% ideale)
2. Profit Factor (>1.5 ideale)
3. Sharpe Ratio (>1.0 ideale)
4. Max Drawdown (<20% ideale)
5. Average Trade Duration

## Troubleshooting

### Problema: MT5 Non Si Connette
```bash
# Verifica credenziali
echo $MT5_LOGIN $MT5_SERVER

# Test connessione manuale
python -c "import MetaTrader5 as mt5; print(mt5.initialize())"
```

### Problema: Nessun Dato Recuperato
```bash
# Verifica simboli disponibili
python -c "import MetaTrader5 as mt5; mt5.initialize(); print(mt5.symbols_get())"

# Verifica timeframe
# Assicurati che il timeframe sia supportato dal broker
```

### Problema: Backtest Lento
```python
# Riduci periodo di test
--start 2024-06-01 --end 2024-12-31

# Aumenta timeframe
TIMEFRAME=15  # Invece di 5 minuti
```

## Best Practices

### 1. Testing
- Sempre testare su dati storici prima del paper trading
- Paper trading per almeno 1 mese prima del live
- Usare account demo per primi test live

### 2. Risk Management
- Mai rischiare più del 1-2% per trade
- Limitare posizioni simultanee
- Impostare stop loss sempre

### 3. Monitoring
- Controllare log giornalmente
- Analizzare performance settimanalmente
- Aggiustare parametri solo dopo analisi approfondita

### 4. Manutenzione
- Aggiornare dipendenze regolarmente
- Backup configurazioni e log
- Testare dopo ogni modifica

## Performance Attese

### Condizioni di Mercato Ideali
- Mercati trending con volatilità moderata
- Sessioni europee e americane
- Evitare news ad alto impatto

### Metriche Realistiche
- Win Rate: 45-55%
- Sharpe Ratio: 0.8-1.5
- Max Drawdown: 15-25%
- Monthly Return: 3-8%

⚠️ **DISCLAIMER**: Past performance non garantisce risultati futuri. 
Trading comporta rischio di perdita capitale.

## Sviluppi Futuri

- [ ] Machine Learning per ottimizzazione parametri
- [ ] Telegram bot per notifiche
- [ ] Dashboard web real-time
- [ ] Multi-strategy ensemble
- [ ] Sentiment analysis integration
- [ ] Portfolio optimization

## Supporto

Per issues: github.com/yourrepo/forex-bot/issues
Per domande: your.email@example.com
"""

print("\\n" + "="*60)
print("PROGETTO COMPLETO GENERATO!")
print("="*60)
print("\\nFile generati:")
print("✓ pyproject.toml - Configurazione Poetry")
print("✓ README.md - Documentazione principale")
print("✓ .env.example - Template configurazione")
print("✓ config/settings.py - Settings management")
print("✓ src/data/mt5_provider.py - MetaTrader5 integration")
print("✓ src/data/twelvedata_provider.py - TwelveData API")
print("✓ src/strategy/indicators.py - Technical indicators")
print("✓ src/strategy/ema_vwap_strategy.py - Trading strategy")
print("✓ src/risk/manager.py - Risk management")
print("✓ src/execution/paper_trader.py - Paper trading")
print("✓ src/execution/mt5_executor.py - Live execution")
print("✓ src/backtest/backtester.py - Backtrader integration")
print("✓ src/main.py - Entry point")
print("✓ tests/test_strategy.py - Strategy tests")
print("✓ tests/test_risk_manager.py - Risk tests")
print("✓ tests/test_execution.py - Execution tests")
print("✓ Dockerfile - Container image")
print("✓ docker-compose.yml - Orchestration")
print("✓ Makefile - Task automation")
print("✓ .gitignore, .dockerignore, pytest.ini")
print("\\n" + "="*60)
"""# FOREX INTRADAY TRADING BOT
# Struttura completa del progetto

"""
forex-trading-bot/
├── pyproject.toml
├── README.md
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── config/
│   ├── __init__.py
│   └── settings.py
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── mt5_provider.py
│   │   └── twelvedata_provider.py
│   ├── strategy/
│   │   ├── __init__.py
│   │   ├── indicators.py
│   │   └── ema_vwap_strategy.py
│   ├── risk/
│   │   ├── __init__.py
│   │   └── manager.py
│   ├── execution/
│   │   ├── __init__.py
│   │   ├── paper_trader.py
│   │   └── mt5_executor.py
│   └── backtest/
│       ├── __init__.py
│       └── backtester.py
├── tests/
│   ├── __init__.py
│   ├── test_strategy.py
│   ├── test_risk_manager.py
│   └── test_execution.py
└── logs/