#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Saga Inc.
# Distributed under the terms of the GPL License.
"""
After reading in the arguments passed to the frontend,
this update figures out which of them were dataframes
and which of them were file paths, and updates the 
df names in the steps properly.
"""

from mitosheet.types import CodeOptions, StepsManagerType
from mitosheet.utils import get_valid_python_identifier

CODE_OPTIONS_UPDATE_EVENT = 'code_options_update'
CODE_OPTIONS_UPDATE_PARAMS = ['code_options']

def execute_args_update(
        steps_manager: StepsManagerType,
        code_options: CodeOptions
    ) -> None:

    # Get the valid function names
    valid_function_name = get_valid_python_identifier(code_options['function_name'], 'function', 'func_')
    final_code_options = code_options.copy()
    final_code_options['function_name'] = valid_function_name

    steps_manager.code_options = final_code_options

CODE_OPTIONS_UPDATE = {
    'event_type': CODE_OPTIONS_UPDATE_EVENT,
    'params': CODE_OPTIONS_UPDATE_PARAMS,
    'execute': execute_args_update
}