# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 22:08:50 2019

@author: JDimarsky
"""

import sys
import pathlib

# hack to add the folder to the python path
app_path = pathlib.Path(__file__).parents[1] / "TickerParser"
sys.path.append(str(app_path))

import pytest

import ticker_parser as tp


def test_imports():
    print(tp.INDEX_LIST)


class TestOptions_OCC_Ticker_Padding:
    def test_ticker_too_little_padding(self):
        with pytest.raises(tp.RegexMatchNotFoundException):
            tp.convert_ticker("AAPL 180216C00175450", "Bloomberg")

    def test_ticker_too_much_padding(self):
        with pytest.raises(tp.RegexMatchNotFoundException):
            tp.convert_ticker("AAPL   180216C00175450", "Bloomberg")

    def test_ticker_exact_padding(self):
        actual = tp.convert_ticker("AAPL  180216C00175450", "Bloomberg")
        expected = "AAPL US 02/16/18 C175.45 Equity"
        assert actual == expected


class TestOptions_OCC_to_Bloomberg:
    def test_basic(self):
        actual = tp.convert_ticker("AAPL  180216C00170000", "Bloomberg")
        expected = "AAPL US 02/16/18 C170.0 Equity"
        assert actual == expected

    def test_strike_price_50(self):
        actual = tp.convert_ticker("AAPL  180216C00175500", "Bloomberg")
        expected = "AAPL US 02/16/18 C175.5 Equity"
        assert actual == expected

    def test_strike_price_00(self):
        actual = tp.convert_ticker("AAPL  180216C00175000", "Bloomberg")
        expected = "AAPL US 02/16/18 C175.0 Equity"
        assert actual == expected

    def test_strike_price_others(self):
        actual = tp.convert_ticker("AAPL  180216C00175450", "Bloomberg")
        expected = "AAPL US 02/16/18 C175.45 Equity"
        assert actual == expected


class TestOptions_OCC_to_Eze:
    def test_basic(self):
        actual = tp.convert_ticker("AAPL  180216C00170000", "Eze")
        expected = "AAPL US 02/16/18 C170.0"
        assert actual == expected

    def test_strike_price_50(self):
        actual = tp.convert_ticker("AAPL  180216C00175500", "Eze")
        expected = "AAPL US 02/16/18 C175.5"
        assert actual == expected

    def test_strike_price_00(self):
        actual = tp.convert_ticker("AAPL  180216C00175000", "Eze")
        expected = "AAPL US 02/16/18 C175.0"
        assert actual == expected

    def test_strike_price_others(self):
        actual = tp.convert_ticker("AAPL  180216C00175450", "Eze")
        expected = "AAPL US 02/16/18 C175.45"
        assert actual == expected


class TestOptions_Bloomberg_to_OCC:
    def test_basic(self):
        actual = tp.convert_ticker("AAPL US 02/16/18 C170.0 Equity", "OCC")
        expected = "AAPL  180216C00170000"
        assert actual == expected

    def test_strike_price_50(self):
        actual = tp.convert_ticker("AAPL US 02/16/18 C175.5 Equity", "OCC")
        expected = "AAPL  180216C00175500"
        assert actual == expected

    def test_strike_price_00(self):
        actual = tp.convert_ticker("AAPL US 02/16/18 C175.0 Equity", "OCC")
        expected = "AAPL  180216C00175000"
        assert actual == expected

    def test_strike_price_others(self):
        actual = tp.convert_ticker("AAPL US 02/16/18 C175.45 Equity", "OCC")
        expected = "AAPL  180216C00175450"
        assert actual == expected


class TestOptions_Bloomberg_to_Eze:
    def test_basic(self):
        actual = tp.convert_ticker("AAPL US 02/16/18 C170.0 Equity", "Eze")
        expected = "AAPL US 02/16/18 C170.0"
        assert actual == expected

    def test_strike_price_50(self):
        actual = tp.convert_ticker("AAPL US 02/16/18 C175.5 Equity", "Eze")
        expected = "AAPL US 02/16/18 C175.5"
        assert actual == expected

    def test_strike_price_00(self):
        actual = tp.convert_ticker("AAPL US 02/16/18 C175.0 Equity", "Eze")
        expected = "AAPL US 02/16/18 C175.0"
        assert actual == expected

    def test_strike_price_others(self):
        actual = tp.convert_ticker("AAPL US 02/16/18 C175.45 Equity", "Eze")
        expected = "AAPL US 02/16/18 C175.45"
        assert actual == expected


class TestOptions_Eze_to_OCC:
    def test_basic(self):
        actual = tp.convert_ticker("AAPL US 02/16/18 C170.0", "OCC")
        expected = "AAPL  180216C00170000"
        assert actual == expected

    def test_strike_price_50(self):
        actual = tp.convert_ticker("AAPL US 02/16/18 C175.5", "OCC")
        expected = "AAPL  180216C00175500"
        assert actual == expected

    def test_strike_price_00(self):
        actual = tp.convert_ticker("AAPL US 02/16/18 C175.0", "OCC")
        expected = "AAPL  180216C00175000"
        assert actual == expected

    def test_strike_price_others(self):
        actual = tp.convert_ticker("AAPL US 02/16/18 C175.45", "OCC")
        expected = "AAPL  180216C00175450"
        assert actual == expected


class TestOptions_Eze_to_Bloomberg:
    def test_basic(self):
        actual = tp.convert_ticker("AAPL US 02/16/18 C170.0", "Bloomberg")
        expected = "AAPL US 02/16/18 C170.0 Equity"
        assert actual == expected

    def test_strike_price_50(self):
        actual = tp.convert_ticker("AAPL US 02/16/18 C175.5", "Bloomberg")
        expected = "AAPL US 02/16/18 C175.5 Equity"
        assert actual == expected

    def test_strike_price_00(self):
        actual = tp.convert_ticker("AAPL US 02/16/18 C175.0", "Bloomberg")
        expected = "AAPL US 02/16/18 C175.0 Equity"
        assert actual == expected

    def test_strike_price_others(self):
        actual = tp.convert_ticker("AAPL US 02/16/18 C175.45", "Bloomberg")
        expected = "AAPL US 02/16/18 C175.45 Equity"
        assert actual == expected
