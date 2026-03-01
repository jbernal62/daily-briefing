"""Yahoo Finance — ETF performance data."""

import yfinance as yf


def fetch_etfs(tickers: list[str], names: dict) -> list[dict]:
    """Fetch ETF price and performance data."""
    items = []
    for symbol in tickers:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            price = info.last_price
            prev_close = info.previous_close
            change = price - prev_close
            change_pct = (change / prev_close) * 100 if prev_close else 0
            arrow = "+" if change >= 0 else ""

            # Get longer-term performance
            hist = ticker.history(period="1mo")
            month_ago_price = hist["Close"].iloc[0] if len(hist) > 0 else price
            month_change = ((price - month_ago_price) / month_ago_price) * 100

            display_name = names.get(symbol, symbol)
            items.append({
                "category": "etf",
                "title": f"{display_name} ({symbol}) {arrow}{change_pct:.2f}%",
                "description": (
                    f"Price: EUR {price:.2f} | Day: {arrow}{change:.2f} | "
                    f"1M: {'+' if month_change >= 0 else ''}{month_change:.1f}%"
                ),
                "source": "Yahoo Finance",
                "url": f"https://finance.yahoo.com/quote/{symbol}",
                "published": "",
            })
        except Exception:
            continue
    return items
