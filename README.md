# Stock_Notifier_Bot

![image]()

A personal project that scans large/mega-cap stocks for major price movements (3M, 6M, 52W lows, large daily drops, and multi-day loss streaks). It then generates and sends a summary email.

## Features
- **Scraping**: Collects large/mega-cap tickers with Selenium + BeautifulSoup.
- **Data Fetching**: Uses Yahoo Finance ('yfinance') to retrieve daily OHLC (open, high, low, close) data.
- **Alerts**:
  - New 3M/6M/52W lows
  - ≥5% drop from previous close
  - Multi-day down streaks (default = 5 days)
  - ≥50% drop from 52W high
- **Context**:
  - Sector tagging via 'yfinance' metadata
  - SPY/QQQ market overview
  - Weekly repeat 5% droppers
  - Total alerts by sector and alert type
- **Email Output**: Sends structured HTML with tables, sectors and badges

## Project Structure
- [Scraper.py](https://github.com/masonlonoff/Stock_Notifier_Bot/blob/main/Scraper.pyhttps://github.com/masonlonoff/Stock_Notifier_Bot/blob/main/Scraper.py) 
