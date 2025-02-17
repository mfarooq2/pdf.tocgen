"""Filter on span dictionaries

This module contains the internal representation of heading filters, which are
used to test if a span should be included in the ToC.
"""

import re

from typing import Optional
from re import Pattern

DEF_TOLERANCE: float = 1e-5


def admits_float(expect: Optional[float],
                 actual: Optional[float],
                 tolerance: float) -> bool:
    """Check if a float should be admitted by a filter"""
    return (expect is None) or \
           (actual is not None and abs(expect - actual) <= tolerance)



class ToCFilter:
    """Filter on span dictionary to pick out headings in the ToC"""
    # The level of the title, strictly > 0
    level: int
    # When set, the filter will be more *greedy* and extract all the text in a
    # block even when at least one match occurs
    greedy: bool
    font_name: Optional[str] = None
    font_size: Optional[float] = None

    def __init__(self, fltr_dict: dict):
        lvl = fltr_dict.get('level')

        if lvl is None:
            raise ValueError("filter's 'level' is not set")
        if lvl < 1:
            raise ValueError("filter's 'level' must be >= 1")

        self.level = lvl
        self.greedy = fltr_dict.get('greedy', False)
        self.font_name = fltr_dict.get('font', {}).get('name')
        self.font_size = fltr_dict.get('font', {}).get('size')

    def admits(self, spn: dict) -> bool:
        """Check if the filter admits the span

        Arguments
          spn: the span dict to be checked
        Returns
          False if the span doesn't match the filter
        """
        if self.font_name is not None and self.font_name != spn.get('font'):
            return False
        return self.font_size is None or self.font_size == spn.get('size')
