"""Provide a class for Markdown scene descriptions export.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/aeon3md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from aeon3mdlib.md_aeon import MdAeon


class MdOutline(MdAeon):
    """Markdown scene summaries file representation.

    Export a full synopsis.
    """
    DESCRIPTION = 'Outline'
    SUFFIX = '_outline'

    _partTemplate = '''# $Title
    
'''

    _chapterTemplate = '''## $Title
    
'''

    _sceneTemplate = '''<!--- $Title --->

$Desc

'''

    _sceneDivider = '''* * *

'''
