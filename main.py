from typing import Any, Optional, TypeAlias

import ccxt
from rich.console import Console
from rich.table import Table

console = Console()

ExchangeClass: TypeAlias = type
TickerData: TypeAlias = dict[str, Any]

EXCHANGES: dict[str, ExchangeClass] = {
    "Binance": ccxt.binance,
    "OKX": ccxt.okx,
    "Bybit": ccxt.bybit,
}

SYMBOLS: list[str] = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
]


def create_exchange(exchange_class: ExchangeClass) -> Any:
    """
    Создает объект биржи CCXT с включенным rate limit.

    Args:
        exchange_class: Класс биржи из CCXT, например ccxt.binance.

    Returns:
        Готовый объект биржи для работы с API.
    """
    return exchange_class({
        "enableRateLimit": True
    })


def fetch_ticker(
    exchange_name: str,
    exchange: Any,
    symbol: str,
) -> TickerData:
    """
    Получает тикер торговой пары с конкретной биржи.

    Args:
        exchange_name: Название биржи, например "Binance".
        exchange: Объект биржи CCXT.
        symbol: Торговая пара, например "BTC/USDT".

    Returns:
        Словарь с данными тикера или словарь с ошибкой.
    """
    try:
        ticker: dict[str, Any] = exchange.fetch_ticker(symbol)

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


def format_number(value: Optional[float], decimal: int = 2) -> str:
    """
    Форматирует число для красивого вывода в таблице.

    Args:
        value: Число, которое нужно отформатировать.
        decimal: Количество знаков после точки.

    Returns:
        Отформатированная строка или "-", если значения нет.
    """
    if value is None:
        return "-"

    return f"{value:,.{decimal}f}"


def format_percent(value: Optional[float]) -> str:
    """
    Форматирует число как процент.

    Args:
        value: Число процента.

    Returns:
        Строка с процентом, например "+1.25%".
    """
    if value is None:
        return "-"

    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}%"


def calculate_spread_percent(
    bid: Optional[float],
    ask: Optional[float],
) -> Optional[float]:
    """
    Считает spread между bid и ask в процентах.

    Args:
        bid: Лучшая цена покупки.
        ask: Лучшая цена продажи.

    Returns:
        Spread в процентах или None, если расчет невозможен.
    """
    if bid is None or ask is None:
        return None

    mid_price = (bid + ask) / 2
    spread = ask - bid

    return (spread / mid_price) * 100


def main() -> None:
    """
    Главная функция программы.

    Создает таблицу, получает данные с бирж,
    считает spread и выводит результат в терминал.
    """
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
                    str(data["error"])[:30],
                )
                continue

            spread = calculate_spread_percent(
                data["bid"],
                data["ask"],
            )

            table.add_row(
                str(data["exchange"]),
                str(data["symbol"]),
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