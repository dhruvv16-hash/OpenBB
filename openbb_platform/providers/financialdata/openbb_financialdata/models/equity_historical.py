"""FinancialData Equity Historical Price Model."""

from typing import Any
from datetime import date as dateType
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_historical import (
    EquityHistoricalData,
    EquityHistoricalQueryParams,
)
from pydantic import Field


class FinancialDataEquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """FinancialData Equity Historical Price Query."""
    pass


class FinancialDataEquityHistoricalData(EquityHistoricalData):
    """FinancialData Equity Historical Price Data."""
    pass


class FinancialDataEquityHistoricalFetcher(
    Fetcher[FinancialDataEquityHistoricalQueryParams, list[FinancialDataEquityHistoricalData]]
):
    """FinancialData Equity Historical Price Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FinancialDataEquityHistoricalQueryParams:
        """Transform the query parameters."""
        return FinancialDataEquityHistoricalQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FinancialDataEquityHistoricalQueryParams,
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

        url = "https://financialdata.net/api/v1/international-stock-prices"
        params = {
            "identifier": query.symbol,
            "key": api_key,
        }

        all_data = []
        for offset in [0, 300, 600, 900]:
            params["offset"] = offset
            try:
                res = make_request(url, params=params)
                if not res or not isinstance(res, list):
                    break
                all_data.extend(res)
                if len(res) < 300:
                    break
            except Exception:
                break

        if not all_data:
            raise EmptyDataError(f"No historical price data found for symbol {query.symbol}")

        return all_data

    @staticmethod
    def transform_data(
        query: FinancialDataEquityHistoricalQueryParams,
        data: list[dict[str, Any]],
        **kwargs: Any,
    ) -> list[FinancialDataEquityHistoricalData]:
        """Transform and filter the results."""
        # pylint: disable=import-outside-toplevel
        from dateutil.parser import parse

        results = []
        for record in data:
            date_str = record.get("date")
            if not date_str:
                continue
            rec_date = parse(date_str).date()

            if query.start_date and rec_date < query.start_date:
                continue
            if query.end_date and rec_date > query.end_date:
                continue

            results.append(
                FinancialDataEquityHistoricalData(
                    date=rec_date,
                    open=record.get("open"),
                    high=record.get("high"),
                    low=record.get("low"),
                    close=record.get("close"),
                    volume=record.get("volume"),
                )
            )

        results.sort(key=lambda x: x.date)
        return results
