#!/usr/bin/python3
"""Convert Aeon Timeline 3 project data to Markdown. 

usage: aeon3md_.py [-h] [--silent] Sourcefile Suffix

positional arguments:
  Sourcefile  The path of the .aeon or .csv file.
  Suffix      The suffix of the output file, indicating the content:  
              _full_synopsis - Part and chapter titles and scene summaries. 
              _brief_synopsis - Part and chapter titles and scene titles.
              _chapter_overview - Part and chapter titles.
              _character_sheets - Character tags, summary, characteristics, traits, and notes.
              _location_sheets - Location tags and summaries. 
              _report - A full description of the narrative part, the characters and the locations.

optional arguments:
  -h, --help  show this help message and exit
  --silent    suppress error messages and the request to confirm overwriting


Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/aeon3md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import argparse
from argparse import RawTextHelpFormatter
import os
from pywriter.ui.ui import Ui
from pywriter.ui.ui_cmd import UiCmd
from pywriter.config.configuration import Configuration
from aeon3mdlib.aeon3md_converter import Aeon3mdConverter

SETTINGS = dict(
    part_number_prefix='Part',
    chapter_number_prefix='Chapter',
    type_event='Event',
    type_character='Character',
    type_location='Location',
    type_item='Item',
    character_label='Participant',
    location_label='Location',
    item_label='Item',
    part_desc_label='Label',
    chapter_desc_label='Label',
    scene_desc_label='Summary',
    scene_title_label='Label',
    notes_label='Notes',
    tag_label='Tags',
    viewpoint_label='Viewpoint',
    character_bio_label='Summary',
    character_aka_label='Nickname',
    character_desc_label1='Characteristics',
    character_desc_label2='Traits',
    character_desc_label3='',
    location_desc_label='Summary',
)


def main(sourcePath, suffix='', silent=True, installDir=''):
    converter = Aeon3mdConverter()
    if silent:
        converter.ui = Ui('')
    else:
        converter.ui = UiCmd('Convert Aeon Timeline 3 project data to Markdown.')
    iniFileName = 'aeon3yw.ini'
    sourceDir = os.path.dirname(sourcePath)
    if not sourceDir:
        sourceDir = './'
    else:
        sourceDir += '/'
    iniFiles = [f'{installDir}{iniFileName}', f'{sourceDir}{iniFileName}']
    configuration = Configuration(SETTINGS)
    for iniFile in iniFiles:
        configuration.read(iniFile)
    kwargs = {'suffix': suffix}
    kwargs.update(configuration.settings)
    kwargs.update(configuration.options)
    converter.run(sourcePath, **kwargs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Convert Aeon Timeline 3 project data to Markdown.',
        epilog='', formatter_class=RawTextHelpFormatter)
    parser.add_argument('sourcePath', metavar='Sourcefile',
                        help='The path of the .aeon or .csv file.')
    parser.add_argument('suffix', metavar='Suffix',
                        help='''The suffix of the output file, indicating the content:                       
_full_synopsis - Part and chapter titles and scene summaries. 
_brief_synopsis - Part and chapter titles and scene titles.
_chapter_overview - Part and chapter titles.
_character_sheets - Character tags, summary, characteristics, traits, and notes.
_location_sheets - Location tags and summaries. 
_report - A full description of the narrative part, the characters and the locations.''')
    parser.add_argument('--silent',
                        action="store_true",
                        help='suppress error messages and the request to confirm overwriting')
    args = parser.parse_args()
    main(args.sourcePath, args.suffix, args.silent)

