"""CoinGecko API — Bitcoin price and market data (free, no key)."""

import httpx


async def fetch_crypto(symbols: list[str]) -> list[dict]:
    """Fetch crypto prices and 24h change from CoinGecko."""
    items = []
    # Map common symbols to CoinGecko IDs
    id_map = {"BTC-USD": "bitcoin", "ETH-USD": "ethereum", "SOL-USD": "solana"}

    coin_ids = [id_map.get(s, s.lower().replace("-usd", "")) for s in symbols]

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(
                "https://api.coingecko.com/api/v3/coins/markets",
                params={
                    "vs_currency": "usd",
                    "ids": ",".join(coin_ids),
                    "price_change_percentage": "24h,7d",
                },
            )
            resp.raise_for_status()
            for coin in resp.json():
                price = coin.get("current_price", 0)
                change_24h = coin.get("price_change_percentage_24h", 0)
                change_7d = coin.get("price_change_percentage_7d_in_currency", 0)
                high_24h = coin.get("high_24h", 0)
                low_24h = coin.get("low_24h", 0)
                arrow = "+" if change_24h >= 0 else ""
                items.append({
                    "category": "crypto",
                    "title": f"Bitcoin ${price:,.0f} ({arrow}{change_24h:.1f}% 24h)",
                    "description": (
                        f"24h range: ${low_24h:,.0f}-${high_24h:,.0f} | "
                        f"7d: {'+' if change_7d >= 0 else ''}{change_7d:.1f}% | "
                        f"Market cap: ${coin.get('market_cap', 0)/1e9:.0f}B"
                    ),
                    "source": "CoinGecko",
                    "url": f"https://www.coingecko.com/en/coins/{coin.get('id', 'bitcoin')}",
                    "published": "",
                })
        except httpx.HTTPError:
            pass
    return items
