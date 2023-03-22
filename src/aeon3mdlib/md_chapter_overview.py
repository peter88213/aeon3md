"""Provide a class for Markdown part descriptions export.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/aeon3md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from aeon3mdlib.md_aeon import MdAeon


class MdChapterOverview(MdAeon):
    """Markdown part and chapter summaries file representation.

    Export a very brief synopsis.
    """
    DESCRIPTION = 'Chapter overview'
    SUFFIX = '_chapter_overview'

    _partTemplate = '''# $Desc

'''

    _chapterTemplate = '''$Desc
    
'''
