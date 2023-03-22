"""Provide a class for Markdown character descriptions export.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/aeon3md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from aeon3mdlib.md_aeon import MdAeon


class MdCharacterSheets(MdAeon):
    """Markdown character descriptions file representation.

    Export a character sheet.
    """
    DESCRIPTION = 'Character sheets'
    SUFFIX = '_character_sheets'

    _characterTemplate = '''## $Title$FullName$AKA

**$Tags**


$Bio


$Goals


$Desc


$Notes

'''
