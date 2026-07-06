"""FinancialData Balance Sheet Model."""

from typing import Any, Literal
from datetime import date as dateType, datetime
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.balance_sheet import (
    BalanceSheetData,
    BalanceSheetQueryParams,
)
from pydantic import Field, field_validator


class FinancialDataBalanceSheetQueryParams(BalanceSheetQueryParams):
    """FinancialData Balance Sheet Query."""

    period: Literal["annual", "quarter"] = Field(
        default="annual",
        description="The period of the statement (annual or quarter).",
    )


class FinancialDataBalanceSheetData(BalanceSheetData):
    """FinancialData Balance Sheet Data."""

    currency: str | None = Field(default=None, description="Currency of the report.")
    cash_and_cash_equivalents: float | None = Field(default=None, description="Cash and cash equivalents.")
    accounts_receivable: float | None = Field(default=None, description="Accounts receivable.")
    inventories: float | None = Field(default=None, description="Inventories.")
    other_current_assets: float | None = Field(default=None, description="Other current assets.")
    total_current_assets: float | None = Field(default=None, description="Total current assets.")
    property_plant_and_equipment: float | None = Field(default=None, description="Property, plant, and equipment.")
    other_non_current_assets: float | None = Field(default=None, description="Other non-current assets.")
    total_non_current_assets: float | None = Field(default=None, description="Total non-current assets.")
    total_assets: float | None = Field(default=None, description="Total assets.")
    accounts_payable: float | None = Field(default=None, description="Accounts payable.")
    short_term_debt: float | None = Field(default=None, description="Short term debt.")
    other_current_liabilities: float | None = Field(default=None, description="Other current liabilities.")
    total_current_liabilities: float | None = Field(default=None, description="Total current liabilities.")
    long_term_debt: float | None = Field(default=None, description="Long term debt.")
    other_non_current_liabilities: float | None = Field(default=None, description="Other non-current liabilities.")
    total_non_current_liabilities: float | None = Field(default=None, description="Total non-current liabilities.")
    total_liabilities: float | None = Field(default=None, description="Total liabilities.")
    common_stock: float | None = Field(default=None, description="Common stock.")
    retained_earnings: float | None = Field(default=None, description="Retained earnings.")
    total_shareholders_equity: float | None = Field(default=None, description="Total shareholders' equity.")


class FinancialDataBalanceSheetFetcher(
    Fetcher[FinancialDataBalanceSheetQueryParams, list[FinancialDataBalanceSheetData]]
):
    """FinancialData Balance Sheet Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FinancialDataBalanceSheetQueryParams:
        """Transform the query parameters."""
        return FinancialDataBalanceSheetQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FinancialDataBalanceSheetQueryParams,
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

        url = "https://financialdata.net/api/v1/international-balance-sheet-statements"
        
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
            raise EmptyDataError(f"No balance sheet data found for symbol {query.symbol}")

        return all_data

    @staticmethod
    def transform_data(
        query: FinancialDataBalanceSheetQueryParams,
        data: list[dict[str, Any]],
        **kwargs: Any,
    ) -> list[FinancialDataBalanceSheetData]:
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
                FinancialDataBalanceSheetData(
                    period_ending=period_ending,
                    fiscal_period=record.get("fiscal_period"),
                    fiscal_year=fiscal_year,
                    currency=record.get("currency_code"),
                    cash_and_cash_equivalents=record.get("cash_and_cash_equivalents"),
                    accounts_receivable=record.get("accounts_receivable"),
                    inventories=record.get("inventories"),
                    other_current_assets=record.get("other_assets_current"),
                    total_current_assets=record.get("total_assets_current"),
                    property_plant_and_equipment=record.get("property_plant_and_equipment"),
                    other_non_current_assets=record.get("other_assets_non_current"),
                    total_non_current_assets=record.get("total_assets_non_current"),
                    total_assets=record.get("total_assets"),
                    accounts_payable=record.get("accounts_payable"),
                    short_term_debt=record.get("short_term_debt"),
                    other_current_liabilities=record.get("other_liabilities_current"),
                    total_current_liabilities=record.get("total_liabilities_current"),
                    long_term_debt=record.get("long_term_debt"),
                    other_non_current_liabilities=record.get("other_liabilities_non_current"),
                    total_non_current_liabilities=record.get("total_liabilities_non_current"),
                    total_liabilities=record.get("total_liabilities"),
                    common_stock=record.get("common_stock"),
                    retained_earnings=record.get("retained_earnings"),
                    total_shareholders_equity=record.get("total_shareholders_equity"),
                )
            )

        if query.limit:
            results = results[:query.limit]

        return results
