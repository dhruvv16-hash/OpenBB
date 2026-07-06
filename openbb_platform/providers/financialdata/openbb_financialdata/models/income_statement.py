"""FinancialData Income Statement Model."""

from typing import Any, Literal
from datetime import date as dateType, datetime
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from pydantic import Field, field_validator


class FinancialDataIncomeStatementQueryParams(IncomeStatementQueryParams):
    """FinancialData Income Statement Query."""

    period: Literal["annual", "quarter"] = Field(
        default="annual",
        description="The period of the statement (annual or quarter).",
    )


class FinancialDataIncomeStatementData(IncomeStatementData):
    """FinancialData Income Statement Data."""

    currency: str | None = Field(default=None, description="Currency of the report.")
    revenue: float | None = Field(default=None, description="Total revenue.")
    cost_of_revenue: float | None = Field(default=None, description="Cost of revenue.")
    gross_profit: float | None = Field(default=None, description="Gross profit.")
    research_and_development_expense: float | None = Field(default=None, description="Research and development expense.")
    general_and_admin_expense: float | None = Field(default=None, description="General and administrative expense.")
    total_operating_expenses: float | None = Field(default=None, description="Total operating expenses.")
    operating_income: float | None = Field(default=None, description="Operating income.")
    interest_expense: float | None = Field(default=None, description="Interest expense.")
    interest_income: float | None = Field(default=None, description="Interest income.")
    net_income: float | None = Field(default=None, description="Net income.")
    basic_earnings_per_share: float | None = Field(default=None, description="Basic earnings per share.")
    diluted_earnings_per_share: float | None = Field(default=None, description="Diluted earnings per share.")
    weighted_average_shares_outstanding: int | None = Field(default=None, description="Weighted average basic shares outstanding.")
    weighted_average_diluted_shares_outstanding: int | None = Field(default=None, description="Weighted average diluted shares outstanding.")


class FinancialDataIncomeStatementFetcher(
    Fetcher[FinancialDataIncomeStatementQueryParams, list[FinancialDataIncomeStatementData]]
):
    """FinancialData Income Statement Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FinancialDataIncomeStatementQueryParams:
        """Transform the query parameters."""
        return FinancialDataIncomeStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FinancialDataIncomeStatementQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Extract data from FinancialData API."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import make_request
        from openbb_core.provider.utils.errors import EmptyDataError

        api_key = credentials.get("api_key") if credentials else None
        if not api_key:
            api_key = kwargs.get("api_key")

        url = "https://financialdata.net/api/v1/international-income-statements"
        
        api_period = "year" if query.period == "annual" else "quarter"
        params = {
            "identifier": query.symbol,
            "period": api_period,
            "key": api_key,
        }

        all_data = []
        for offset in [0, 50, 100]:
            params["offset"] = offset
            try:
                res = make_request(url, params=params)
                if not res or not isinstance(res, list):
                    break
                all_data.extend(res)
                if len(res) < 50:
                    break
            except Exception:
                break

        if not all_data:
            raise EmptyDataError(f"No income statement data found for symbol {query.symbol}")

        return all_data

    @staticmethod
    def transform_data(
        query: FinancialDataIncomeStatementQueryParams,
        data: list[dict[str, Any]],
        **kwargs: Any,
    ) -> list[FinancialDataIncomeStatementData]:
        """Transform and filter the results."""
        # pylint: disable=import-outside-toplevel
        from dateutil.parser import parse

        results = []
        for record in data:
            date_str = record.get("period_end_date")
            if not date_str:
                continue
            period_ending = parse(date_str).date()
            fiscal_year = period_ending.year

            results.append(
                FinancialDataIncomeStatementData(
                    period_ending=period_ending,
                    fiscal_period=record.get("fiscal_period"),
                    fiscal_year=fiscal_year,
                    currency=record.get("currency_code"),
                    revenue=record.get("revenue"),
                    cost_of_revenue=record.get("cost_of_revenue"),
                    gross_profit=record.get("gross_profit"),
                    research_and_development_expense=record.get("research_and_development_expenses"),
                    general_and_admin_expense=record.get("general_and_administrative_expenses"),
                    total_operating_expenses=record.get("operating_expenses"),
                    operating_income=record.get("operating_income"),
                    interest_expense=record.get("interest_expense"),
                    interest_income=record.get("interest_income"),
                    net_income=record.get("net_income"),
                    basic_earnings_per_share=record.get("earnings_per_share_basic"),
                    diluted_earnings_per_share=record.get("earnings_per_share_diluted"),
                    weighted_average_shares_outstanding=record.get("weighted_average_shares_outstanding_basic"),
                    weighted_average_diluted_shares_outstanding=record.get("weighted_average_shares_outstanding_diluted"),
                )
            )

        if query.limit:
            results = results[:query.limit]

        return results
