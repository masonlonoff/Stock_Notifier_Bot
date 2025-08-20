from Scraper import main as get_symbols
from fetch import get_price_data
from sectors import add_sector_column
from logger import log_alerts
from market import get_market_overview
from emailer import generate_html_email, send_email
from config import EMAIL_ADDRESS, EMAIL_PASSWORD, TO_ADDRESS
from pathlib import Path


LOG_DIR = Path(r"C:\Users\Nancy Lonoff\OneDrive\Desktop\Misc\Stock Notifier\log_files")

if __name__ == "__main__":
    tickers = get_symbols()["Symbol"].tolist()
    tickers = [t.strip().upper().replace('.', '-') for t in tickers if isinstance(t, str) and t.strip().upper() != "SYMBOL"]

    info = get_price_data(tickers)
    alerts = info[
        info["below_3m_low"] |
        info["below_6m_low"] |
        info["below_52w_low"] |
        info["below_5%_prev_close"] |
        info["below_5%_open_to_close"] |
        info["down_streak"]
    ]

    alerts = add_sector_column(alerts)
    log_alerts(info)

    email_body = generate_html_email(
        alerts,
        drop_threshold=-5,
        streak_min=5,
        log_dir=LOG_DIR,
        days_back=7,
        market_overview=get_market_overview(), 
    )

    send_email(
        subject="📊 Daily Stock Alert Summary",
        body=email_body,
        sender=EMAIL_ADDRESS,
        recipient=TO_ADDRESS,
        password=EMAIL_PASSWORD,
        html=True
    )

