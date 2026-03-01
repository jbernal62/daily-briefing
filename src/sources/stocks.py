"""Yahoo Finance — stock watchlist data via yfinance."""

import yfinance as yf


def fetch_stocks(tickers: list[str]) -> list[dict]:
    """Fetch current price and daily change for each ticker."""
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
            items.append({
                "category": "stocks",
                "title": f"{symbol} {arrow}{change_pct:.1f}% (${price:.2f})",
                "description": f"Previous close: ${prev_close:.2f}, Change: {arrow}${change:.2f}",
                "source": "Yahoo Finance",
                "url": f"https://finance.yahoo.com/quote/{symbol}",
                "published": "",
            })
        except Exception:
            continue
    return items
