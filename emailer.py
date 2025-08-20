from datetime import datetime
from pandas.tseries.offsets import BDay
import os
import glob
import pandas as pd
from collections import defaultdict
import smtplib
from email.mime.text import MIMEText


def generate_html_email(info_df, drop_threshold=-5, streak_min=5, log_dir='.', days_back=7, market_overview=None):
    """
    Generates a structured HTML email summarizing triggered stock alerts.

    The email groups alerts by type (e.g., below 3M low, down streak) and sector,
    includes a summary count, highlights sectors under pressure, and
    embeds market overview and recent repeat drop statistics.

    Parameters:
        info_df (pd.DataFrame): DataFrame containing alert flags, prices, and sectors for each stock.
                                Required columns include:
                                  - symbol
                                  - sector
                                  - below_3m_low, below_6m_low, below_52w_low
                                  - down_streak
                                  - pct_drop_from_prev_close
        drop_threshold (float): Percentage drop threshold for highlighting major declines (default: -5).
        streak_min (int): Minimum streak length (in days) to flag a down streak (default: 5).
        log_dir (str): Directory containing historical trigger log CSVs (default: current directory).
        days_back (int): Number of business days to look back for repeat alert detection (default: 7).
        market_overview (dict or None): Dictionary of market index % changes. Example:
            {
                "SPY": -1.23,
                "QQQ": 0.45
            }

    Returns:
        str: HTML-formatted string suitable for embedding in an email body.
             Includes:
               - summary stats
               - alert sections grouped by type and sector
               - sector pressure highlights
               - repeat 5% droppers this week
               - market index overview (SPY/QQQ)
               - run timestamp footer

    Raises:
        ValueError: If required columns are missing or malformed in `info_df`.
    """

    today = datetime.today()
    today_str = today.strftime('%Y-%m-%d')

    # Load recent logs to get repeat counts
    log_files = sorted(glob.glob(os.path.join(log_dir, "trigger_log_*.csv")))
    recent_logs = []

    if today.weekday() < 5:
        min_allowed_date = today - BDay(days_back - 1)
    else:
        min_allowed_date = today - BDay(days_back)

    for file in log_files:
        try:
            date_str = os.path.basename(file).split("_")[-1].replace(".csv", "")
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            if file_date.weekday() < 5 and min_allowed_date.date() <= file_date.date() <= today.date():
                df = pd.read_csv(file)
                recent_logs.append(df)
        except:
            continue

    if recent_logs:
        all_recent = pd.concat(recent_logs)
        repeat_counts = all_recent[all_recent["alert_type"] == "pct_drop_5plus"]["symbol"].value_counts().to_dict()
        recent_repeat_drops = pd.Series(repeat_counts).sort_values(ascending=False)
    else:
        repeat_counts = {}
        recent_repeat_drops = pd.Series(dtype=int)

    # Grouped structure: section → sector → list of alert tuples
    sections_by_sector = defaultdict(lambda: defaultdict(list))
    sector_totals = defaultdict(int)  # For pressure flag

    for _, row in info_df.iterrows():
        symbol = row["symbol"]
        sector = row.get("sector", "Unknown")
        link = f'<a href="https://finance.yahoo.com/quote/{symbol}" target="_blank" style="text-decoration:none;"><b>{symbol}</b></a>'

        drop_from_52w_high = row.get("drop_from_52w_high")
        # Count how many alert flags triggered
        trigger_count = sum([
            row.get("below_3m_low", False),
            row.get("below_6m_low", False),
            row.get("below_52w_low", False),
            row.get("pct_drop_from_prev_close", 0) <= drop_threshold,
            row.get("down_streak", 0) >= streak_min,
            row.get("drop_from_52w_high") is not None and row["drop_from_52w_high"] <= -50
            # row.get("below_200sma") is True
        ])

        
        badge = ""
        if trigger_count >= 2:
            badge = f"<span style='background-color:#eee; border-radius:6px; padding:2px 6px; font-size:12px; color:#555;'>{trigger_count} alerts</span>"

        if row.get("below_3m_low", False):
            tag = badge
            sections_by_sector["📉 Below 3M Low"][sector].append((link, tag))
            sector_totals[sector] += 1
        if row.get("below_6m_low", False):
            tag = badge
            sections_by_sector["💔 Below 6M Low"][sector].append((link, tag))
            sector_totals[sector] += 1
        if row.get("below_52w_low", False):
            tag = badge
            sections_by_sector["☢️ Below 52W Low"][sector].append((link, tag))
            sector_totals[sector] += 1
        if row.get("down_streak", 0) >= streak_min:
            days = int(row["down_streak"])
            tag = f"{days} days {badge}".strip()
            sections_by_sector[f"🔻 {streak_min}+ Day Down Streak"][sector].append((link, tag))
            sector_totals[sector] += 1
        if row.get("pct_drop_from_prev_close", 0) <= drop_threshold:
            pct = round(row["pct_drop_from_prev_close"], 2)
            pct_str = f"<span style='color:red'>({pct:+.2f}%)</span>"
            tag = f"{pct_str} {badge}".strip()
            sections_by_sector[f"⚠️ Drop ≥5% from Prev Close"][sector].append((link, tag))
            sector_totals[sector] += 1
        if drop_from_52w_high is not None and drop_from_52w_high <= -50:
            pct = round(drop_from_52w_high, 2)
            tag = f"<span style='color:#b33'>({pct:+.2f}%)</span> {badge}".strip()
            sections_by_sector["💀 Down ≥50% from 52W High"][sector].append((link, tag))
            sector_totals[sector] += 1
        # if row.get("below_200sma", False):
        #     tag = f"{badge}".strip()
        #     sections_by_sector["📉 Below 200-Day SMA"][sector].append((link, tag))
        #     sector_totals[sector] += 1
            


    # Summary block
    summary_lines = []
    total_alerts = 0
    for section, sector_dict in sections_by_sector.items():
        count = sum(len(stocks) for stocks in sector_dict.values())
        total_alerts += count
        summary_lines.append(f"<li><b>{section}</b>: {count} stocks</li>")

    summary_html = (
        f"<p><b>{total_alerts} total alerts</b> triggered today:</p>"
        f"<ul>{''.join(summary_lines)}</ul>"
    )

    html_lines = [f"<h2>📊 Stock Alert Summary — {today_str}</h2>"]

    # Market overview
    if market_overview and market_overview.get("SPY") is not None:
        spy = market_overview["SPY"]
        qqq = market_overview["QQQ"]
        spy_color = "red" if spy < 0 else "green"
        qqq_color = "red" if qqq < 0 else "green"

        html_lines.append("<h3>📉 Market Overview</h3><ul>")
        html_lines.append(f"<li>S&P 500 (SPY): <span style='color:{spy_color}'>{spy:+.2f}%</span></li>")
        html_lines.append(f"<li>Nasdaq 100 (QQQ): <span style='color:{qqq_color}'>{qqq:+.2f}%</span></li>")
        html_lines.append("</ul>")

    # Weekly repeaters (for 5% drop only)
    repeat_drops_filtered = recent_repeat_drops[recent_repeat_drops >= 2]
    if not repeat_drops_filtered.empty:
        html_lines.append("<h3>🔁 Repeat 5% Droppers This Week (2+ times)</h3><ul>")
        for symbol, count in repeat_drops_filtered.items():
            html_lines.append(f"<li>{symbol} ({count}x)</li>")
        html_lines.append("</ul>")

    # Sector pressure
    pressured_sectors = {s: c for s, c in sector_totals.items() if c >= 3}
    if pressured_sectors:
        html_lines.append("<h3>⚠️ Sectors Under Pressure (3+ alerts)</h3><ul>")
        for sector, count in sorted(pressured_sectors.items(), key=lambda x: -x[1]):
            html_lines.append(f"<li><b>{sector}</b>: {count} alerts</li>")
        html_lines.append("</ul>")

    html_lines.append(summary_html)

    # Section-by-sector breakdown (enforce custom order)
    section_order = [
        "📉 Below 3M Low",
        "💔 Below 6M Low",
        "☢️ Below 52W Low",
        f"🔻 {streak_min}+ Day Down Streak",
        "⚠️ Drop ≥5% from Prev Close",
        "💀 Down ≥50% from 52W High"
        # "📉 Below 200-Day SMA"
    ]

    for section in section_order:
        if section not in sections_by_sector:
            continue
        sector_dict = sections_by_sector[section]
        html_lines.append(f"<h3 style='margin-top:20px;'>{section}</h3>")
        for sector in sorted(sector_dict.keys()):
            html_lines.append(f"<h4 style='margin-bottom:5px;color:#555;'>{sector}</h4>")
            html_lines.append("""
            <table style="width:100%; border-collapse:collapse; font-size:14px; table-layout:fixed;">
            <tr>
                <th align="left" style="border-bottom:1px solid #ccc; padding:4px;">Symbol</th>
                <th align="left" style="border-bottom:1px solid #ccc; padding:4px;">Details</th>
            </tr>
            """)
            for symbol_link, details in sector_dict[sector]:
                html_lines.append(f"""
                <tr style="vertical-align: top;">
                    <td style="padding:6px 4px; white-space:nowrap; font-family:Arial, sans-serif; font-size:14px; overflow:hidden; text-overflow:ellipsis;">{symbol_link}</td>
                    <td style="padding:6px 4px; white-space:nowrap; font-family:Arial, sans-serif; font-size:14px; overflow:hidden; text-overflow:ellipsis;">{details}</td>
                </tr>
                """)
            html_lines.append("</table>")

    if total_alerts == 0:
        html_lines.append("<p>No alerts triggered today.</p>")

    run_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html_lines.append(f"<hr><p style='font-size:12px;color:#888;'>Generated by Stock Notifier Bot<br>Run at {run_time_str}</p>")

    return "\n".join(html_lines)


def send_email(subject, body, sender, recipient, password, html=False):
    """
    Sends an email via Gmail SMTP.

    Parameters:
        subject (str): Email subject line.
        body (str): Email message content (HTML or plain text).
        sender (str): Sender's email address.
        recipient (str): Recipient email address.
        password (str): App-specific password or Gmail login password.
        html (bool): If True, sends HTML; otherwise sends plain text.

    Side Effect:
        Sends an email and prints success/failure status.
    """
    msg = MIMEText(body, "html" if html else "plain", _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print("✅ Email sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

