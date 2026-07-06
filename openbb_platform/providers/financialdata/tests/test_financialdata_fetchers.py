"""Unit tests for FinancialData provider fetchers."""

import pytest
from unittest.mock import patch
from datetime import date
from openbb_financialdata.models.equity_search import FinancialDataEquitySearchFetcher
from openbb_financialdata.models.equity_historical import FinancialDataEquityHistoricalFetcher
from openbb_financialdata.models.income_statement import FinancialDataIncomeStatementFetcher
from openbb_financialdata.models.balance_sheet import FinancialDataBalanceSheetFetcher
from openbb_financialdata.models.cash_flow import FinancialDataCashFlowFetcher

test_credentials = {"api_key": "MOCK_API_KEY"}

@patch("openbb_core.provider.utils.helpers.make_request")
def test_financialdata_equity_search_fetcher(mock_make_request):
    """Test FinancialData Equity Search Fetcher."""
    mock_make_request.return_value = [
        {"trading_symbol": "SHEL.L", "registrant_name": "Shell plc"},
        {"trading_symbol": "BP.L", "registrant_name": "BP plc"}
    ]
    fetcher = FinancialDataEquitySearchFetcher()
    
    params = {"query": "Shell"}
    query = fetcher.transform_query(params)
    assert query.query == "Shell"
    
    data = fetcher.extract_data(query, test_credentials)
    results = fetcher.transform_data(query, data)
    assert len(results) == 1
    assert results[0].symbol == "SHEL.L"
    assert results[0].name == "Shell plc"


@patch("openbb_core.provider.utils.helpers.make_request")
def test_financialdata_equity_historical_fetcher(mock_make_request):
    """Test FinancialData Equity Historical Price Fetcher."""
    mock_make_request.return_value = [
        {"trading_symbol": "SHEL.L", "date": "2025-05-01", "open": 2400.0, "high": 2450.0, "low": 2380.0, "close": 2410.0, "volume": 100000.0},
        {"trading_symbol": "SHEL.L", "date": "2025-05-02", "open": 2410.0, "high": 2460.0, "low": 2390.0, "close": 2420.0, "volume": 120000.0}
    ]
    fetcher = FinancialDataEquityHistoricalFetcher()
    params = {"symbol": "SHEL.L", "start_date": date(2025, 5, 1), "end_date": date(2025, 5, 2)}
    query = fetcher.transform_query(params)
    data = fetcher.extract_data(query, test_credentials)
    results = fetcher.transform_data(query, data)
    assert len(results) == 2
    assert results[0].date == date(2025, 5, 1)
    assert results[0].close == 2410.0
    assert results[1].date == date(2025, 5, 2)
    assert results[1].close == 2420.0


@patch("openbb_core.provider.utils.helpers.make_request")
def test_financialdata_income_statement_fetcher(mock_make_request):
    """Test FinancialData Income Statement Fetcher."""
    mock_make_request.return_value = [
        {
            "trading_symbol": "SHEL.L",
            "registrant_name": "Shell plc",
            "fiscal_period": "FY",
            "period_end_date": "2024-12-31",
            "currency_code": "USD",
            "revenue": 284312000000.0,
            "cost_of_revenue": 238371000000.0,
            "gross_profit": 45941000000.0,
            "operating_income": 29992000000.0,
            "net_income": 16094000000.0
        }
    ]
    fetcher = FinancialDataIncomeStatementFetcher()
    params = {"symbol": "SHEL.L", "limit": 1}
    query = fetcher.transform_query(params)
    data = fetcher.extract_data(query, test_credentials)
    results = fetcher.transform_data(query, data)
    assert len(results) == 1
    assert results[0].period_ending == date(2024, 12, 31)
    assert results[0].fiscal_year == 2024
    assert results[0].revenue == 284312000000.0
    assert results[0].net_income == 16094000000.0


@patch("openbb_core.provider.utils.helpers.make_request")
def test_financialdata_balance_sheet_fetcher(mock_make_request):
    """Test FinancialData Balance Sheet Fetcher."""
    mock_make_request.return_value = [
        {
            "trading_symbol": "SHEL.L",
            "registrant_name": "Shell plc",
            "fiscal_period": "FY",
            "period_end_date": "2024-12-31",
            "currency_code": "USD",
            "total_assets": 387609000000.0,
            "total_liabilities": 207441000000.0
        }
    ]
    fetcher = FinancialDataBalanceSheetFetcher()
    params = {"symbol": "SHEL.L", "limit": 1}
    query = fetcher.transform_query(params)
    data = fetcher.extract_data(query, test_credentials)
    results = fetcher.transform_data(query, data)
    assert len(results) == 1
    assert results[0].period_ending == date(2024, 12, 31)
    assert results[0].total_assets == 387609000000.0


@patch("openbb_core.provider.utils.helpers.make_request")
def test_financialdata_cash_flow_fetcher(mock_make_request):
    """Test FinancialData Cash Flow Fetcher."""
    mock_make_request.return_value = [
        {
            "trading_symbol": "SHEL.L",
            "registrant_name": "Shell plc",
            "fiscal_period": "FY",
            "period_end_date": "2024-12-31",
            "currency_code": "USD",
            "cash_from_operating_activities": 54687000000.0,
            "cash_at_end_of_period": 39110000000.0
        }
    ]
    fetcher = FinancialDataCashFlowFetcher()
    params = {"symbol": "SHEL.L", "limit": 1}
    query = fetcher.transform_query(params)
    data = fetcher.extract_data(query, test_credentials)
    results = fetcher.transform_data(query, data)
    assert len(results) == 1
    assert results[0].period_ending == date(2024, 12, 31)
    assert results[0].net_cash_from_operating_activities == 54687000000.0
