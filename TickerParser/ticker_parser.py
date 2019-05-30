# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 22:08:50 2019

@author: JDimarsky
"""

import logging
import math
import re
from functools import lru_cache

INDEX_LIST = ["SPX", "NDX", "INDU", "COMPX", "COMPQX", "RTY", "RUT", "MNX", "VIX", "/VXG18"]
CASH_LIST = ["USD", "GBP", "WFUSUDI LX", "DGCXX", "FGTXX", "FTIXX", "IJTXX", "MISXX", "TFDXX"]


class FORMAT_TYPES:
    OCC = "OCC"
    Bloomberg = "Bloomberg"
    Eze = "Eze"
    Generic = "Generic"


class ASSET_CLASS:
    Equity = "Equity"
    Option = "Option"
    Index = "Index"
    Cash = "Cash"
    TempNonOption = "TempNonOption"


class Security:
    def __init__(
        self,
        format_type,
        asset_class,
        root_symbol,
        *,
        call_put=None,
        expiry_year=None,
        expiry_month=None,
        expiry_day=None,
        strike_price=None,
        exchange=None,
        bloomberg_suffix="",
    ):
        for key, val in locals().items():
            if val and key != "self":
                setattr(self, key, val)

    def __repr__(self):
        """shamelessly copied from ib_insync library"""
        clsName = self.__class__.__qualname__
        kwargs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{clsName}({kwargs})"


class BaseTickerFormat:
    @staticmethod
    def to_Security(regex_match) -> Security:
        raise NotImplementedError()

    @staticmethod
    def to_ticker_string(security: Security) -> str:
        raise NotImplementedError()


class OCC_Option(BaseTickerFormat):
    """
    Example OCC: AAPL  180216C00170000

    See https://en.wikipedia.org/wiki/Option_symbol
    """

    asset_class = (ASSET_CLASS.Option,)
    format_type = (FORMAT_TYPES.OCC,)
    regex_string = """
        ^(?P<root>[a-zA-Z ]{6})(?=\d{6}[CcPp]\d{8})     # beginning ticker padded with spaces, 6 total characters, only if followed by (6 digits,C or P, and 8 digits)
        (?P<expiry_year>\d{2})                          # 2 digits for yy
        (?P<expiry_month>\d{2})                         # 2 digits for mm
        (?P<expiry_day>\d{2})                           # 2 digits for dd
        (?P<call_put>[CcPp])                            # C or P for call or put
        (?P<strike>\d{8})$                              # 8 digits for strike price
    """

    @staticmethod
    def to_Security(regex_match):
        return Security(
            asset_class=ASSET_CLASS.Option,
            format_type=FORMAT_TYPES.OCC,
            bloomberg_suffix="Equity",
            call_put=regex_match.groupdict()["call_put"],
            exchange="US",
            expiry_day=int(regex_match.groupdict()["expiry_day"]),
            expiry_month=int(regex_match.groupdict()["expiry_month"]),
            expiry_year=int(regex_match.groupdict()["expiry_year"]),
            root_symbol=regex_match.groupdict()["root"].strip(), # remove whitespace padding from root
            strike_price=float(regex_match.groupdict()["strike"]) / 1000,
        )

    @staticmethod
    def to_ticker_string(s: Security) -> str:
        return (
            f"{s.root_symbol.upper()}{(6-len(s.root_symbol))*' '}{format(s.expiry_year, '0>2d')}{format(s.expiry_month, '0>2d')}"
            f"{format(s.expiry_day, '0>2d')}"
            f"{s.call_put}{format(s.strike_price*1000, '08.0f')}"
        )


class Bloomberg_Option(BaseTickerFormat):
    """
    Example Bloomberg: AAPL US 18/02/16 C170.0 Equity
    """

    asset_class = (ASSET_CLASS.Option,)
    format_type = (FORMAT_TYPES.Bloomberg,)
    regex_string = """
        ^(?P<root>[a-zA-Z]+)                # beginning ticker, 1 or more letters
        (?P<delim>\s{1})                    # one separator
        (?P<exch>\w{2})                     # 2 letter exchange symbol (like US)
        (?P<delim2>\s{1})                   # one separator    
        (?P<expiry_month>\d{2})             # 2 digit month
        (?P<date_delim>[/])                 # slash symbol
        (?P<expiry_day>\d{2})               # 2 digit day
        (?P<date_delim2>[/])                # slash symbol
        (?P<expiry_year>\d{2})              # 2 digit year
        (?P<delim3>\s{1})                   # one separator
        (?P<call_put>[CcPp])                # C or P for call or put
        (?P<strike>\d+\.?\d+|\d+)           # one or more digits for strike price
        (?P<delim4>\s{1})                   # one separator
        (?P<bb_suffix>Equity)$              # the word 'Equity'
    """

    @staticmethod
    def to_Security(regex_match):
        return Security(
            asset_class=ASSET_CLASS.Option,
            format_type=FORMAT_TYPES.Bloomberg,
            bloomberg_suffix=regex_match.groupdict()["bb_suffix"],
            call_put=regex_match.groupdict()["call_put"],
            exchange=regex_match.groupdict()["exch"],
            expiry_day=int(regex_match.groupdict()["expiry_day"]),
            expiry_month=int(regex_match.groupdict()["expiry_month"]),
            expiry_year=int(regex_match.groupdict()["expiry_year"]),
            root_symbol=regex_match.groupdict()["root"],
            strike_price=float(regex_match.groupdict()["strike"]),
        )

    @staticmethod
    def to_ticker_string(s: Security) -> str:
        # if first digit after the decimal is 0 or 5, then round to 1 decimal place, otherwise 2 places
        if round((s.strike_price - math.trunc(s.strike_price)), 4) in (float(0.5), float(0.0)):
            fmt = ".1f"
        else:
            fmt = ".2f"

        return (
            f"{s.root_symbol.upper()} {s.exchange} "
            f"{format(s.expiry_month, '0>2d')}/{format(s.expiry_day, '0>2d')}/{format(s.expiry_year, '0>2d')} "
            f"{s.call_put}{format(s.strike_price, fmt)} {s.bloomberg_suffix}"
        )


class Eze_Option(BaseTickerFormat):
    """
    Example Eze: AAPL US 18/02/16 C170.0
    """

    asset_class = (ASSET_CLASS.Option,)
    format_type = (FORMAT_TYPES.Eze,)
    regex_string = """
        ^(?P<root>[a-zA-Z]+)                # beginning ticker, 1 or more letters
        (?P<delim>\s{1})                    # one separator
        (?P<exch>\w{2})                     # 2 letter exchange symbol (like US)
        (?P<delim2>\s{1})                   # one separator    
        (?P<expiry_month>\d{2})             # 2 digit month
        (?P<date_delim>[/])                 # slash symbol
        (?P<expiry_day>\d{2})               # 2 digit day
        (?P<date_delim2>[/])                # slash symbol
        (?P<expiry_year>\d{2})              # 2 digit year
        (?P<delim3>\s{1})                   # one separator
        (?P<call_put>[CcPp])                # C or P for call or put
        (?P<strike>\d+\.?\d+|\d+)$          # one or more digits for strike price
    """

    @staticmethod
    def to_Security(regex_match):
        return Security(
            asset_class=ASSET_CLASS.Option,
            format_type=FORMAT_TYPES.Eze,
            bloomberg_suffix="Equity",
            call_put=regex_match.groupdict()["call_put"],
            exchange=regex_match.groupdict()["exch"],
            expiry_day=int(regex_match.groupdict()["expiry_day"]),
            expiry_month=int(regex_match.groupdict()["expiry_month"]),
            expiry_year=int(regex_match.groupdict()["expiry_year"]),
            root_symbol=regex_match.groupdict()["root"],
            strike_price=float(regex_match.groupdict()["strike"]),
        )

    @staticmethod
    def to_ticker_string(s: Security) -> str:
        # if first digit after the decimal is 0 or 5, then round to 1 decimal place, otherwise 2 places
        if round((s.strike_price - math.trunc(s.strike_price)), 4) in (float(0.5), float(0.0)):
            fmt = ".1f"
        else:
            fmt = ".2f"

        return (
            f"{s.root_symbol.upper()} {s.exchange} "
            f"{format(s.expiry_month, '0>2d')}/{format(s.expiry_day, '0>2d')}/{format(s.expiry_year, '0>2d')} "
            f"{s.call_put}{format(s.strike_price, fmt)}"
        )


class Generic_Non_Option(BaseTickerFormat):

    asset_class = (ASSET_CLASS.TempNonOption,)
    format_type = FORMAT_TYPES.Generic
    regex_string = """
        ^(?P<root>[a-zA-Z0-9._\-/]{1,10})$        #  ticker, 1 to 10 word characters or one of [.-/]
    """

    @staticmethod
    def to_Security(regex_match):
        sec = Security(
            format_type=FORMAT_TYPES.Generic,
            exchange="US",
            root_symbol=regex_match.groupdict()["root"],
            asset_class=None,  # temp, changed below, just need to pass something
        )
        if regex_match.groupdict()["root"] in INDEX_LIST:
            sec.asset_class = ASSET_CLASS.Index
            sec.bloomberg_suffix = "Index"
        elif regex_match.groupdict()["root"] in CASH_LIST:
            sec.asset_class = ASSET_CLASS.Cash
        else:
            sec.asset_class = ASSET_CLASS.Equity
            sec.bloomberg_suffix = "Equity"
        return sec

    @staticmethod
    def to_ticker_string(s: Security) -> str:
        return s.root_symbol.upper()


class Bloomberg_Equity(BaseTickerFormat):

    asset_class = (ASSET_CLASS.Equity,)
    format_type = FORMAT_TYPES.Bloomberg
    regex_string = """
        ^(?P<root>[a-zA-Z0-9._\-/]{1,10})   # beginning ticker, 1 to 10 word characters or one of [.-/]
        (?P<delim>\s{1})                    # one separator
        ((?P<exch>\w{2})                    # 2 letter exchange symbol (like US), optional
        (?P<delim2>\s{1}))?                 # one separator, optional 
        (?P<bb_suffix>Equity)$              # the word 'Equity'
    """

    @staticmethod
    def to_Security(regex_match):
        return Security(
            asset_class=ASSET_CLASS.Equity,
            format_type=FORMAT_TYPES.Bloomberg,
            bloomberg_suffix="Equity",
            exchange=regex_match.groupdict().get("exch", "US"),
            root_symbol=regex_match.groupdict()["root"],
        )

    @staticmethod
    def to_ticker_string(s: Security) -> str:
        return f"{s.root_symbol.upper()} {s.exchange} {s.bloomberg_suffix}"


class Bloomberg_Index(BaseTickerFormat):

    asset_class = (ASSET_CLASS.Index,)
    format_type = FORMAT_TYPES.Bloomberg
    regex_string = """
        ^(?P<root>[a-zA-Z0-9._\-/]{1,10})   # beginning ticker, 1 to 10 word characters or one of [.-/]
        (?P<delim>\s{1})                    # one separator
        (?P<bb_suffix>Index)$               # the word 'Index'
    """

    @staticmethod
    def to_Security(regex_match):
        return Security(
            asset_class=ASSET_CLASS.Index,
            format_type=FORMAT_TYPES.Bloomberg,
            bloomberg_suffix="Index",
            root_symbol=regex_match.groupdict()["root"],
        )

    @staticmethod
    def to_ticker_string(s: Security) -> str:
        return f"{s.root_symbol.upper()} {s.bloomberg_suffix}"


# List of formats to SEARCH through when trying to parse a ticker
FORMATS_TO_SEARCH = [
    OCC_Option,
    Bloomberg_Option,
    Eze_Option,
    Generic_Non_Option,
    Bloomberg_Equity,
    Bloomberg_Index,
]


# Dictionary of formats by Asset Class to search when REBUILDING a ticker, not the same as the list to SEARCH
FORMATS_FOR_REBUILD = {
    ASSET_CLASS.Option: {
        FORMAT_TYPES.Bloomberg: Bloomberg_Option,
        FORMAT_TYPES.Eze: Eze_Option,
        FORMAT_TYPES.OCC: OCC_Option,
    },
    ASSET_CLASS.Equity: {
        FORMAT_TYPES.Bloomberg: Bloomberg_Equity,
        FORMAT_TYPES.Eze: Generic_Non_Option,
        FORMAT_TYPES.OCC: Generic_Non_Option,
    },
    ASSET_CLASS.Index: {
        FORMAT_TYPES.Bloomberg: Bloomberg_Index,
        FORMAT_TYPES.Eze: Generic_Non_Option,
        FORMAT_TYPES.OCC: Generic_Non_Option,
    },
    ASSET_CLASS.Cash: {
        FORMAT_TYPES.Bloomberg: Generic_Non_Option,
        FORMAT_TYPES.Eze: Generic_Non_Option,
        FORMAT_TYPES.OCC: Generic_Non_Option,
    },
}


def _parse_ticker(ticker: str) -> Security:
    matching_formats = []
    for fmt in FORMATS_TO_SEARCH:
        match = re.match(fmt.regex_string, ticker, re.VERBOSE)
        if match:
            matching_formats.append((fmt, match))

    if len(matching_formats) == 1:
        return matching_formats[0][0].to_Security(matching_formats[0][1])
    else:
        return f"Could not find exactly one regex match for ticker: {ticker}"


@lru_cache(maxsize=128, typed=False)
def parse_ticker(ticker: str) -> dict:
    logging.info(f"Parsing ticker: {ticker}")
    sec = _parse_ticker(ticker)
    if isinstance(sec, Security):
        d = dict(sec.__dict__)
        d["ticker_original"] = ticker
        d["ticker_occ"] = FORMATS_FOR_REBUILD[sec.asset_class][FORMAT_TYPES.OCC].to_ticker_string(
            sec
        )
        d["ticker_bloomberg"] = FORMATS_FOR_REBUILD[sec.asset_class][
            FORMAT_TYPES.Bloomberg
        ].to_ticker_string(sec)
        d["ticker_eze"] = FORMATS_FOR_REBUILD[sec.asset_class][FORMAT_TYPES.Eze].to_ticker_string(
            sec
        )
        return d
    else:
        return {"ticker_original": ticker, "error_message": sec}


class RegexMatchNotFoundException(Exception):
    pass


def convert_ticker(ticker: str, target_format: str) -> str:
    fmt = getattr(FORMAT_TYPES, target_format)
    sec = _parse_ticker(ticker)
    if isinstance(sec, Security):
        return FORMATS_FOR_REBUILD[sec.asset_class][fmt].to_ticker_string(sec)
    else:
        raise RegexMatchNotFoundException(f"No regex matches found for: {ticker}")
