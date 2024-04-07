"""Provide a converter class for Aeon 3 Timeline import.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/aeon3md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.converter.yw_cnv_ff import YwCnvFf
from aeon3ywlib.csv_timeline3 import CsvTimeline3
from aeon3ywlib.json_timeline3 import JsonTimeline3
from aeon3mdlib.md_outline import MdOutline
from aeon3mdlib.md_full_synopsis import MdFullSynopsis
from aeon3mdlib.md_brief_synopsis import MdBrieflSynopsis
from aeon3mdlib.md_chapter_overview import MdChapterOverview
from aeon3mdlib.md_character_sheets import MdCharacterSheets
from aeon3mdlib.md_location_sheets import MdLocationSheets
from aeon3mdlib.md_report import MdReport


class Aeon3mdConverter(YwCnvFf):
    """A converter for universal export from a yWriter 7 project.

    Overrides the superclass constants EXPORT_SOURCE_CLASSES,
    EXPORT_TARGET_CLASSES.
    """
    EXPORT_SOURCE_CLASSES = [
        CsvTimeline3,
        JsonTimeline3
        ]
    EXPORT_TARGET_CLASSES = [
        MdOutline,
        MdFullSynopsis,
        MdBrieflSynopsis,
        MdChapterOverview,
        MdCharacterSheets,
        MdLocationSheets,
        MdReport,
        ]
