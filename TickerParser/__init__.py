import json
import logging

import azure.functions as func

from . import ticker_parser as tp


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    ticker = req.params.get('ticker')
    if not ticker:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            ticker = req_body.get('ticker')

    if ticker:
        return func.HttpResponse(json.dumps(tp.parse_ticker(ticker)))
    else:
        return func.HttpResponse(
             "Please pass a ticker on the query string or in the request body",
             status_code=400
        )

