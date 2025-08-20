# fetch.py
import yfinance as yf
import pandas as pd

def get_price_data(tickers, period="1y", interval="1d") -> pd.DataFrame:
    """
    Fetch historical price data and compute alert metrics for each ticker.
    """
    info = []
    EPS = 1e-9 

    for ticker in tickers:
        try:
            symbol = yf.Ticker(ticker)
            hist = symbol.history(period=period, interval=interval).dropna().sort_index()

            if hist.empty or len(hist) < 2:
                print(f"{ticker}: no data")
                continue

            last_date = hist.index[-1]
            today_row = hist.iloc[-1]
            latest_price = float(today_row["Close"])

            # Prior windows (exclude today)
            prior = hist.iloc[:-1]
            w3  = prior[prior.index >= last_date - pd.Timedelta(days=90)]
            w6  = prior[prior.index >= last_date - pd.Timedelta(days=180)]
            w52 = prior[prior.index >= last_date - pd.Timedelta(days=365)]

            # Prior lows/highs (None-safe)
            prev_3m_low  = float(w3["Low"].min())  if not w3.empty  else None
            prev_6m_low  = float(w6["Low"].min())  if not w6.empty  else None
            prev_52w_low = float(w52["Low"].min()) if not w52.empty else None

            # 52w high can include today (for % drop display)
            high_52w = float(hist["High"].max())
            prev_3m_high = float(w3["High"].max()) if not w3.empty else None
            prev_6m_high = float(w6["High"].max()) if not w6.empty else None

            # Day-over-day and intraday moves
            yesterday_close = float(hist["Close"].iloc[-2])
            pct_drop_from_prev_close  = (latest_price / yesterday_close - 1) * 100
            pct_drop_from_open_to_close = (latest_price / float(today_row["Open"]) - 1) * 100

            # Down-streak
            tmp = hist.copy()
            tmp["down"] = tmp["Close"] < tmp["Close"].shift(1)
            tmp["streak"] = tmp["down"].astype(int).groupby((~tmp["down"]).cumsum()).cumsum()
            latest_streak = int(tmp["streak"].iloc[-1]) if tmp["down"].iloc[-1] else 0

            info.append({
                "symbol": ticker,
                "latest_price": latest_price,
                "3m_high": prev_3m_high,
                "3m_low":  prev_3m_low,
                "6m_high": prev_6m_high,
                "6m_low":  prev_6m_low,
                "52w_high": high_52w,
                "52w_low":  prev_52w_low,
                "pct_drop_from_prev_close": pct_drop_from_prev_close,
                "pct_drop_from_open_to_close": pct_drop_from_open_to_close,
                "below_3m_low":  (prev_3m_low  is not None) and (latest_price <= prev_3m_low  + EPS),
                "below_6m_low":  (prev_6m_low  is not None) and (latest_price <= prev_6m_low  + EPS),
                "below_52w_low": (prev_52w_low is not None) and (latest_price <= prev_52w_low + EPS),
                "below_5%_prev_close": pct_drop_from_prev_close <= -5,
                "below_5%_open_to_close": pct_drop_from_open_to_close <= -5,
                "down_streak": latest_streak if latest_streak >= 5 else None,
                "drop_from_52w_high": (100.0 * (latest_price - high_52w) / high_52w) if high_52w > 0 else None
            })

        except Exception as e:
            print(f"{ticker} error: {e}")
        
    
    return pd.DataFrame(info)

