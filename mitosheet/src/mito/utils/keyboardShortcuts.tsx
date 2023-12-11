import { ActionEnum, KeyboardShorcut } from "../types"
import { Actions } from "./actions"

/**
 * A list of all keyboard shortcuts in the app.
 */
export const keyboardShortcuts: KeyboardShorcut[] = [
    {
        macKeyCombo: {
            metaKey: true,
            keys: ['c']
        },
        winKeyCombo: {
            ctrlKey: true,
            keys: ['c']
        },
        action: ActionEnum.Copy
    },
    {
        macKeyCombo: {
            metaKey: true,
            keys: ['f']
        },
        winKeyCombo: {
            ctrlKey: true,
            keys: ['f']
        },
        preventDefaultAndStopPropagation: true,
        jupyterLabCommand: 'mitosheet:open-search',
        action: ActionEnum.OpenSearch
    },
    {
        macKeyCombo: {
            metaKey: true,
            keys: ['z']
        },
        winKeyCombo: {
            ctrlKey: true,
            keys: ['z']
        },
        preventDefaultAndStopPropagation: true,
        jupyterLabCommand: 'mitosheet:mito-undo',
        action: ActionEnum.Undo
    },
    {
        macKeyCombo: {
            metaKey: true,
            keys: ['y']
        },
        winKeyCombo: {
            ctrlKey: true,
            keys: ['y']
        },
        preventDefaultAndStopPropagation: true,
        action: ActionEnum.Redo
    },
    {
        macKeyCombo: {
            ctrlKey: true,
            keys: [' ']
        },
        winKeyCombo: {
            ctrlKey: true,
            keys: [' ']
        },
        action: ActionEnum.Select_Columns
    },
    {
        macKeyCombo: {
            shiftKey: true,
            keys: [' ']
        },
        winKeyCombo: {
            shiftKey: true,
            keys: [' ']
        },
        preventDefaultAndStopPropagation: true,
        action: ActionEnum.Select_Rows
    },
    {
        macKeyCombo: {
            metaKey: true,
            keys: ['a']
        },
        winKeyCombo: {
            ctrlKey: true,
            keys: ['a']
        },
        preventDefaultAndStopPropagation: true,
        action: ActionEnum.Select_All
    }
]

/**
 * Handles keyboard shortcuts. If a keyboard shortcut is pressed, the corresponding action is executed.
 * @param e The keyboard event.
 * @param actions The actions object.
 */
export const handleKeyboardShortcuts = (e: React.KeyboardEvent, actions: Actions) => {
    const operatingSystem = window.navigator.userAgent.toUpperCase().includes('MAC')
        ? 'mac'
        : 'windows'

    const shortcut = keyboardShortcuts.find(shortcut => {
        const keyCombo = operatingSystem === 'mac' ? shortcut.macKeyCombo : shortcut.winKeyCombo
        // If the special key combination doesn't match, return false.
        if (!!e.metaKey !== !!keyCombo.metaKey ||
            !!e.ctrlKey !== !!keyCombo.ctrlKey ||
            !!e.shiftKey !== !!keyCombo.shiftKey ||
            !!e.altKey !== !!keyCombo.altKey) {
            return false;
        }
        // If the special keys matched, check if the key is the same.
        return keyCombo.keys.includes(e.key);
    })
    
    if (shortcut !== undefined) {
        actions.buildTimeActions[shortcut.action].actionFunction()
        if (shortcut.preventDefaultAndStopPropagation) {
            e.preventDefault();
            e.stopPropagation();
        }
    }
}
