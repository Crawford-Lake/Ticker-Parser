import json
import logging

import azure.functions as func

from . import ticker_parser as tp


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    ticker = req.params.get("ticker")
    if not ticker:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            ticker = req_body.get("ticker")

    if ticker:
        # multiple tickers passed in via req body
        if isinstance(ticker, (tuple, list)):
            return func.HttpResponse(json.dumps([tp.parse_ticker(t) for t in ticker]))
        # multiple tickers passed in via req params, e.g. "AAPL,MSFT,IBM"
        elif isinstance(ticker, str) and "," in ticker:
            return func.HttpResponse(json.dumps([tp.parse_ticker(t) for t in ticker.split(",")]))
        # single ticker passed
        else:
            return func.HttpResponse(json.dumps(tp.parse_ticker(ticker)))
    else:
        return func.HttpResponse(
            "No valid input was provided. Please pass a ticker on the query string (ticker=AAPL) or in the request body (as JSON)",
            status_code=400,
        )
