import pandas as pd
from datetime import datetime
from pathlib import Path



def log_alerts(df, log_dir = None):
    """
    Logs triggered alerts from the stock DataFrame to a dated CSV file.

    Parameters:
        df (pd.DataFrame): DataFrame containing stock alert flags and symbol column.
        log_dir (str): Directory where logs should be saved. Default is 'log_files'.

    Output:
        Writes a CSV log of triggered alert types to log_files/trigger_log_<YYYY-MM-DD>.csv
    """
    today_str = datetime.today().strftime("%Y-%m-%d")
    LOG_DIR = Path(r"C:\Users\Nancy Lonoff\OneDrive\Desktop\Misc\Stock Notifier\log_files")
    LOG_DIR.mkdir(parents=True, exist_ok=True)  # create if missing
    
    log_file = LOG_DIR / f"trigger_log_{today_str}.csv"

    log_rows = []
    for _,row in df.iterrows():
        symbol = row["symbol"]

        if row.get("below_3m_low"): log_rows.append((symbol, today_str, "below_3m_low"))
        if row.get("below_6m_low"): log_rows.append((symbol, today_str, "below_6m_low"))
        if row.get("below_52w_low"): log_rows.append((symbol, today_str, "below_52w_low"))
        if row.get("down_streak", 0) >= 5: log_rows.append((symbol, today_str, "down_streak_5plus"))
        if row.get("pct_drop_from_prev_close", 0) <= -5: log_rows.append((symbol, today_str, "pct_drop_5plus"))


    pd.DataFrame(log_rows, columns = ["symbol", "date", "alert_type"]).to_csv(log_file, index = False)
