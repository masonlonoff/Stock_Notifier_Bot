# Stock_Notifier_Bot

![image](https://helloyubo.com/wp-content/uploads/2021/07/How-To-Integrate-The-Chatbot-With-Email-Marketing.jpg)

A personal project that scans large/mega-cap stocks for major price movements (3M, 6M, 52W lows, large daily drops, and multi-day loss streaks). It then generates and sends a summary email.

## Motivation


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
- [Scraper.py](https://github.com/masonlonoff/Stock_Notifier_Bot/blob/main/Scraper.py): Scrape tickers
- [fetch.py](https://github.com/masonlonoff/Stock_Notifier_Bot/blob/main/fetch.py): download OHLC data & compute alerts
- [sectors.py](https://github.com/masonlonoff/Stock_Notifier_Bot/blob/main/sectors.py): add sector info
- [market.py](https://github.com/masonlonoff/Stock_Notifier_Bot/blob/main/market.py): SPY/QQQ context
- [emailer.py](https://github.com/masonlonoff/Stock_Notifier_Bot/blob/main/emailer.py): build/send HTML summary
- [logger.py](https://github.com/masonlonoff/Stock_Notifier_Bot/blob/main/logger.py): log daily triggers
- [trigger_log.csv](https://github.com/masonlonoff/Stock_Notifier_Bot/blob/main/trigger_log_2025-08-20.csv): example of what one of the logged files looks like
- [Daily Stock Alert Summary Email.pdf](https://github.com/masonlonoff/Stock_Notifier_Bot/blob/main/Daily%20Stock%20Alert%20Summary%20Email.pdf): sample email sent out on 8/20/25


## How it works
1) Scrapes tickers -> DataFrame
2) Fetch OHLC data for the past year -> compute alerts
3) Assigns each ticker a sector
4) Log triggered alerts to a csv (log_files/)
5) Render HTML email summary and send it 
