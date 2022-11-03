import codecs
import json
from glob import glob
import os
from unicodedata import lookup

from mac2winKeyboard import process_input_keylayout, make_keyboard_name, make_klc_filename, make_klc_data, \
    error_msg_winmac_mismatch, char_description
from klc_data import (
    win_to_mac_keycodes, win_keycodes,
    klc_keynames, klc_prologue_dummy, klc_epilogue_dummy
)
from locale_data import (
    locale_id, locale_id_long, locale_tag, locale_name, locale_name_long,
)
from tqdm import tqdm
from mac2winKeyboard import (
    error_msg_macwin_mismatch
)

win_kc2key_code = {
    # Row 0
    # Esc, F1-12 keys are not translated:
    # Row 1:
    # Backspace is not translated
    'OEM_3': 'Backquote',
    '1': 'Digit1',
    '2': 'Digit2',
    '3': 'Digit3',
    '4': 'Digit4',
    '5': 'Digit5',
    '6': 'Digit6',
    '7': 'Digit7',
    '8': 'Digit8',
    '9': 'Digit9',
    '0': 'Digit0',
    'OEM_MINUS': 'Minus',
    'OEM_PLUS': 'Equal',

    # Row 2: Backslash is not translated
    'Q': 'KeyQ',
    'W': 'KeyW',
    'E': 'KeyE',
    'R': 'KeyR',
    'T': 'KeyT',
    'Y': 'KeyY',
    'U': 'KeyU',
    'I': 'KeyI',
    'O': 'KeyO',
    'P': 'KeyP',
    'OEM_4': 'BracketLeft',
    'OEM_6': 'BracketRight',
    'OEM_5': 'Backslash',

    # Row 3:
    'A': 'KeyA',
    'S': 'KeyS',
    'D': 'KeyD',
    'F': 'KeyF',
    'G': 'KeyG',
    'H': 'KeyH',
    'J': 'KeyJ',
    'K': 'KeyK',
    'L': 'KeyL',
    'OEM_1': 'Semicolon',
    'OEM_7': 'Quote',

    # Row 4:
    'Z': 'KeyZ',
    'X': 'KeyX',
    'C': 'KeyC',
    'V': 'KeyV',
    'B': 'KeyB',
    'N': 'KeyN',
    'M': 'KeyM',
    'OEM_COMMA': 'Comma',
    'OEM_PERIOD': 'Period',
    'OEM_2': 'Slash'
}


def convert_to_unicode(string):
    if string == '<none>':
        return ''
    else:
        try:
            return lookup(string)
        except KeyError:
            return string.replace('PUA ', '')

failed_layouts = []
for keylayout in tqdm(glob('keylayout/*/*.keylayout')):
    try:
        keyboard_data = process_input_keylayout(keylayout)
        keyboard_name = make_keyboard_name(keylayout)

        translation_json = {}
        for win_kc_hex, win_kc_name in sorted(win_keycodes.items()):
            win_kc_int = int(win_kc_hex, 16)

            if win_kc_int not in win_to_mac_keycodes:
                print(error_msg_macwin_mismatch.format(
                    win_kc_int, win_keycodes[win_kc_hex]))
                continue

            mac_kc = win_to_mac_keycodes[win_kc_int]
            if mac_kc not in keyboard_data.output_dict:
                print(error_msg_winmac_mismatch.format(
                    win_kc_int, win_keycodes[win_kc_hex], mac_kc))
                continue
            if win_kc_name not in win_kc2key_code:
                continue
            keycode = win_kc2key_code[win_kc_name]
            outputs = keyboard_data.output_dict[mac_kc]

            default_output = keyboard_data.get_key_output(outputs, 'default')
            shift_output = keyboard_data.get_key_output(outputs, 'shift')
            translation_json[keycode] = {
                'lower': convert_to_unicode(char_description(default_output)),
                'upper': convert_to_unicode(char_description(shift_output))
            }
        with open(f'json/{keyboard_name}.json', 'w') as f:
            json.dump(translation_json, f, ensure_ascii=False, indent=4)

        # klc_filename = make_klc_filename(keyboard_name)
        # klc_data = make_klc_data(keyboard_name, keyboard_data)
        #
        # output_path = os.sep.join(('klc', klc_filename))
        # with codecs.open(output_path, 'w', 'utf-16') as output_file:
        #     for line in klc_data:
        #         output_file.write(line)
        #         output_file.write(os.linesep)
        #
        # print(f'{keyboard_name} written to {klc_filename}')
    except Exception as e:
        print(f'Error processing {keylayout}: {e}')
        failed_layouts.append(keylayout)

print(f'Failed layouts: {failed_layouts}')
