# Crea file test_mt5.py
import MetaTrader5 as mt5
from config.settings import settings

if mt5.initialize():
    print("✓ MT5 inizializzato")

    if mt5.login(settings.mt5_login, settings.mt5_password, settings.mt5_server):
        print("✓ Login riuscito!")
        
        account = mt5.account_info()
        print(f"Balance: ${account.balance}")
        print(f"Equity: ${account.equity}")
        
        # Verifica simboli disponibili
        symbols = mt5.symbols_get()
        print(f"Simboli disponibili: {len(symbols)}")
        
        # Cerca EURUSD
        eurusd = mt5.symbol_info("EURUSD")
        if eurusd:
            print(f"✓ EURUSD trovato: {eurusd.bid}")
        
        mt5.shutdown()
    else:
        print(f"✗ Login fallito: {mt5.last_error()}")
else:
    print("✗ Inizializzazione fallita")