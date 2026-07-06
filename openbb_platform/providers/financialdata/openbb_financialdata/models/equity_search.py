"""FinancialData Equity Search Model."""

from typing import Any
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_search import (
    EquitySearchData,
    EquitySearchQueryParams,
)
from pydantic import Field


class FinancialDataEquitySearchQueryParams(EquitySearchQueryParams):
    """FinancialData Equity Search Query."""
    pass


class FinancialDataEquitySearchData(EquitySearchData):
    """FinancialData Equity Search Data."""
    pass


class FinancialDataEquitySearchFetcher(
    Fetcher[FinancialDataEquitySearchQueryParams, list[FinancialDataEquitySearchData]]
):
    """FinancialData Equity Search Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FinancialDataEquitySearchQueryParams:
        """Transform the query parameters."""
        return FinancialDataEquitySearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FinancialDataEquitySearchQueryParams,
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

        url = "https://financialdata.net/api/v1/international-stock-symbols"
        params = {"key": api_key} if api_key else {}

        all_data = []
        for offset in [0, 500, 1000]:
            params["offset"] = offset
            try:
                res = make_request(url, params=params)
                if not res or not isinstance(res, list):
                    break
                all_data.extend(res)
                if len(res) < 500:
                    break
            except Exception:
                break

        if not all_data:
            raise EmptyDataError("No symbol data retrieved from FinancialData.net")

        return all_data

    @staticmethod
    def transform_data(
        query: FinancialDataEquitySearchQueryParams,
        data: list[dict[str, Any]],
        **kwargs: Any,
    ) -> list[FinancialDataEquitySearchData]:
        """Transform and filter the results."""
        results = []
        for record in data:
            symbol = record.get("trading_symbol")
            name = record.get("registrant_name")

            if query.query:
                q = query.query.lower()
                matches = False
                if query.is_symbol:
                    if symbol and q in symbol.lower():
                        matches = True
                else:
                    if (symbol and q in symbol.lower()) or (name and q in name.lower()):
                        matches = True
                if not matches:
                    continue

            results.append(
                FinancialDataEquitySearchData(
                    symbol=symbol,
                    name=name,
                )
            )
        return results
