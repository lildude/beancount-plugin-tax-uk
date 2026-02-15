"""Test for commission accumulation fix"""

import datetime
import re
from decimal import Decimal
from pathlib import Path
from unittest import mock

from beancount import loader
from beancount.core import data, amount
from beancount.core.data import Transaction, Posting

from beancount_plugin_tax_uk.calculate_tax import (
    TaxConfig,
    generate_tax_related_events,
)
from beancount_plugin_tax_uk.models import AssetType, TaxRelatedEventType
from beancount_plugin_tax_uk.rate_converter import BeancountRateConverter
from beancount_plugin_tax_uk.tax_report import generate_tax_report


def test_commission_accumulation():
    """Test that commission values are accumulated when multiple postings match the regex."""
    # Create a mock transaction with multiple commission postings
    meta = data.new_metadata("<test>", 0)

    from beancount.core import position

    postings = [
        Posting(
            "Assets:Stocks",
            amount.Amount(Decimal("10"), "AAPL"),
            position.Cost(
                number=Decimal("150"),
                currency="GBP",
                date=None,
                label=None,
            ),
            None,
            None,
            None,
        ),
        Posting(
            "Assets:Cash",
            amount.Amount(
                Decimal("-1503"), "GBP"
            ),  # 10 * 150 + 2 + 1 (total commission)
            None,
            None,
            None,
            None,
        ),
        Posting(
            "Expenses:Broker:Commissions",  # First commission posting
            amount.Amount(Decimal("2"), "GBP"),
            None,
            None,
            None,
            None,
        ),
        Posting(
            "Expenses:Trading:Commissions",  # Second commission posting
            amount.Amount(Decimal("1"), "GBP"),
            None,
            None,
            None,
            None,
        ),
    ]

    transaction = Transaction(
        meta,
        datetime.date(2023, 1, 1),
        "*",
        None,
        "Buy AAPL with multiple commission postings",
        {"buy"},  # This tag will match the buy event type
        data.EMPTY_SET,
        postings,
    )

    entries = [transaction]
    options = {"operating_currency": ["GBP"]}

    # Mock the load_tax_config function to return a custom configuration
    with mock.patch(
        "beancount_plugin_tax_uk.calculate_tax.load_tax_config"
    ) as mock_config:
        mock_config.return_value = TaxConfig(
            platform_mapping=[
                (re.compile(r"Assets:Stocks"), "TestBroker", AssetType.STOCKS)
            ],
            asset_mapping={},
            tag_mapping={},
            commission_account_regex=re.compile(r"Expenses:.*:Commissions"),
            income_account_regex=re.compile(r"Income:.*"),
            ignored_account_regex=re.compile(r"Equity:.*"),
            ignored_currencies=["GBP"],
        )

        # Generate tax related events
        events = generate_tax_related_events(entries, options, verbose=False)

    # Should have one event for the buy transaction
    assert len(events) == 1
    event = events[0]

    # Verify the event properties
    assert event.event_type == TaxRelatedEventType.BUY
    assert event.asset == "AAPL"
    assert event.quantity == Decimal("10")

    # The key test: fee_value should be the sum of both commission postings
    assert event.fee_value == Decimal("3")  # 2 + 1 = 3


