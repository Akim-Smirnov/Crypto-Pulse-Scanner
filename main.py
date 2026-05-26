import ccxt
from rich.console import Console
from rich.table import Table

console = Console()

EXCHANGES = {
    "Binance": ccxt.binance,
    "OKX": ccxt.okx,
    "Bybit": ccxt.bybit,
}

SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
]


def create_exchange(exchange_class):
    return exchange_class({
        "enableRateLimit": True
    })


def fetch_ticker(exchange_name, exchange, symbol):
    try:
        ticker = exchange.fetch_ticker(symbol)

        return {
            "exchange": exchange_name,
            "symbol": symbol,
            "last": ticker.get("last"),
            "bid": ticker.get("bid"),
            "ask": ticker.get("ask"),
            "percentage": ticker.get("percentage"),
            "quote_volume": ticker.get("quoteVolume"),
        }

    except Exception as error:
        return {
            "exchange": exchange_name,
            "symbol": symbol,
            "error": str(error),
        }


def format_number(value, decimal=2):
    if value is None:
        return "-"

    return f"{value:,.{decimal}f}"


def format_percent(value):
    if value is None:
        return "-"

    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}%"


def calculate_spread_percent(bid, ask):
    if not bid or not ask:
        return None

    mid_price = (bid + ask) / 2
    spread = ask - bid

    return (spread / mid_price) * 100


def main():
    table = Table(title="Crypto Pulse Scanner v0.1")

    table.add_column("Биржа")
    table.add_column("Пара")
    table.add_column("Цена", justify="right")
    table.add_column("Bid", justify="right")
    table.add_column("Ask", justify="right")
    table.add_column("Изм. 24h", justify="right")
    table.add_column("Объем 24h", justify="right")
    table.add_column("Спред", justify="right")

    for exchange_name, exchange_class in EXCHANGES.items():
        exchange = create_exchange(exchange_class)

        for symbol in SYMBOLS:
            data = fetch_ticker(exchange_name, exchange, symbol)

            if "error" in data:
                table.add_row(
                    exchange_name,
                    symbol,
                    "ERROR",
                    "-",
                    "-",
                    "-",
                    "-",
                    data["error"][:30],
                )
                continue

            spread = calculate_spread_percent(
                data["bid"],
                data["ask"],
            )

            table.add_row(
                data["exchange"],
                data["symbol"],
                format_number(data["last"]),
                format_number(data["bid"]),
                format_number(data["ask"]),
                format_percent(data["percentage"]),
                format_number(data["quote_volume"], 0),
                format_percent(spread),
            )

    console.print(table)


if __name__ == "__main__":
    main()