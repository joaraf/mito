#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Saga Inc.
# Distributed under the terms of the GPL License.
"""
Contains tests for the MONTH function.
"""

import pytest
import pandas as pd

from mitosheet.public.v3.sheet_functions.date_functions import MONTH

MONTH_TESTS = [
    # Just constant tests
    (['2000-1-2'], 1),
    ([pd.to_datetime('2000-4-2 13:12:11')], 4),

    # Just series tests
    ([pd.Series(data=['2000-1-2 12:45:00', '2000-11-2 15:12:00'])], pd.Series([1, 11])),
    ([pd.Series(data=['2000-1-2 12:45:00', '2000-12-2 15:45:00', None])], pd.Series([1, 12, None])),
    ([pd.Series(data=['1/2/2000', 'abc', '4/1/2000 15:12:0'])], pd.Series([1,None,4])),
]

@pytest.mark.parametrize("_argv,expected", MONTH_TESTS)
def test_month(_argv, expected):
    result = MONTH(*_argv)
    if isinstance(result, pd.Series):
        assert result.equals(expected)
    else: 
        assert result == expected
