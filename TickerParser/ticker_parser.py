# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 22:08:50 2019

@author: JDimarsky
"""

import re



class FORMAT_TYPES():
    OCC = 'OCC'
    Bloomberg = 'Bloomberg'
    Eze = 'Eze'
    Generic = 'Generic'

class ASSET_CLASS():
    Equity = 'Equity'
    Option = 'Option'
    Index = 'Index'
    Cash = 'Cash'
    TempNonOption = 'TempNonOption'
    

class Security():
    
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
            bloomberg_suffix='',
            ):
        for key, val in locals().items():
            if val and key != 'self':
                setattr(self, key, val)
                
    def __repr__(self):
        '''shamelessly copied from ib_insync library'''
        clsName = self.__class__.__qualname__
        kwargs = ', '.join(f'{k}={v!r}' for k, v in self.__dict__.items())
        return f'{clsName}({kwargs})'
                        
    
class BaseTickerFormat():
    
    def __init__(self, 
                 asset_class: ASSET_CLASS, 
                 format_type: FORMAT_TYPES,
                 regex_string: str):
        self.asset_class = asset_class
        self.format_type = format_type
        self.regex_string = regex_string
        self._index_list = ["SPX", "NDX", "INDU", "COMPX", "COMPQX", "RTY", "RUT", "MNX", "VIX", "/VXG18"]
        self._cash_list = [ "USD", "GBP", "WFUSUDI LX", "DGCXX", "FGTXX", "FTIXX", "IJTXX", "MISXX", "TFDXX"]
        
    def to_Security(self, regex_match) -> Security:
        raise NotImplementedError()
    
    def to_ticker_string(self, security: Security) -> str:
        raise NotImplementedError()
        
        
        
class OCC_Option(BaseTickerFormat):
    
    def __init__(self):
        super().__init__(
                asset_class=ASSET_CLASS.Option,
                format_type=FORMAT_TYPES.OCC,
                regex_string='''
                    ^(?<root>\w+)                       # beginning ticker, 1 or more word characters
                    (?<delim>\s{1,10})                  # 1 to 10 separators
                    (?<expiry_year>\d{2})               # 2 digits for yy
                    (?<expiry_month>\d{2})              # 2 digits for mm
                    (?<expiry_day>\d{2})                # 2 digits for dd
                    (?<call_put>[CcPp])                 # C or P for call or put
                    (?<strike>\d{8})$                   # 8 digits for strike price
                '''
            )
    def to_Security(self, regex_match):
        pass
        
        
        
    
    
    
    
    
                