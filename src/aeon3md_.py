"""Convert Aeon Timeline 3 project data to Markdown. 

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/aeon3md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import sys
import os
from pywriter.ui.ui import Ui
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


def run(sourcePath, suffix='', installDir=''):
    ui = Ui('')
    converter = Aeon3mdConverter()
    converter.ui = ui
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
    run(sys.argv[1], sys.argv[2], '')
