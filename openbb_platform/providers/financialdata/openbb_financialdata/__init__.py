"""FinancialData provider module."""

from openbb_financialdata.models.equity_search import FinancialDataEquitySearchFetcher
from openbb_financialdata.models.equity_historical import FinancialDataEquityHistoricalFetcher
from openbb_financialdata.models.income_statement import FinancialDataIncomeStatementFetcher
from openbb_financialdata.models.balance_sheet import FinancialDataBalanceSheetFetcher
from openbb_financialdata.models.cash_flow import FinancialDataCashFlowFetcher
from openbb_core.provider.abstract.provider import Provider

financialdata_provider = Provider(
    name="financialdata",
    website="https://financialdata.net",
    description="""FinancialData.Net provides real-time and historical financial data
covering US and international markets, including symbols, historical prices, and financial statements.""",
    credentials=["api_key"],
    fetcher_dict={
        "EquitySearch": FinancialDataEquitySearchFetcher,
        "EquityHistorical": FinancialDataEquityHistoricalFetcher,
        "IncomeStatement": FinancialDataIncomeStatementFetcher,
        "BalanceSheet": FinancialDataBalanceSheetFetcher,
        "CashFlow": FinancialDataCashFlowFetcher,
    },
    repr_name="FinancialData",
)
