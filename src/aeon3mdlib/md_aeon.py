"""Provide a base class for Markdown export from Aeon Timeline 3.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/aeon3md
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.file.file_export import FileExport


class MdAeon(FileExport):
    """Markdown Aeon Timeline import file representation.
    """
    EXTENSION = '.md'

    def _get_characterMapping(self, crId):
        """Return a mapping dictionary for a character section. 
        
        Positional arguments:
            crId -- str: character ID.
        
        Extends the superclass method.
        """
        characterMapping = super()._get_characterMapping(crId)
        if self.characters[crId].aka:
            characterMapping['AKA'] = f' ("{self.characters[crId].aka}")'
        if self.characters[crId].fullName and self.characters[crId].fullName != self.characters[crId].title:
            characterMapping['FullName'] = f'/{self.characters[crId].fullName}'
        else:
            characterMapping['FullName'] = ''
        return characterMapping

    def _get_locationMapping(self, lcId):
        """Return a mapping dictionary for a location section. 
        
        Positional arguments:
            lcId -- str: location ID.

        Extends the superclass method.
        """
        locationMapping = super().get_locationMapping(lcId)
        if self.locations[lcId].aka:
            locationMapping['AKA'] = f' ("{self.locations[lcId].aka}")'
        return locationMapping
