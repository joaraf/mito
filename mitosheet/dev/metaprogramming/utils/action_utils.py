




from typing import Dict

from metaprogramming.utils.code_utils import (CLOSE_BRACKET, OPEN_BRACKET,
                                              add_enum_value, name_to_enum_key)
from metaprogramming.utils.path_utils import get_src_folder

ACTIONENUM_MARKER = "// AUTOGENERATED LINE: ACTIONENUM (DO NOT DELETE)"
ACTION_MARKER = "// AUTOGENERATED LINE: ACTION (DO NOT DELETE)"


def get_action_code(action_name: str, enum_name: str, create_taskpane: bool) -> str:

    taskpane_type = name_to_enum_key(action_name)
    if create_taskpane:
        action_function_code = f"""// We turn off editing mode, if it is on
                setEditorState(undefined);

                setUIState(prevUIState => {OPEN_BRACKET}
                    return {OPEN_BRACKET}
                        ...prevUIState,
                        currOpenTaskpane: {OPEN_BRACKET}type: TaskpaneType.{taskpane_type}{CLOSE_BRACKET},
                        selectedTabType: 'data'
                    {CLOSE_BRACKET}
                {CLOSE_BRACKET})"""
    else:
        action_function_code = f"""// TODO"""

    return f"""[ActionEnum.{enum_name}]: {OPEN_BRACKET}
            type: ActionEnum.{enum_name},
            shortTitle: '{action_name}',
            longTitle: '{action_name}',
            actionFunction: () => {OPEN_BRACKET}
                {action_function_code}
            {CLOSE_BRACKET},
            isDisabled: () => {OPEN_BRACKET}return undefined{CLOSE_BRACKET}, // TODO
            searchTerms: ['{action_name}'],
            tooltip: "{action_name}"
        {CLOSE_BRACKET},
        {ACTION_MARKER}
    """

def write_to_actions_file(action_name: str, create_taskpane: bool) -> None:
    path_to_types = get_src_folder() / 'types.tsx'
    path_to_actions = get_src_folder() / 'utils' / 'actions.tsx'

    enum_name = name_to_enum_key(action_name)
    enum_value = action_name.replace(' ', '_')

    # First, write the enum
    add_enum_value(path_to_types, ACTIONENUM_MARKER, enum_name, enum_value)

    # Then, add a filler for the action
    with open(path_to_actions, 'r') as f:
        code = f.read()
        code = code.replace(ACTION_MARKER, get_action_code(action_name, enum_name, create_taskpane))

    with open(path_to_actions, 'w') as f:
        f.write(code)
