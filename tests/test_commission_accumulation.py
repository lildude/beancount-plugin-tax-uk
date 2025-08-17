"""Test for commission accumulation fix"""

import datetime
import re
from decimal import Decimal

from beancount.core import data, amount
from beancount.core.data import Transaction, Posting

from src.beancount_plugin_tax_uk.calculate_tax import TaxConfig, generate_tax_related_events
from src.beancount_plugin_tax_uk.models import AssetType, TaxRelatedEventType


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
            amount.Amount(Decimal("-1503"), "GBP"), # 10 * 150 + 2 + 1 (total commission)
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
    
    # Create configuration with commission account regex that matches both postings
    config = TaxConfig(
        platform_mapping=[(re.compile(r"Assets:Stocks"), "TestBroker", AssetType.STOCKS)],
        asset_mapping={},
        tag_mapping={},
        commission_account_regex=re.compile(r"Expenses:.*:Commissions"),
        income_account_regex=re.compile(r"Income:.*"),
        ignored_account_regex=re.compile(r"Equity:.*"),
        ignored_currencies=["GBP"],
    )
    
    # Create entries list with just this transaction
    entries = [transaction]
    options = {"operating_currency": ["GBP"]}
    
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
            amount.Amount(Decimal("-1502"), "GBP"), # 10 * 150 + 2
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
    
    # Create configuration
    config = TaxConfig(
        platform_mapping=[(re.compile(r"Assets:Stocks"), "TestBroker", AssetType.STOCKS)],
        asset_mapping={},
        tag_mapping={},
        commission_account_regex=re.compile(r"Expenses:.*:Commissions"),
        income_account_regex=re.compile(r"Income:.*"),
        ignored_account_regex=re.compile(r"Equity:.*"),
        ignored_currencies=["GBP"],
    )
    
    # Create entries list
    entries = [transaction]
    options = {"operating_currency": ["GBP"]}
    
    # Generate tax related events
    events = generate_tax_related_events(entries, options, verbose=False)
    
    # Should have one event
    assert len(events) == 1
    event = events[0]
    
    # Verify the event properties
    assert event.event_type == TaxRelatedEventType.BUY
    assert event.fee_value == Decimal("2")  # Single commission value