def test_single_commission_unchanged():
    """Test that single commission posting still works correctly."""
    # Create a mock transaction with single commission posting
    meta = data.new_metadata("<test>", 0)

    from beancount.core import position

    postings = [
        Posting(
            "Assets:Stocks",
            amount.Amount(Decimal("10"), "AAPL"),
            position.Cost(
                number=Decimal("150"),
                currency="GBP",
                date=None,
                label=None,
            ),
            None,
            None,
            None,
        ),
        Posting(
            "Assets:Cash",
            amount.Amount(Decimal("-1502"), "GBP"),  # 10 * 150 + 2
            None,
            None,
            None,
            None,
        ),
        Posting(
            "Expenses:Broker:Commissions",
            amount.Amount(Decimal("2"), "GBP"),
            None,
            None,
            None,
            None,
        ),
    ]

    transaction = Transaction(
        meta,
        datetime.date(2023, 1, 1),
        "*",
        None,
        "Buy AAPL with single commission posting",
        {"buy"},
        data.EMPTY_SET,
        postings,
    )

    entries = [transaction]
    options = {"operating_currency": ["GBP"]}

    # Mock the load_tax_config function to return a custom configuration
    with mock.patch(
        "beancount_plugin_tax_uk.calculate_tax.load_tax_config"
    ) as mock_config:
        mock_config.return_value = TaxConfig(
            platform_mapping=[
                (re.compile(r"Assets:Stocks"), "TestBroker", AssetType.STOCKS)
            ],
            asset_mapping={},
            tag_mapping={},
            commission_account_regex=re.compile(r"Expenses:.*:Commissions"),
            income_account_regex=re.compile(r"Income:.*"),
            ignored_account_regex=re.compile(r"Equity:.*"),
            ignored_currencies=["GBP"],
        )

        # Generate tax related events
        events = generate_tax_related_events(entries, options, verbose=False)

    # Should have one event
    assert len(events) == 1
    event = events[0]

    # Verify the event properties
    assert event.event_type == TaxRelatedEventType.BUY
    assert event.fee_value == Decimal("2")  # Single commission value


def test_linked_transaction_fees_gathered():
    """Test that expenses from linked transactions (via ^ links) are added to fee_value."""
    data_dir = Path("tests") / "data"
    ledger_path = (
        data_dir / "cgtcalc_inputs_beancount" / "MultiTransactionFees.beancount"
    )

    entries, errors, options = loader.load_file(str(ledger_path))
    assert not errors, f"Beancount loading errors: {errors}"

    events = generate_tax_related_events(entries, options, verbose=False)

    # Should have 2 events: a buy and a sell
    assert len(events) == 2

    sell_event = [e for e in events if e.event_type == TaxRelatedEventType.SELL][0]

    # The sell transaction has direct commissions (4.95 + 0.18 = 5.13 USD) plus
    # linked fees (81.38 USD + 0.65 GBP) all accumulated into fee_value.
    # Total: 5.13 + 81.38 + 0.65 = 87.16
    assert sell_event.fee_value == Decimal("87.16")


def test_linked_fees_included_in_chargeable_gain():
    """Test that linked fees are included in the chargeable gain calculation for sell events."""
    data_dir = Path("tests") / "data"
    ledger_path = (
        data_dir / "cgtcalc_inputs_beancount" / "MultiTransactionFees.beancount"
    )

    entries, errors, options = loader.load_file(str(ledger_path))
    assert not errors, f"Beancount loading errors: {errors}"

    events = generate_tax_related_events(entries, options, verbose=False)

    rate_converter = BeancountRateConverter(entries)
    rows, tax_res, _ = generate_tax_report(
        entries,
        events,
        rate_converter=rate_converter,
    )

    # Filter to sell events
    sell_events = tax_res[tax_res["event_type"] == "Sell"]
    assert len(sell_events) == 1

    sell_row = sell_events.iloc[0]

    # All fees (direct commissions + linked fees) are accumulated into fee_value.
    # Total fee_value: 4.95 + 0.18 + 81.38 + 0.65 = 87.16 (in sell currency USD)
    # The chargeable gain should be reduced by the total fees.
    chargeable_gain = Decimal(str(sell_row["chargeable_gain"]))

    # Sell: 105 USD * 130 = 13650 USD
    # Buy: 101.57 USD * 130 = 13204.10 USD
    sell_rate = rate_converter.get_rate(int(events[1].timestamp) / 1000, "USD")
    sell_gbp = Decimal("13650") / sell_rate
    buy_rate = rate_converter.get_rate(int(events[0].timestamp) / 1000, "USD")
    buy_gbp = Decimal("13204.10") / buy_rate
    total_fee_gbp = Decimal("87.16") / sell_rate

    expected_gain = sell_gbp - buy_gbp - total_fee_gbp

    # Allow small floating point tolerance
    assert abs(chargeable_gain - expected_gain) < Decimal("0.01"), (
        f"Chargeable gain {chargeable_gain} does not match expected {expected_gain}"
    )

    # Confirm the fees actually made a difference (they should reduce gain by ~66 GBP)
    assert total_fee_gbp > Decimal("50"), (
        f"Total fees in GBP should be significant, got {total_fee_gbp}"
    )
