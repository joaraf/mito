#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Saga Inc.
# Distributed under the terms of the GPL License.
"""
Contains tests for edit events.
"""
from typing import Any, List
import numpy as np
import pandas as pd
import pytest

from mitosheet.step_performers.filter import (FC_BOOLEAN_IS_TRUE, FC_DATETIME_EXACTLY, FC_NUMBER_EXACTLY, FC_NUMBER_GREATER, FC_NUMBER_LESS,
                                              FC_STRING_CONTAINS, FC_STRING_STARTS_WITH)
from mitosheet.step_performers.graph_steps.graph_utils import BAR
from mitosheet.step_performers.sort import SORT_DIRECTION_ASCENDING
from mitosheet.tests.decorators import pandas_post_1_only, pandas_pre_1_only
from mitosheet.tests.test_utils import create_mito_wrapper_dfs
from mitosheet.types import FilterOnColumnHeader
from mitosheet.saved_analyses import read_and_upgrade_analysis


def test_simple_pivot():
    df1 = pd.DataFrame(data={'Name': ['Nate', 'Nate'], 'Height': [4, 5]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(0, ['Name'], [], {'Height': ['sum']})
    mito.set_formula('=LEN(Name)', 1, 'B', add_column=True)

    assert mito.dfs[1].equals(
        pd.DataFrame(data={'Name': ['Nate'], 'Height sum': [9], 'B': [4]})
    )

def test_simple_pivot_does_not_let_spaces_stay_in_columns():
    df1 = pd.DataFrame(data={'Name': ['Nate Rush'], 'Height': [4]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(0, [], ['Name'], {'Height': ['sum']})

    assert mito.dfs[1].equals(
        pd.DataFrame(data={'level_0': ['Height'], 'level_1': ['sum'], 'Nate Rush': [4]})
    )

def test_pivot_nan_works_with_agg_functions():
    df1 = pd.DataFrame(data={'type': ['person', 'person', 'dog', None], 'B': [10, None, 5, 4]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(0, ['type'], [], {'B': ['sum', 'mean', 'min', 'max']})

    assert mito.dfs[1].equals(
        pd.DataFrame(data={'type': ['dog', 'person'], 'B max': [5.0, 10.0], 'B mean': [5.0, 10.0], 'B min': [5.0, 10.0], 'B sum': [5.0, 10.0]})
    )


@pandas_pre_1_only
def test_pivot_transpiles_pivot_by_mulitple_columns_pre_1():
    df1 = pd.DataFrame(data={'First_Name': ['Nate', 'Nate'], 'Last_Name': ['Rush', 'Jack'], 'Height': [4, 5]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(
        0, [], ['First_Name', 'Last_Name'], {'Height': ['sum']}
    )
    
    assert mito.dfs[1].equals(
        pd.DataFrame(data={
            'level_0': ['Height', 'Height'],
            'level_1': ['sum', 'sum'],
            'First_Name': ['Nate', 'Nate'],
            'Last_Name': ['Jack', 'Rush'],
            0: [5, 4]
        })
    )

@pandas_post_1_only
def test_pivot_transpiles_pivot_by_mulitple_columns_post_1():
    df1 = pd.DataFrame(data={'First_Name': ['Nate', 'Nate'], 'Last_Name': ['Rush', 'Jack'], 'Height': [4, 5]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(
        0, [], ['First_Name', 'Last_Name'], {'Height': ['sum']}
    )   

    assert mito.dfs[1].equals(
        pd.DataFrame(data={
            'level_0': ['Height'],
            'level_1': ['sum'],
            'Nate Jack': [5],
            'Nate Rush': [4]
        })
    )

def test_pivot_transpiles_pivot_mulitple_columns_and_rows():
    df1 = pd.DataFrame(data={'First_Name': ['Nate', 'Nate'], 'Last_Name': ['Rush', 'Jack'], 'Height': [4, 5]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(
        0, ['Height'], ['First_Name', 'Last_Name'], {'Height': ['sum']}
    )   

    assert mito.dfs[1].equals(
        pd.DataFrame(data={
            'Height': [4, 5],
            'Height sum Nate Jack': [np.NaN, 5],
            'Height sum Nate Rush': [4, np.NaN]
        })
    )

@pandas_pre_1_only
def test_pivot_transpiles_pivot_mulitple_columns_non_strings_pre_1():
    df1 = pd.DataFrame(data={'First_Name': ['Nate', 'Nate'], 'Last_Name': [0, 1], 'Height': [4, 5]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(
        0, [], ['First_Name', 'Last_Name'], {'Height': ['sum']}
    )   

    assert mito.dfs[1].equals(
        pd.DataFrame(data={
            'level_0': ['Height', 'Height'],
            'level_1': ['sum', 'sum'],
            'First_Name': ['Nate', 'Nate'],
            'Last_Name': [0, 1],
            0: [4, 5]
        })
    )

@pandas_post_1_only
def test_pivot_transpiles_pivot_mulitple_columns_non_strings_post_1():
    df1 = pd.DataFrame(data={'First_Name': ['Nate', 'Nate'], 'Last_Name': [0, 1], 'Height': [4, 5]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(
        0, [], ['First_Name', 'Last_Name'], {'Height': ['sum']}
    )   

    assert mito.dfs[1].equals(
        pd.DataFrame(data={
            'level_0': ['Height'],
            'level_1': ['sum'],
            'Nate 0': [4],
            'Nate 1': [5]
        })
    )

def test_pivot_transpiles_with_no_keys_or_values():
    df1 = pd.DataFrame(data={'First_Name': ['Nate', 'Nate'], 'Last_Name': [0, 1], 'Height': [4, 5]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(
        0, [], [], {}
    )   

    assert mito.dfs[1].equals(
        pd.DataFrame(data={})
    )

def test_pivot_transpiles_with_values_but_no_keys():
    df1 = pd.DataFrame(data={'First_Name': ['Nate', 'Nate'], 'Last_Name': [0, 1], 'Height': [4, 5]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(
        0, [], [], {'Height': 'sum'}
    )   

    assert mito.dfs[1].equals(
        pd.DataFrame(data={})
    )


def test_pivot_transpiles_with_keys_but_no_values():
    df1 = pd.DataFrame(data={'First_Name': ['Nate', 'Nate'], 'Last_Name': [0, 1], 'Height': [4, 5]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(
        0, ['First_Name'], [], {}
    )   

    assert mito.dfs[1].equals(
        pd.DataFrame(data={})
    )



def test_pivot_count_unique():
    df1 = pd.DataFrame(data={'First_Name': ['Nate', 'Nate'], 'Last_Name': [0, 1], 'Height': [4, 5]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(
        0, ['First_Name'], ['Last_Name'], {'Height': ['count unique']}
    )   
    assert mito.dfs[1].equals(
        pd.DataFrame(data={'First_Name': ['Nate'], 'Height nunique 0': [1], 'Height nunique 1': [1]})
    )

def test_pivot_rows_and_values_overlap():
    df1 = pd.DataFrame(data={'Name': ['Nate', 'Nate', 'Aaron', 'Jake', 'Jake'], 'Height': [4, 5, 6, 7, 8]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(0, ['Name'], [], {'Name': ['count']})

    assert len(mito.steps_including_skipped) == 2
    assert mito.dfs[1].equals(
        pd.DataFrame(data={'Name': ['Aaron', 'Jake', 'Nate'], 'Name count': [1, 2, 2]})
    )


def test_pivot_rows_and_values_and_columns_overlap():
    df1 = pd.DataFrame(data={'Name': ['Nate', 'Nate', 'Aaron', 'Jake', 'Jake'], 'Height': [4, 5, 6, 7, 8]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(0, ['Name'], ['Name'], {'Name': ['count']})

    assert len(mito.steps_including_skipped) == 2
    assert mito.dfs[1].equals(
        pd.DataFrame(data={
            'Name': ['Aaron', 'Jake', 'Nate'], 
            'Name count Aaron': [1.0, None, None],
            'Name count Jake': [None, 2.0, None],
            'Name count Nate': [None, None, 2.0],
        })
    )


def test_pivot_by_mulitple_functions():
    df1 = pd.DataFrame(data={'Name': ['Nate', 'Nate'], 'Height': [4, 5]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(0, ['Name'], [], {'Height': ['min', 'max']})

    assert len(mito.steps_including_skipped) == 2
    assert mito.dfs[1].equals(
        pd.DataFrame(data={'Name': ['Nate'], 'Height max': [5], 'Height min': [4]})
    )


def test_pivot_with_optional_parameter_sheet_index():
    df1 = pd.DataFrame(data={'Name': ['Nate', 'Nate'], 'Height': [4, 5]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(0, ['Name'], [], {'Height': ['min']})
    mito.pivot_sheet(0, ['Name'], [], {'Height': ['max']}, destination_sheet_index=1)

    assert mito.dfs[1].equals(
        pd.DataFrame(data={'Name': ['Nate'], 'Height max': [5]})
    )


def test_all_other_steps_after_pivot():
    df1 = pd.DataFrame(data={'Name': ['Nate', 'Nate'], 'Height': [4, 5]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(0, ['Name'], [], {'Height': ['min']})

    # Run all the other steps
    mito.set_cell_value(1, 'Name', 0, 'Dork')
    mito.change_column_dtype(1, ['Height min'], 'string')
    mito.add_column(1, 'A')
    mito.add_column(1, 'B')
    mito.delete_columns(1, ['B'])
    mito.set_formula('=Name', 1, 'A')

    assert mito.dfs[1].equals(
        pd.DataFrame({'Name': ['Dork'], 'Height min': ['4'], 'A': ['Dork']})
    )

    # Duplicate and merge with the original dataframe
    mito.duplicate_dataframe(1)
    mito.set_cell_value(2, 'Name', 0, 'Nate')
    mito.merge_sheets('left', 0, 2, [['Name', 'Name']], ['Name'], ['Name'])
    mito.set_cell_value(3, 'Name', 0, 'Aaron')

    # Filter down in the pivot dataframe, and the merged dataframe
    mito.filter(1, 'Height min', 'And', FC_STRING_CONTAINS, "5")
    mito.filter(3, 'Name', 'And', FC_STRING_CONTAINS, "Aaron")

    assert mito.dfs[1].empty
    assert mito.dfs[3].equals(
        pd.DataFrame({'Name': ['Aaron']})
    )

def test_simple_pivot_optimizes_after_delete():
    df1 = pd.DataFrame(data={'Name': ['Nate', 'Nate'], 'Height': [4, 5]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(0, ['Name'], [], {'Height': ['sum']})
    mito.delete_dataframe(1)

    assert mito.transpiled_code == []

def test_simple_pivot_edit_optimizes_after_delete():
    df1 = pd.DataFrame(data={'Name': ['Nate', 'Nate'], 'Height': [4, 5]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(0, ['Name'], [], {'Height': ['sum']})
    mito.pivot_sheet(0, ['Name'], [], {'Height': ['mean']}, destination_sheet_index=1)
    mito.delete_dataframe(1)
    
    assert len(mito.transpiled_code) == 0

def test_simple_pivot_edit_optimizes_after_delete_with_edit_to_pivot():
    df1 = pd.DataFrame(data={'Name': ['Nate', 'Nate'], 'Height': [4, 5]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(0, ['Name'], [], {'Height': ['sum']})
    mito.add_column(1, 'Test')
    mito.pivot_sheet(0, ['Name'], [], {'Height': ['mean']}, destination_sheet_index=1)
    mito.delete_dataframe(1)
    
    assert len(mito.transpiled_code) == 0

def test_simple_pivot_edit_optimizes_after_delete_with_edit_to_source():
    df1 = pd.DataFrame(data={'Name': ['Nate', 'Nate'], 'Height': [4, 5]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(0, ['Name'], [], {'Height': ['sum']})
    mito.add_column(0, 'Test')
    mito.pivot_sheet(0, ['Name'], [], {'Height': ['mean']}, destination_sheet_index=1)
    mito.delete_dataframe(1)
    
    assert len(mito.transpiled_code) >= 0

def test_simple_pivot_edit_with_delete_after_sort_and_filter():
    df1 = pd.DataFrame(data={'Name': ['Nate', 'Nate'], 'Height': [4, 5]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(0, ['Name'], [], {'Height': ['sum']})
    mito.pivot_sheet(0, ['Name'], [], {'Height': ['mean']}, destination_sheet_index=1)
    mito.sort(1, 'Height mean', SORT_DIRECTION_ASCENDING)
    mito.filter(1, 'Height mean', 'And', FC_NUMBER_EXACTLY, 5)
    mito.delete_dataframe(1)
    
    assert len(mito.transpiled_code) == 0

def test_simple_pivot_edit_after_graph():
    df1 = pd.DataFrame(data={'Name': ['Nate', 'Nate'], 'Height': [4, 5]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(0, ['Name'], [], {'Height': ['sum']})
    mito.generate_graph('test', BAR, 1, False, [], [], 400, 400)
    mito.pivot_sheet(0, ['Name'], [], {'Height': ['mean']}, destination_sheet_index=1)
    mito.sort(1, 'Height mean', SORT_DIRECTION_ASCENDING)
    mito.filter(1, 'Height mean', 'And', FC_NUMBER_EXACTLY, 5)
    mito.delete_dataframe(1)
    
    assert len(mito.transpiled_code) == 0


def test_delete_pivot_table_optimizes():
    df1 = pd.DataFrame(data={'Name': ['Nate', 'Nate'], 'Height': [4, 5]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(0, ['Name'], [], {'Height': ['sum']})
    mito.delete_dataframe(1)
    
    assert len(mito.transpiled_code) == 0

def test_delete_pivot_table_with_additional_edits_optimizes():
    df1 = pd.DataFrame(data={'Name': ['Nate', 'Nate'], 'Height': [4, 5]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(0, ['Name'], [], {'Height': ['sum']})
    mito.add_column(1, 'C')
    mito.rename_column(1, 'C', 'CC')
    mito.delete_dataframe(1)
    
    assert len(mito.transpiled_code) == 0

def test_edit_pivot_table_then_delete_optimizes():
    df1 = pd.DataFrame(data={'Name': ['Nate', 'Nate'], 'Height': [4, 5]})
    mito = create_mito_wrapper_dfs(df1)
    mito.pivot_sheet(0, ['Name'], [], {'Height': ['sum']})
    mito.add_column(1, 'C')
    mito.rename_column(1, 'C', 'CC')
    mito.pivot_sheet(0, ['Name'], [], {'Height': ['mean']}, destination_sheet_index=1)
    mito.delete_dataframe(1)
    assert len(mito.transpiled_code) == 0

def test_pivot_with_filter_no_effect_on_source_data():
    df1 = pd.DataFrame(data={'Name': ['ADR', 'Nate'], 'Height': [4, 5]})
    mito = create_mito_wrapper_dfs(df1)

    mito.pivot_sheet(0, ['Name'], [], {'Height': ['sum']}, pivot_filters=[
            {
                'column_header': 'Height', 
                'filter_': {
                    'condition': FC_NUMBER_GREATER,
                    'value': 4
                }
            }
        ]
    )

    assert mito.dfs[0].equals(df1)
    assert mito.dfs[1].equals(pd.DataFrame({'Name': ['Nate'], 'Height sum': [5]}))


def test_pivot_with_filter_reaplies ():
    df1 = pd.DataFrame(data={'Name': ['ADR', 'Nate', 'Jake'], 'Height': [4, 5, 6]})
    mito = create_mito_wrapper_dfs(df1)

    pivot_filters = [{
            'column_header': 'Height', 
            'filter_': {
                'condition': FC_NUMBER_GREATER,
                'value': 4
            }
        }
    ]

    mito.pivot_sheet(0, ['Name'], [], {'Height': ['sum']}, pivot_filters=pivot_filters)
    mito.filter(0, 'Height', 'AND', FC_NUMBER_LESS, 6)
    mito.pivot_sheet(0, ['Name'], [], {'Height': ['sum']}, pivot_filters=pivot_filters, destination_sheet_index=1)

    assert mito.dfs[0].equals(pd.DataFrame({'Name': ['ADR', 'Nate'], 'Height': [4,5]}))
    assert mito.dfs[1].equals(pd.DataFrame({'Name': ['Nate'], 'Height sum': [5]}))


PIVOT_FILTER_TESTS: List[Any] = [
    # Filter does not remove rows
    (
        pd.DataFrame(data={'Name': ['Nate', 'Nate'], 'Height': [4, 5]}),
        ['Name'], [], {'Height': ['sum']}, 
        [
            {
                'column_header': 'Name', 
                'filter_': {
                    'condition': FC_STRING_CONTAINS,
                    'value': 'Nate'
                }
            }
        ],
        pd.DataFrame({'Name': ['Nate'], 'Height sum': [9]})
    ),
    # Filter does not remove numbers
    (
        pd.DataFrame(data={'Name': ['Nate', 'Nate'], 'Height': [4, 5]}),
        ['Name'], [], {'Height': ['sum']}, 
        [
            {
                'column_header': 'Height', 
                'filter_': {
                    'condition': FC_NUMBER_LESS,
                    'value': 10
                }
            }
        ],
        pd.DataFrame({'Name': ['Nate'], 'Height sum': [9]})
    ),
    # Filter to half of the dataframe
    (
        pd.DataFrame(data={'Name': ['Nate', 'bork'], 'Height': [4, 5]}),
        ['Name'], [], {'Height': ['sum']}, 
        [
            {
                'column_header': 'Name', 
                'filter_': {
                    'condition': FC_STRING_CONTAINS,
                    'value': 'bork'
                }
            }
        ],
        pd.DataFrame({'Name': ['bork'], 'Height sum': [5]})
    ),
    # Filter work with multiple aggregation methods
    (
        pd.DataFrame(data={'Name': ['Nate', 'bork'], 'Height': [4, 5]}),
        ['Name'], [], {'Height': ['sum', 'max']}, 
        [
            {
                'column_header': 'Name', 
                'filter_': {
                    'condition': FC_STRING_CONTAINS,
                    'value': 'bork'
                }
            }
        ],
        pd.DataFrame({'Name': ['bork'], 'Height max': [5], 'Height sum': [5]})
    ),
    # Filter works on multiple columns of same type, AND is true
    (
        pd.DataFrame(data={'Name': ['Nate', 'Nate'], 'Last': ['Rush', 'Diamond'], 'Height': [4, 5]}),
        ['Name'], [], {'Height': ['sum', 'max']}, 
        [
            {
                'column_header': 'Name', 
                'filter_': {
                    'condition': FC_STRING_CONTAINS,
                    'value': 'Nate'
                }
            },
            {
                'column_header': 'Last', 
                'filter_': {
                    'condition': FC_STRING_CONTAINS,
                    'value': 'Rush'
                }
            },
        ],
        pd.DataFrame({'Name': ['Nate'], 'Height max': [4], 'Height sum': [4]})
    ),
    
    # Filter works on multiple columns with different types, AND is true
    (
        pd.DataFrame(data={'Name': ['Nate', 'Nate'], 'Age': [1, 2], 'Height': [4, 5]}),
        ['Name'], [], {'Height': ['sum', 'max']}, 
        [
            {
                'column_header': 'Name', 
                'filter_': {
                    'condition': FC_STRING_CONTAINS,
                    'value': 'Nate'
                }
            },
            {
                'column_header': 'Age', 
                'filter_': {
                    'condition': FC_NUMBER_EXACTLY,
                    'value': 1
                }
            },
        ],
        pd.DataFrame({'Name': ['Nate'], 'Height max': [4], 'Height sum': [4]})
    ),

    # Filter applied to all pivot table columns
    (
        pd.DataFrame(data={'Name': ['Nate', 'Nate'], 'Last': ['Rush', 'Diamond'], 'Height': [4, 5]}),
        ['Name'], [], {'Height': ['sum', 'max']}, 
        [
            {
                'column_header': 'Name', 
                'filter_': {
                    'condition': FC_STRING_CONTAINS,
                    'value': 'Nate'
                }
            },
            {
                'column_header': 'Height', 
                'filter_': {
                    'condition': FC_NUMBER_EXACTLY,
                    'value': 5
                }
            },
        ],
        pd.DataFrame({'Name': ['Nate'], 'Height max': [5], 'Height sum': [5]})
    ),

    # String condition
    (
        pd.DataFrame(data={'Name': ['Nate', 'Jake'], 'Age': [1, 2], 'Is Cool': [True, False], 'DOB': pd.to_datetime(['1-1-2000', '1-1-1999']), 'Height': [4, 5]}),
        ['Name'], [], {'Height': ['sum', 'max']}, 
        [
            {
                'column_header': 'Name', 
                'filter_': {
                    'condition': FC_STRING_CONTAINS,
                    'value': 'Nate'
                }
            },
        ],
        pd.DataFrame({'Name': ['Nate'], 'Height max': [4], 'Height sum': [4]})
    ),
    # Number condition
    (
        pd.DataFrame(data={'Name': ['Nate', 'Jake'], 'Age': [1, 2], 'Is Cool': [True, False], 'DOB': pd.to_datetime(['1-1-2000', '1-1-1999']), 'Height': [4, 5]}),
        ['Name'], [], {'Height': ['sum', 'max']}, 
        [
            {
                'column_header': 'Age', 
                'filter_': {
                    'condition': FC_NUMBER_EXACTLY,
                    'value': 1
                }
            },
        ],
        pd.DataFrame({'Name': ['Nate'], 'Height max': [4], 'Height sum': [4]})
    ),
    # Boolean condition
    (
        pd.DataFrame(data={'Name': ['Nate', 'Jake'], 'Age': [1, 2], 'Is Cool': [True, False], 'DOB': pd.to_datetime(['1-1-2000', '1-1-1999']), 'Height': [4, 5]}),
        ['Name'], [], {'Height': ['sum', 'max']}, 
        [
            {
                'column_header': 'Is Cool', 
                'filter_': {
                    'condition': FC_BOOLEAN_IS_TRUE,
                    'value': True
                }
            },
        ],
        pd.DataFrame({'Name': ['Nate'], 'Height max': [4], 'Height sum': [4]})
    ),
    # Datetime condition
    (
        pd.DataFrame(data={'Name': ['Nate', 'Jake'], 'Age': [1, 2], 'Is Cool': [True, False], 'DOB': pd.to_datetime(['1-1-2000', '1-1-1999']), 'Height': [4, 5]}),
        ['Name'], [], {'Height': ['sum', 'max']}, 
        [
            {
                'column_header': 'DOB', 
                'filter_': {
                    'condition': FC_DATETIME_EXACTLY,
                    'value': pd.to_datetime('1-1-2000')
                }
            },
        ],
        pd.DataFrame({'Name': ['Nate'], 'Height max': [4], 'Height sum': [4]})
    ),
    # Anything else?
]

# On pre Pandas 1.0 versions, if you filter to _no_ data, we get an error. This is literally 
# almost none of our users, in a flow that is extremly rare, so rather than complicating the 
# pivot code to handle it, we just throw an error, and dont' run this test
PIVOT_FILTER_TESTS_EMPTY: List[Any] = [
    # Filter to nothing
    (
        pd.DataFrame(data={'Name': ['Nate', 'Nate'], 'Height': [4, 5]}),
        ['Name'], [], {'Height': ['sum']}, 
        [
            {
                'column_header': 'Name', 
                'filter_': {
                    'condition': FC_STRING_CONTAINS,
                    'value': 'bork'
                }
            }
        ],
        pd.DataFrame({'Name': []})
    ),
    # Filter works on multiple columns of same type, AND is false
    (
        pd.DataFrame(data={'Name': ['Nate', 'Jake'], 'Last': ['Rush', 'Diamond'], 'Height': [4, 5]}),
        ['Name'], [], {'Height': ['sum', 'max']}, 
        [
            {
                'column_header': 'Name', 
                'filter_': {
                    'condition': FC_STRING_CONTAINS,
                    'value': 'Nate'
                }
            },
            {
                'column_header': 'Last', 
                'filter_': {
                    'condition': FC_STRING_CONTAINS,
                    'value': 'Diamond'
                }
            },
        ],
        pd.DataFrame({'Name': []})
    ),
    # Filter works on multiple columns with different types, AND is false
    (
        pd.DataFrame(data={'Name': ['Nate', 'Jake'], 'Age': [1, 2], 'Height': [4, 5]}),
        ['Name'], [], {'Height': ['sum', 'max']}, 
        [
            {
                'column_header': 'Name', 
                'filter_': {
                    'condition': FC_STRING_CONTAINS,
                    'value': 'Nate'
                }
            },
            {
                'column_header': 'Age', 
                'filter_': {
                    'condition': FC_NUMBER_EXACTLY,
                    'value': 2
                }
            },
        ],
        pd.DataFrame({'Name': []})
    ),
]
if tuple([int(i) for i in pd.__version__.split('.')]) > (1, 0, 0):
    PIVOT_FILTER_TESTS = PIVOT_FILTER_TESTS + PIVOT_FILTER_TESTS_EMPTY

@pytest.mark.parametrize("original_df, pivot_rows, pivot_columns, values, pivot_filters, pivoted_df", PIVOT_FILTER_TESTS)
def test_pivot_filter(original_df, pivot_rows, pivot_columns, values, pivot_filters, pivoted_df):
    mito = create_mito_wrapper_dfs(original_df)
    mito.pivot_sheet(0, pivot_rows, pivot_columns, values, pivot_filters=pivot_filters)

    assert mito.dfs[0].equals(original_df)
    # For some reason, we need to check if dataframes are equal differently if
    # they are empty, due to bugs in pandas .equals
    if len(pivoted_df) > 0:
        assert mito.dfs[1].equals(pivoted_df)
    else:
        assert len(mito.dfs[1]) == 0
        assert mito.dfs[1].columns.to_list() == pivoted_df.columns.to_list() 