import datetime
import json
from decimal import Decimal
from abc import ABC, abstractmethod
from typing import List
from beancount.core import prices


class RateConverter(ABC):
    """Interface for currency rate conversion."""

    @abstractmethod
    def get_rate(self, ts: int, currency: str) -> Decimal:
        """Get exchange rate for a given timestamp and currency.

        Args:
            ts: Unix timestamp
            currency: Currency code (e.g. 'USD', 'EUR')

        Returns:
            Exchange rate as Decimal
        """
        pass


class BeancountRateConverter(RateConverter):
    """Rate converter using Beancount's price database."""

    def __init__(self, entries: List, base_currency: str = "GBP"):
        """Initialize with Beancount entries.

        Args:
            entries: List of Beancount entries containing price directives
            base_currency: Base currency for conversions (default: GBP)
        """
        self.base_currency = base_currency
        self.price_map = prices.build_price_map(entries)

    def get_rate(self, ts: int, currency: str) -> Decimal:
        """Get exchange rate from Beancount's price database.

        Uses the most recent price before the given timestamp.
        Falls back to direct conversion if available, otherwise tries reverse rate.

        Args:
            ts: Unix timestamp
            currency: Currency code to convert from

        Returns:
            Exchange rate as Decimal (1 currency = X base_currency)
        """
        if currency == self.base_currency:
            return Decimal(1)

        dt = datetime.datetime.fromtimestamp(ts)

        # Try direct conversion
        price_tuple = prices.get_price(
            self.price_map, (self.base_currency, currency), dt.date()
        )
        if price_tuple[1] is not None:
            return Decimal(price_tuple[1])

        # Try reverse conversion
        price_tuple = prices.get_price(
            self.price_map, (currency, self.base_currency), dt.date()
        )
        if price_tuple[1] is not None:
            return Decimal(1) / Decimal(price_tuple[1])

        raise ValueError(
            f"No conversion rate found for {currency} to {self.base_currency} at {dt}"
        )


class HMRCRateConverter(RateConverter):
    """Rate converter using HMRC exchange rates."""

    def __init__(self, rates_path: str = "hmrc-exchange-rates"):
        """Initialize HMRC rate converter.

        Args:
            rates_path: Path to the directory containing HMRC exchange rates (default: hmrc-exchange-rates)
        """
        self._cached_rates = {}
        self._rates_path = rates_path

    def get_rate(self, ts: int, currency: str) -> Decimal:
        assert ts, "timestamp should be provided"
        assert currency, "currency should be provided"
        if currency == "GBP":
            return Decimal(1)
        if currency == "GBX":
            return Decimal(100)
        dt = datetime.datetime.fromtimestamp(ts)
        folder = dt.strftime("%Y/%m")
        key = folder + "_" + currency
        if key not in self._cached_rates:
            with open(f"{self._rates_path}/rate/{folder}.json", "r") as f:
                self._cached_rates[key] = Decimal(
                    json.loads(f.read())["rates"][currency]
                )
        return self._cached_rates[key]
