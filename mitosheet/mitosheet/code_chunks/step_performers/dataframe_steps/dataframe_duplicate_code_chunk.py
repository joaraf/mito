#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Saga Inc.
# Distributed under the terms of the GPL License.

from typing import Any, Dict, List, Optional

from mitosheet.code_chunks.code_chunk import CodeChunk
from mitosheet.state import State


class DataframeDuplicateCodeChunk(CodeChunk):

    def __init__(self, prev_state: State, post_state: State, params: Dict[str, Any], execution_data: Optional[Dict[str, Any]]):
        super().__init__(prev_state, post_state, params, execution_data)
        self.sheet_index = params['sheet_index']

        self.old_df_name = self.post_state.df_names[self.sheet_index]
        self.new_df_name = self.post_state.df_names[len(self.post_state.dfs) - 1]

    def get_display_name(self) -> str:
        return 'Duplicated Dataframe'
    
    def get_description_comment(self) -> str:
        return f'Duplicated {self.old_df_name}'

    def get_code(self) -> List[str]:
        return [f'{self.new_df_name} = {self.old_df_name}.copy(deep=True)']

    def get_created_sheet_indexes(self) -> List[int]:
        return [len(self.post_state.dfs) - 1]