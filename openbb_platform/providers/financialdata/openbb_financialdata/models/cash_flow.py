"""FinancialData Cash Flow Statement Model."""

from typing import Any, Literal
from datetime import date as dateType, datetime
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cash_flow import (
    CashFlowStatementData,
    CashFlowStatementQueryParams,
)
from pydantic import Field, field_validator


class FinancialDataCashFlowQueryParams(CashFlowStatementQueryParams):
    """FinancialData Cash Flow Statement Query."""

    period: Literal["annual", "quarter"] = Field(
        default="annual",
        description="The period of the statement (annual or quarter).",
    )


class FinancialDataCashFlowData(CashFlowStatementData):
    """FinancialData Cash Flow Statement Data."""

    currency: str | None = Field(default=None, description="Currency of the report.")
    depreciation_and_amortization: float | None = Field(default=None, description="Depreciation and amortization.")
    share_based_compensation: float | None = Field(default=None, description="Share-based compensation expense.")
    net_cash_from_operating_activities: float | None = Field(default=None, description="Net cash from operating activities.")
    capital_expenditure: float | None = Field(default=None, description="Capital expenditure.")
    business_acquisitions_and_disposals: float | None = Field(default=None, description="Acquisitions and disposals of businesses.")
    net_cash_from_investing_activities: float | None = Field(default=None, description="Net cash from investing activities.")
    dividends_paid: float | None = Field(default=None, description="Dividends paid.")
    common_stock_issued: float | None = Field(default=None, description="Common stock issued.")
    common_stock_repurchased: float | None = Field(default=None, description="Common stock repurchased.")
    debt_issued: float | None = Field(default=None, description="Debt issued.")
    debt_repaid: float | None = Field(default=None, description="Debt repaid.")
    net_cash_from_financing_activities: float | None = Field(default=None, description="Net cash from financing activities.")
    net_change_in_cash: float | None = Field(default=None, description="Net change in cash.")
    cash_at_end_of_period: float | None = Field(default=None, description="Cash at end of period.")


class FinancialDataCashFlowFetcher(
    Fetcher[FinancialDataCashFlowQueryParams, list[FinancialDataCashFlowData]]
):
    """FinancialData Cash Flow Statement Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FinancialDataCashFlowQueryParams:
        """Transform the query parameters."""
        return FinancialDataCashFlowQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FinancialDataCashFlowQueryParams,
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

        url = "https://financialdata.net/api/v1/international-cash-flow-statements"
        
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
            raise EmptyDataError(f"No cash flow data found for symbol {query.symbol}")

        return all_data

    @staticmethod
    def transform_data(
        query: FinancialDataCashFlowQueryParams,
        data: list[dict[str, Any]],
        **kwargs: Any,
    ) -> list[FinancialDataCashFlowData]:
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
                FinancialDataCashFlowData(
                    period_ending=period_ending,
                    fiscal_period=record.get("fiscal_period"),
                    fiscal_year=fiscal_year,
                    currency=record.get("currency_code"),
                    depreciation_and_amortization=record.get("depreciation_and_amortization"),
                    share_based_compensation=record.get("share_based_compensation_expense"),
                    net_cash_from_operating_activities=record.get("cash_from_operating_activities"),
                    capital_expenditure=record.get("acquisition_of_property_plant_and_equipment"),
                    business_acquisitions_and_disposals=record.get("acquisition_of_business"),
                    net_cash_from_investing_activities=record.get("cash_from_investing_activities"),
                    dividends_paid=record.get("payments_of_dividends"),
                    common_stock_issued=record.get("issuance_of_common_stock"),
                    common_stock_repurchased=record.get("repurchase_of_common_stock"),
                    debt_issued=record.get("issuance_of_long_term_debt"),
                    debt_repaid=record.get("repayment_of_long_term_debt"),
                    net_cash_from_financing_activities=record.get("cash_from_financing_activities"),
                    net_change_in_cash=record.get("change_in_cash"),
                    cash_at_end_of_period=record.get("cash_at_end_of_period"),
                )
            )

        if query.limit:
            results = results[:query.limit]

        return results
