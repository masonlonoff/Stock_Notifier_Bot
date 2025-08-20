import yfinance as yf
import time

def add_sector_column(alert_df):
    """
    Adds a 'sector' column to the alert DataFrame using yfinance metadata.

    Parameters:
        alert_df (pd.DataFrame): DataFrame with a 'symbol' column.

    Returns:
        pd.DataFrame: A copy of the original DataFrame with an additional 'sector' column.
                      If sector data is unavailable, fills with 'Unknown'.
    """
    sectors = []

    for _, row in alert_df.iterrows():
        symbol = row["symbol"]

        try:
            info = yf.Ticker(symbol).info
            sectors.append(info.get("sector", "Unknown"))
            time.sleep(0.25)

        except:
            sectors.append("Unknown")
    if len(sectors) != len(alert_df):
        raise ValueError(f"Sector list length ({len(sectors)}) doesn't match alerts length ({len(alert_df)})")

    alert_df = alert_df.copy()
    alert_df["sector"] = sectors
    return alert_df
    