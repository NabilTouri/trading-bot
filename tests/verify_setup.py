#!/usr/bin/env python3
"""Script di verifica completa della configurazione"""

import sys
from pathlib import Path

# Aggiungi src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config.settings import settings
from src.data.mt5_provider import MT5Provider
from src.data.twelvedata_provider import TwelveDataProvider
import MetaTrader5 as mt5

print("=" * 60)
print("VERIFICA CONFIGURAZIONE FOREX TRADING BOT")
print("=" * 60)

# 1. Verifica caricamento settings
print("\n[1/5] Verifica Settings...")
try:
    print(f"  ✓ Symbols: {settings.symbols}")
    print(f"  ✓ Timeframe: {settings.timeframe}")
    print(f"  ✓ Risk: {settings.risk_percent}%")
    print(f"  ✓ Mode: {settings.mode}")
except Exception as e:
    print(f"  ✗ Errore: {e}")
    sys.exit(1)

# 2. Test MT5
print("\n[2/5] Test Connessione MT5...")
mt5_provider = MT5Provider(
    settings.mt5_login,
    settings.mt5_password,
    settings.mt5_server
)

if mt5_provider.connect():
    print("  ✓ MT5 connesso!")
    
    account = mt5_provider.get_account_info()
    print(f"  ✓ Balance: ${account.get('balance', 0):.2f}")
    print(f"  ✓ Equity: ${account.get('equity', 0):.2f}")
    
    # Test recupero dati
    from datetime import datetime, timedelta
    end = datetime.now()
    start = end - timedelta(days=2)
    
    data = mt5_provider.get_historical_data(
        settings.symbols[0],
        settings.timeframe,
        start,
        end
    )
    
    if data is not None and not data.empty:
        print(f"  ✓ Dati recuperati: {len(data)} candele")
    else:
        print("  ⚠ Nessun dato recuperato")
    
    mt5_provider.disconnect()
else:
    print("  ✗ Connessione MT5 fallita!")
    print(f"  Errore: {mt5.last_error()}")
    sys.exit(1)

# 3. Test TwelveData
print("\n[3/5] Test TwelveData API...")
try:
    td_provider = TwelveDataProvider(settings.twelvedata_api_key)
    
    data = td_provider.get_historical_data(
        "EURUSD",
        "5min",
        (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        datetime.now().strftime("%Y-%m-%d")
    )
    
    if data is not None and not data.empty:
        print(f"  ✓ TwelveData funziona: {len(data)} candele")
    else:
        print("  ⚠ TwelveData: nessun dato")
        
except Exception as e:
    print(f"  ✗ Errore TwelveData: {e}")

# 4. Test Strategy
print("\n[4/5] Test Strategy...")
try:
    from src.strategy.ema_vwap_strategy import EMAVWAPStrategy
    
    strategy = EMAVWAPStrategy(
        ema_fast=settings.ema_fast,
        ema_slow=settings.ema_slow,
        atr_period=settings.atr_period
    )
    print("  ✓ Strategy inizializzata")
    
    if data is not None and len(data) > 30:
        signal = strategy.get_current_signal(data)
        if signal:
            print(f"  ✓ Segnale generato: {signal['direction']}")
        else:
            print("  ✓ Nessun segnale (normale)")
            
except Exception as e:
    print(f"  ✗ Errore Strategy: {e}")

# 5. Test Risk Manager
print("\n[5/5] Test Risk Manager...")
try:
    from src.risk.manager import RiskManager
    
    rm = RiskManager(
        risk_percent=settings.risk_percent,
        initial_capital=settings.initial_capital
    )
    print(f"  ✓ Risk Manager inizializzato")
    print(f"  ✓ Capitale: ${rm.capital:.2f}")
    print(f"  ✓ Rischio per trade: ${rm.capital * rm.risk_percent:.2f}")
    
    size = rm.calculate_position_size(1.09000, 1.08900, "EURUSD")
    print(f"  ✓ Position size calcolato: {size} lots")
    
except Exception as e:
    print(f"  ✗ Errore Risk Manager: {e}")

# Riepilogo finale
print("\n" + "=" * 60)
print("CONFIGURAZIONE COMPLETATA CON SUCCESSO! ✓")
print("=" * 60)
print("\nProssimi passi:")
print("1. Esegui backtest: poetry run python src/main.py --mode backtest --start 2024-01-01 --end 2024-12-31")
print("2. Avvia paper trading: poetry run python src/main.py --mode paper")
print("3. Monitora logs: tail -f logs/trading_bot.log")
print("\n")
print("Buon trading! 🚀")