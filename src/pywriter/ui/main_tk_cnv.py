#!/usr/bin/env python3
""""Provide a tkinter GUI base class for converter applications.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
from pywriter.ui.main_tk import MainTk
from pywriter.yw.yw7_file import Yw7File


class MainTkCnv(MainTk):
    """A tkinter GUI base class for yWriter file conversion.

    Public methods:
        open_project(fileName) -- select a valid project file and display the path.

    Public instance variables:
        converter -- converter strategy class.

    Adds a "Swap" and a "Run" entry to the main menu.
    """    
    _EXPORT_DESC = 'Export from yWriter.'
    _IMPORT_DESC = 'Import to yWriter.'

    def __init__(self, title, **kwargs):
        """Initialize instance variables.
        
        Positional arguments:
            title -- application title to be displayed at the window frame.
                    
        Required keyword arguments:
            yw_last_open -- initial file.
            file_types -- list of tuples for file selection (display text, extension).
        
        Extends the superclass constructor.
        """
        super().__init__(title, **kwargs)
        self.converter = None
        self._sourcePath = None
        self._ywExtension = Yw7File.EXTENSION
        self._docExtension = None

    def _extend_menu(self):
        """Add main menu entries.
        
        Overrides the superclass template method. 
        """
        self._mainMenu.add_command(label='Swap', command=self._reverse_direction)
        self._mainMenu.entryconfig('Swap', state='disabled')
        self._mainMenu.add_command(label='Run', command=self._convert_file)
        self._mainMenu.entryconfig('Run', state='disabled')

    def _disable_menu(self):
        """Disable menu entries when no project is open.
        
        Extends the superclass method.      
        """
        super()._disable_menu()
        self._mainMenu.entryconfig('Run', state='disabled')
        self._mainMenu.entryconfig('Swap', state='disabled')

    def _enable_menu(self):
        """Enable menu entries when a project is open.
        
        Extends the superclass method.
        """
        super()._enable_menu()
        self._mainMenu.entryconfig('Run', state='normal')
        self._mainMenu.entryconfig('Swap', state='normal')

    def open_project(self, fileName):
        """Create a source object instance and read the file.
        
        Positional arguments:
            fileName -- str: project file path.
            
        Return the file name.
        Extends the superclass method.
        """
        fileName = super().open_project(fileName, fileTypes=self.kwargs['file_types'])
        if not fileName:
            return ''
        self._sourcePath = fileName
        self._enable_menu()
        if fileName.endswith(self._ywExtension):
            self._titleBar.config(text=self._EXPORT_DESC)
        elif fileName.endswith(self._docExtension):
            self._titleBar.config(text=self._IMPORT_DESC)
        return fileName

    def _reverse_direction(self):
        """Swap source and target file names."""
        fileName, fileExtension = os.path.splitext(self._sourcePath)
        if fileExtension == self._ywExtension:
            self._sourcePath = f'{fileName}{self._docExtension}'
            self._pathBar.config(text=os.path.normpath(self._sourcePath))
            self._titleBar.config(text=self._IMPORT_DESC)
            self._set_status('')
        elif fileExtension == self._docExtension:
            self._sourcePath = f'{fileName}{self._ywExtension}'
            self._pathBar.config(text=os.path.normpath(self._sourcePath))
            self._titleBar.config(text=self._EXPORT_DESC)
            self._set_status('')

    def _convert_file(self):
        """Call the converter's conversion method, if a source file is selected."""
        self._set_status('')
        self.kwargs['yw_last_open'] =self._sourcePath
        self.converter.run(self._sourcePath, **self.kwargs)

