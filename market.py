import yfinance as yf

def get_market_overview():
    """
    Retrieves the 1-day percent change in SPY and QQQ from Yahoo Finance.

    Returns:
        dict: {
            "SPY": float or None,
            "QQQ": float or None
        }

        If data is unavailable or fails, returns None for each index.
    """
    try:
        spy = yf.Ticker("SPY").history(period = "2d")["Close"]
        qqq = yf.Ticker("QQQ").history(period = "2d")["Close"]


        if len(spy) < 2 or len(qqq) < 2:
            return {"SPY": None, "QQQ": None}

        spy_change = ((spy.iloc[-1] / spy.iloc[-2]) - 1) * 100
        qqq_change = ((qqq.iloc[-1] / qqq.iloc[-2]) - 1) * 100

        return {
            "SPY": round(spy_change, 2), 
            "QQQ": round(qqq_change, 2)
        }
    except Exception as e:
        print(f"Failed to fetch market overview: {e}")
        return {"SPY": None, "QQQ": None}

