#!/usr/bin/python3
"""Convert Aeon Timeline 3 project data to Markdown. 

usage: aeon3md.py [-h] [--silent] Sourcefile Suffix

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
ERROR = '!'
import sys


class Ui:
    """Base class for UI facades, implementing a 'silent mode'.
    
    Public methods:
        ask_yes_no(text) -- return True or False.
        set_info_what(message) -- show what the converter is going to do.
        set_info_how(message) -- show how the converter is doing.
        start() -- launch the GUI, if any.
        
    Public instance variables:
        infoWhatText -- buffer for general messages.
        infoHowText -- buffer for error/success messages.
    """

    def __init__(self, title):
        """Initialize text buffers for messaging.
        
        Positional arguments:
            title -- application title.
        """
        self.infoWhatText = ''
        self.infoHowText = ''

    def ask_yes_no(self, text):
        """Return True or False.
        
        Positional arguments:
            text -- question to be asked. 
            
        This is a stub used for "silent mode".
        The application may use a subclass for confirmation requests.    
        """
        return True

    def set_info_what(self, message):
        """Show what the converter is going to do.
        
        Positional arguments:
            message -- message to be buffered. 
        """
        self.infoWhatText = message

    def set_info_how(self, message):
        """Show how the converter is doing.
        
        Positional arguments:
            message -- message to be buffered.
            
        Print the message to stderr, replacing the error marker, if any.
        """
        if message.startswith(ERROR):
            message = f'FAIL: {message.split(ERROR, maxsplit=1)[1].strip()}'
            sys.stderr.write(message)
        self.infoHowText = message

    def start(self):
        """Launch the GUI, if any.
        
        To be overridden by subclasses requiring
        special action to launch the user interaction.
        """


class UiCmd(Ui):
    """Ui subclass implementing a console interface.
    
    Public methods:
        ask_yes_no(text) -- query yes or no at the console.
        set_info_what(message) -- show what the converter is going to do.
        set_info_how(message) -- show how the converter is doing.
    """

    def __init__(self, title):
        """Print the title.
        
        Positional arguments:
            title -- application title to be displayed at the console.
        
        Extends the superclass constructor.
        """
        super().__init__(title)
        print(title)

    def ask_yes_no(self, text):
        """Query yes or no at the console.
        
        Positional arguments:
            text -- question to be asked at the console. 
            
        Overrides the superclass method.       
        """
        result = input(f'WARNING: {text} (y/n)')
        if result.lower() == 'y':
            return True
        else:
            return False

    def set_info_what(self, message):
        """Show what the converter is going to do.
        
        Positional arguments:
            message -- message to be printed at the console. 
            
        Print the message.
        Overrides the superclass method.
        """
        print(message)

    def set_info_how(self, message):
        """Show how the converter is doing.

        Positional arguments:
            message -- message to be printed at the console. 
            
        Print the message, replacing the error marker, if any.
        Overrides the superclass method.
        """
        if message.startswith(ERROR):
            message = f'FAIL: {message.split(ERROR, maxsplit=1)[1].strip()}'
        self.infoHowText = message
        print(message)
from configparser import ConfigParser


class Configuration:
    """Application configuration, representing an INI file.

        INI file sections:
        <self._sLabel> - Strings
        <self._oLabel> - Boolean values

    Public methods:
        set(settings={}, options={}) -- set the entire configuration without writing the INI file.
        read(iniFile) -- read a configuration file.
        write(iniFile) -- save the configuration to iniFile.

    Public instance variables:    
        settings - dictionary of strings
        options - dictionary of boolean values
    """

    def __init__(self, settings={}, options={}):
        """Initalize attribute variables.

        Optional arguments:
            settings -- default settings (dictionary of strings)
            options -- default options (dictionary of boolean values)
        """
        self.settings = None
        self.options = None
        self._sLabel = 'SETTINGS'
        self._oLabel = 'OPTIONS'
        self.set(settings, options)

    def set(self, settings=None, options=None):
        """Set the entire configuration without writing the INI file.

        Optional arguments:
            settings -- new settings (dictionary of strings)
            options -- new options (dictionary of boolean values)
        """
        if settings is not None:
            self.settings = settings.copy()
        if options is not None:
            self.options = options.copy()

    def read(self, iniFile):
        """Read a configuration file.
        
        Positional arguments:
            iniFile -- str: path configuration file path.
            
        Settings and options that can not be read in, remain unchanged.
        """
        config = ConfigParser()
        config.read(iniFile, encoding='utf-8')
        if config.has_section(self._sLabel):
            section = config[self._sLabel]
            for setting in self.settings:
                fallback = self.settings[setting]
                self.settings[setting] = section.get(setting, fallback)
        if config.has_section(self._oLabel):
            section = config[self._oLabel]
            for option in self.options:
                fallback = self.options[option]
                self.options[option] = section.getboolean(option, fallback)

    def write(self, iniFile):
        """Save the configuration to iniFile.

        Positional arguments:
            iniFile -- str: path configuration file path.
        """
        config = ConfigParser()
        if self.settings:
            config.add_section(self._sLabel)
            for settingId in self.settings:
                config.set(self._sLabel, settingId, str(self.settings[settingId]))
        if self.options:
            config.add_section(self._oLabel)
            for settingId in self.options:
                if self.options[settingId]:
                    config.set(self._oLabel, settingId, 'Yes')
                else:
                    config.set(self._oLabel, settingId, 'No')
        with open(iniFile, 'w', encoding='utf-8') as f:
            config.write(f)
import webbrowser


class YwCnv:
    """Base class for Novel file conversion.

    Public methods:
        convert(sourceFile, targetFile) -- Convert sourceFile into targetFile.
    """

    def convert(self, source, target):
        """Convert source into target and return a message.

        Positional arguments:
            source, target -- Novel subclass instances.

        Operation:
        1. Make the source object read the source file.
        2. Make the target object merge the source object's instance variables.
        3. Make the target object write the target file.
        Return a message beginning with the ERROR constant in case of error.

        Error handling:
        - Check if source and target are correctly initialized.
        - Ask for permission to overwrite target.
        - Pass the error messages of the called methods of source and target.
        - The success message comes from target.write(), if called.       
        """
        if source.filePath is None:
            return f'{ERROR}Source "{os.path.normpath(source.filePath)}" is not of the supported type.'

        if not os.path.isfile(source.filePath):
            return f'{ERROR}"{os.path.normpath(source.filePath)}" not found.'

        if target.filePath is None:
            return f'{ERROR}Target "{os.path.normpath(target.filePath)}" is not of the supported type.'

        if os.path.isfile(target.filePath) and not self._confirm_overwrite(target.filePath):
            return f'{ERROR}Action canceled by user.'

        message = source.read()
        if message.startswith(ERROR):
            return message

        message = target.merge(source)
        if message.startswith(ERROR):
            return message

        return target.write()

    def _confirm_overwrite(self, fileName):
        """Return boolean permission to overwrite the target file.
        
        Positional argument:
            fileName -- path to the target file.
        
        This is a stub to be overridden by subclass methods.
        """
        return True


class YwCnvUi(YwCnv):
    """Base class for Novel file conversion with user interface.

    Public methods:
        export_from_yw(sourceFile, targetFile) -- Convert from yWriter project to other file format.
        create_yw(sourceFile, targetFile) -- Create target from source.
        import_to_yw(sourceFile, targetFile) -- Convert from any file format to yWriter project.

    Instance variables:
        ui -- Ui (can be overridden e.g. by subclasses).
        newFile -- str: path to the target file in case of success.   
    """

    def __init__(self):
        """Define instance variables."""
        self.ui = Ui('')
        # Per default, 'silent mode' is active.
        self.newFile = None
        # Also indicates successful conversion.

    def export_from_yw(self, source, target):
        """Convert from yWriter project to other file format.

        Positional arguments:
            source -- YwFile subclass instance.
            target -- Any Novel subclass instance.

        Operation:
        1. Send specific information about the conversion to the UI.
        2. Convert source into target.
        3. Pass the message to the UI.
        4. Save the new file pathname.

        Error handling:
        - If the conversion fails, newFile is set to None.
        """
        self.ui.set_info_what(
            f'Input: {source.DESCRIPTION} "{os.path.normpath(source.filePath)}"\nOutput: {target.DESCRIPTION} "{os.path.normpath(target.filePath)}"')
        message = self.convert(source, target)
        self.ui.set_info_how(message)
        if message.startswith(ERROR):
            self.newFile = None
        else:
            self.newFile = target.filePath

    def create_yw7(self, source, target):
        """Create target from source.

        Positional arguments:
            source -- Any Novel subclass instance.
            target -- YwFile subclass instance.

        Operation:
        1. Send specific information about the conversion to the UI.
        2. Convert source into target.
        3. Pass the message to the UI.
        4. Save the new file pathname.

        Error handling:
        - Tf target already exists as a file, the conversion is cancelled,
          an error message is sent to the UI.
        - If the conversion fails, newFile is set to None.
        """
        self.ui.set_info_what(
            f'Create a yWriter project file from {source.DESCRIPTION}\nNew project: "{os.path.normpath(target.filePath)}"')
        if os.path.isfile(target.filePath):
            self.ui.set_info_how(f'{ERROR}"{os.path.normpath(target.filePath)}" already exists.')
        else:
            message = self.convert(source, target)
            self.ui.set_info_how(message)
            if message.startswith(ERROR):
                self.newFile = None
            else:
                self.newFile = target.filePath

    def import_to_yw(self, source, target):
        """Convert from any file format to yWriter project.

        Positional arguments:
            source -- Any Novel subclass instance.
            target -- YwFile subclass instance.

        Operation:
        1. Send specific information about the conversion to the UI.
        2. Convert source into target.
        3. Pass the message to the UI.
        4. Delete the temporay file, if exists.
        5. Save the new file pathname.

        Error handling:
        - If the conversion fails, newFile is set to None.
        """
        self.ui.set_info_what(
            f'Input: {source.DESCRIPTION} "{os.path.normpath(source.filePath)}"\nOutput: {target.DESCRIPTION} "{os.path.normpath(target.filePath)}"')
        message = self.convert(source, target)
        self.ui.set_info_how(message)
        self._delete_tempfile(source.filePath)
        if message.startswith(ERROR):
            self.newFile = None
        else:
            self.newFile = target.filePath

    def _confirm_overwrite(self, filePath):
        """Return boolean permission to overwrite the target file.
        
        Positional arguments:
            fileName -- path to the target file.
        
        Overrides the superclass method.
        """
        return self.ui.ask_yes_no(f'Overwrite existing file "{os.path.normpath(filePath)}"?')

    def _delete_tempfile(self, filePath):
        """Delete filePath if it is a temporary file no longer needed."""
        if filePath.endswith('.html'):
            # Might it be a temporary text document?
            if os.path.isfile(filePath.replace('.html', '.odt')):
                # Does a corresponding Office document exist?
                try:
                    os.remove(filePath)
                except:
                    pass
        elif filePath.endswith('.csv'):
            # Might it be a temporary spreadsheet document?
            if os.path.isfile(filePath.replace('.csv', '.ods')):
                # Does a corresponding Office document exist?
                try:
                    os.remove(filePath)
                except:
                    pass

    def _open_newFile(self):
        """Open the converted file for editing and exit the converter script."""
        webbrowser.open(self.newFile)
        sys.exit(0)


class FileFactory:
    """Base class for conversion object factory classes.
    """

    def __init__(self, fileClasses=[]):
        """Write the parameter to a "private" instance variable.

        Optional arguments:
            _fileClasses -- list of classes from which an instance can be returned.
        """
        self._fileClasses = fileClasses


class ExportSourceFactory(FileFactory):
    """A factory class that instantiates a yWriter object to read.

    Public methods:
        make_file_objects(self, sourcePath, **kwargs) -- return conversion objects.
    """

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a source object for conversion from a yWriter project.

        Positional arguments:
            sourcePath -- str: path to the source file to convert.

        Return a tuple with three elements:
        - A message beginning with the ERROR constant in case of error
        - sourceFile: a YwFile subclass instance, or None in case of error
        - targetFile: None
        """
        __, fileExtension = os.path.splitext(sourcePath)
        for fileClass in self._fileClasses:
            if fileClass.EXTENSION == fileExtension:
                sourceFile = fileClass(sourcePath, **kwargs)
                return 'Source object created.', sourceFile, None
            
        return f'{ERROR}File type of "{os.path.normpath(sourcePath)}" not supported.', None, None


class ExportTargetFactory(FileFactory):
    """A factory class that instantiates a document object to write.

    Public methods:
        make_file_objects(self, sourcePath, **kwargs) -- return conversion objects.
    """

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a target object for conversion from a yWriter project.

        Positional arguments:
            sourcePath -- str: path to the source file to convert.

        Optional arguments:
            suffix -- str: an indicator for the target file type.

        Required keyword arguments: 
            suffix -- str: target file name suffix.

        Return a tuple with three elements:
        - A message beginning with the ERROR constant in case of error
        - sourceFile: None
        - targetFile: a FileExport subclass instance, or None in case of error 
        """
        fileName, __ = os.path.splitext(sourcePath)
        suffix = kwargs['suffix']
        for fileClass in self._fileClasses:
            if fileClass.SUFFIX == suffix:
                if suffix is None:
                    suffix = ''
                targetFile = fileClass(f'{fileName}{suffix}{fileClass.EXTENSION}', **kwargs)
                return 'Target object created.', None, targetFile
        
        return f'{ERROR}File type of "{os.path.normpath(sourcePath)}" not supported.', None, None


class ImportSourceFactory(FileFactory):
    """A factory class that instantiates a documente object to read.

    Public methods:
        make_file_objects(self, sourcePath, **kwargs) -- return conversion objects.
    """

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a source object for conversion to a yWriter project.       

        Positional arguments:
            sourcePath -- str: path to the source file to convert.

        Return a tuple with three elements:
        - A message beginning with the ERROR constant in case of error
        - sourceFile: a Novel subclass instance, or None in case of error
        - targetFile: None
        """
        for fileClass in self._fileClasses:
            if fileClass.SUFFIX is not None:
                if sourcePath.endswith(f'{fileClass.SUFFIX }{fileClass.EXTENSION}'):
                    sourceFile = fileClass(sourcePath, **kwargs)
                    return 'Source object created.', sourceFile, None
        return f'{ERROR}This document is not meant to be written back.', None, None


class ImportTargetFactory(FileFactory):
    """A factory class that instantiates a yWriter object to write.

    Public methods:
        make_file_objects(self, sourcePath, **kwargs) -- return conversion objects.
    """

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a target object for conversion to a yWriter project.

        Positional arguments:
            sourcePath -- str: path to the source file to convert.

        Optional arguments:
            suffix -- str: an indicator for the source file type.

        Required keyword arguments: 
            suffix -- str: target file name suffix.

        Return a tuple with three elements:
        - A message beginning with the ERROR constant in case of error
        - sourceFile: None
        - targetFile: a YwFile subclass instance, or None in case of error
        """
        fileName, __ = os.path.splitext(sourcePath)
        sourceSuffix = kwargs['suffix']
        if sourceSuffix:
            ywPathBasis = fileName.split(sourceSuffix)[0]
        else:
            ywPathBasis = fileName

        # Look for an existing yWriter project to rewrite.
        for fileClass in self._fileClasses:
            if os.path.isfile(f'{ywPathBasis}{fileClass.EXTENSION}'):
                targetFile = fileClass(f'{ywPathBasis}{fileClass.EXTENSION}', **kwargs)
                return 'Target object created.', None, targetFile
            
        return f'{ERROR}No yWriter project to write.', None, None


class YwCnvFf(YwCnvUi):
    """Class for Novel file conversion using factory methods to create target and source classes.

    Public methods:
        run(sourcePath, **kwargs) -- create source and target objects and run conversion.

    Class constants:
        EXPORT_SOURCE_CLASSES -- list of YwFile subclasses from which can be exported.
        EXPORT_TARGET_CLASSES -- list of FileExport subclasses to which export is possible.
        IMPORT_SOURCE_CLASSES -- list of Novel subclasses from which can be imported.
        IMPORT_TARGET_CLASSES -- list of YwFile subclasses to which import is possible.

    All lists are empty and meant to be overridden by subclasses.

    Instance variables:
        exportSourceFactory -- ExportSourceFactory.
        exportTargetFactory -- ExportTargetFactory.
        importSourceFactory -- ImportSourceFactory.
        importTargetFactory -- ImportTargetFactory.
        newProjectFactory -- FileFactory (a stub to be overridden by subclasses).
    """
    EXPORT_SOURCE_CLASSES = []
    EXPORT_TARGET_CLASSES = []
    IMPORT_SOURCE_CLASSES = []
    IMPORT_TARGET_CLASSES = []

    def __init__(self):
        """Create strategy class instances.
        
        Extends the superclass constructor.
        """
        super().__init__()
        self.exportSourceFactory = ExportSourceFactory(self.EXPORT_SOURCE_CLASSES)
        self.exportTargetFactory = ExportTargetFactory(self.EXPORT_TARGET_CLASSES)
        self.importSourceFactory = ImportSourceFactory(self.IMPORT_SOURCE_CLASSES)
        self.importTargetFactory = ImportTargetFactory(self.IMPORT_TARGET_CLASSES)
        self.newProjectFactory = FileFactory()

    def run(self, sourcePath, **kwargs):
        """Create source and target objects and run conversion.

        Positional arguments: 
            sourcePath -- str: the source file path.
        
        Required keyword arguments: 
            suffix -- str: target file name suffix.

        This is a template method that calls superclass methods as primitive operations by case.
        """
        self.newFile = None
        if not os.path.isfile(sourcePath):
            self.ui.set_info_how(f'{ERROR}File "{os.path.normpath(sourcePath)}" not found.')
            return
        
        message, source, __ = self.exportSourceFactory.make_file_objects(sourcePath, **kwargs)
        if message.startswith(ERROR):
            # The source file is not a yWriter project.
            message, source, __ = self.importSourceFactory.make_file_objects(sourcePath, **kwargs)
            if message.startswith(ERROR):
                # A new yWriter project might be required.
                message, source, target = self.newProjectFactory.make_file_objects(sourcePath, **kwargs)
                if message.startswith(ERROR):
                    self.ui.set_info_how(message)
                else:
                    self.create_yw7(source, target)
            else:
                # Try to update an existing yWriter project.
                kwargs['suffix'] = source.SUFFIX
                message, __, target = self.importTargetFactory.make_file_objects(sourcePath, **kwargs)
                if message.startswith(ERROR):
                    self.ui.set_info_how(message)
                else:
                    self.import_to_yw(source, target)
        else:
            # The source file is a yWriter project.
            message, __, target = self.exportTargetFactory.make_file_objects(sourcePath, **kwargs)
            if message.startswith(ERROR):
                self.ui.set_info_how(message)
            else:
                self.export_from_yw(source, target)
import csv
from datetime import datetime
from urllib.parse import quote


class Novel:
    """Abstract yWriter project file representation.

    This class represents a file containing a novel with additional 
    attributes and structural information (a full set or a subset
    of the information included in an yWriter project file).

    Public methods:
        read() -- parse the file and get the instance variables.
        merge(source) -- update instance variables from a source instance.
        write() -- write instance variables to the file.

    Public instance variables:
        title -- str: title.
        desc -- str: description in a single string.
        authorName -- str: author's name.
        author bio -- str: information about the author.
        fieldTitle1 -- str: scene rating field title 1.
        fieldTitle2 -- str: scene rating field title 2.
        fieldTitle3 -- str: scene rating field title 3.
        fieldTitle4 -- str: scene rating field title 4.
        chapters -- dict: (key: ID; value: chapter instance).
        scenes -- dict: (key: ID, value: scene instance).
        srtChapters -- list: the novel's sorted chapter IDs.
        locations -- dict: (key: ID, value: WorldElement instance).
        srtLocations -- list: the novel's sorted location IDs.
        items -- dict: (key: ID, value: WorldElement instance).
        srtItems -- list: the novel's sorted item IDs.
        characters -- dict: (key: ID, value: character instance).
        srtCharacters -- list: the novel's sorted character IDs.
        filePath -- str: path to the file (property with getter and setter). 
    """
    DESCRIPTION = 'Novel'
    EXTENSION = None
    SUFFIX = None
    # To be extended by subclass methods.

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.

        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        Optional arguments:
            kwargs -- keyword arguments to be used by subclasses.            
        """
        self.title = None
        # str
        # xml: <PROJECT><Title>

        self.desc = None
        # str
        # xml: <PROJECT><Desc>

        self.authorName = None
        # str
        # xml: <PROJECT><AuthorName>

        self.authorBio = None
        # str
        # xml: <PROJECT><Bio>

        self.fieldTitle1 = None
        # str
        # xml: <PROJECT><FieldTitle1>

        self.fieldTitle2 = None
        # str
        # xml: <PROJECT><FieldTitle2>

        self.fieldTitle3 = None
        # str
        # xml: <PROJECT><FieldTitle3>

        self.fieldTitle4 = None
        # str
        # xml: <PROJECT><FieldTitle4>

        self.chapters = {}
        # dict
        # xml: <CHAPTERS><CHAPTER><ID>
        # key = chapter ID, value = Chapter instance.
        # The order of the elements does not matter (the novel's order of the chapters is defined by srtChapters)

        self.scenes = {}
        # dict
        # xml: <SCENES><SCENE><ID>
        # key = scene ID, value = Scene instance.
        # The order of the elements does not matter (the novel's order of the scenes is defined by
        # the order of the chapters and the order of the scenes within the chapters)

        self.srtChapters = []
        # list of str
        # The novel's chapter IDs. The order of its elements corresponds to the novel's order of the chapters.

        self.locations = {}
        # dict
        # xml: <LOCATIONS>
        # key = location ID, value = WorldElement instance.
        # The order of the elements does not matter.

        self.srtLocations = []
        # list of str
        # The novel's location IDs. The order of its elements
        # corresponds to the XML project file.

        self.items = {}
        # dict
        # xml: <ITEMS>
        # key = item ID, value = WorldElement instance.
        # The order of the elements does not matter.

        self.srtItems = []
        # list of str
        # The novel's item IDs. The order of its elements corresponds to the XML project file.

        self.characters = {}
        # dict
        # xml: <CHARACTERS>
        # key = character ID, value = Character instance.
        # The order of the elements does not matter.

        self.srtCharacters = []
        # list of str
        # The novel's character IDs. The order of its elements corresponds to the XML project file.

        self._filePath = None
        # str
        # Path to the file. The setter only accepts files of a supported type as specified by EXTENSION.

        self._projectName = None
        # str
        # URL-coded file name without suffix and extension.

        self._projectPath = None
        # str
        # URL-coded path to the project directory.

        self.filePath = filePath

    @property
    def filePath(self):
        return self._filePath

    @filePath.setter
    def filePath(self, filePath):
        """Setter for the filePath instance variable.
                
        - Format the path string according to Python's requirements. 
        - Accept only filenames with the right suffix and extension.
        """
        if self.SUFFIX is not None:
            suffix = self.SUFFIX
        else:
            suffix = ''
        if filePath.lower().endswith(f'{suffix}{self.EXTENSION}'.lower()):
            self._filePath = filePath
            head, tail = os.path.split(os.path.realpath(filePath))
            self.projectPath = quote(head.replace('\\', '/'), '/:')
            self.projectName = quote(tail.replace(f'{suffix}{self.EXTENSION}', ''))

    def read(self):
        """Parse the file and get the instance variables.
        
        Return a message beginning with the ERROR constant in case of error.
        This is a stub to be overridden by subclass methods.
        """
        return f'{ERROR}Read method is not implemented.'

    def merge(self, source):
        """Update instance variables from a source instance.
        
        Positional arguments:
            source -- Novel subclass instance to merge.
        
        Return a message beginning with the ERROR constant in case of error.
        This is a stub to be overridden by subclass methods.
        """
        return f'{ERROR}Merge method is not implemented.'

    def write(self):
        """Write instance variables to the file.
        
        Return a message beginning with the ERROR constant in case of error.
        This is a stub to be overridden by subclass methods.
        """
        return f'{ERROR}Write method is not implemented.'

    def _convert_to_yw(self, text):
        """Return text, converted from source format to yw7 markup.
        
        Positional arguments:
            text -- string to convert.
        
        This is a stub to be overridden by subclass methods.
        """
        return text

    def _convert_from_yw(self, text, quick=False):
        """Return text, converted from yw7 markup to target format.
        
        Positional arguments:
            text -- string to convert.
        
        Optional arguments:
            quick -- bool: if True, apply a conversion mode for one-liners without formatting.
        
        This is a stub to be overridden by subclass methods.
        """
        return text
import re


class Scene:
    """yWriter scene representation.
    
    Public instance variables:
        title -- str: scene title.
        desc -- str: scene description in a single string.
        sceneContent -- str: scene content (property with getter and setter).
        rtfFile -- str: RTF file name (yWriter 5).
        wordCount - int: word count (derived; updated by the sceneContent setter).
        letterCount - int: letter count (derived; updated by the sceneContent setter).
        isUnused -- bool: True if the scene is marked "Unused". 
        isNotesScene -- bool: True if the scene type is "Notes".
        isTodoScene -- bool: True if the scene type is "Todo". 
        doNotExport -- bool: True if the scene is not to be exported to RTF.
        status -- int: scene status (Outline/Draft/1st Edit/2nd Edit/Done).
        sceneNotes -- str: scene notes in a single string.
        tags -- list of scene tags. 
        field1 -- int: scene ratings field 1.
        field2 -- int: scene ratings field 2.
        field3 -- int: scene ratings field 3.
        field4 -- int: scene ratings field 4.
        appendToPrev -- bool: if True, append the scene without a divider to the previous scene.
        isReactionScene -- bool: if True, the scene is "reaction". Otherwise, it's "action". 
        isSubPlot -- bool: if True, the scene belongs to a sub-plot. Otherwise it's main plot.  
        goal -- str: the main actor's scene goal. 
        conflict -- str: what hinders the main actor to achieve his goal.
        outcome -- str: what comes out at the end of the scene.
        characters -- list of character IDs related to this scene.
        locations -- list of location IDs related to this scene. 
        items -- list of item IDs related to this scene.
        date -- str: specific start date in ISO format (yyyy-mm-dd).
        time -- str: specific start time in ISO format (hh:mm).
        minute -- str: unspecific start time: minutes.
        hour -- str: unspecific start time: hour.
        day -- str: unspecific start time: day.
        lastsMinutes -- str: scene duration: minutes.
        lastsHours -- str: scene duration: hours.
        lastsDays -- str: scene duration: days. 
        image -- str:  path to an image related to the scene. 
    """
    STATUS = (None, 'Outline', 'Draft', '1st Edit', '2nd Edit', 'Done')
    # Emulate an enumeration for the scene status
    # Since the items are used to replace text,
    # they may contain spaces. This is why Enum cannot be used here.

    ACTION_MARKER = 'A'
    REACTION_MARKER = 'R'
    NULL_DATE = '0001-01-01'
    NULL_TIME = '00:00:00'

    def __init__(self):
        """Initialize instance variables."""
        self.title = None
        # str
        # xml: <Title>

        self.desc = None
        # str
        # xml: <Desc>

        self._sceneContent = None
        # str
        # xml: <SceneContent>
        # Scene text with yW7 raw markup.

        self.rtfFile = None
        # str
        # xml: <RTFFile>
        # Name of the file containing the scene in yWriter 5.

        self.wordCount = 0
        # int # xml: <WordCount>
        # To be updated by the sceneContent setter

        self.letterCount = 0
        # int
        # xml: <LetterCount>
        # To be updated by the sceneContent setter

        self.isUnused = None
        # bool
        # xml: <Unused> -1

        self.isNotesScene = None
        # bool
        # xml: <Fields><Field_SceneType> 1

        self.isTodoScene = None
        # bool
        # xml: <Fields><Field_SceneType> 2

        self.doNotExport = None
        # bool
        # xml: <ExportCondSpecific><ExportWhenRTF>

        self.status = None
        # int
        # xml: <Status>
        # 1 - Outline
        # 2 - Draft
        # 3 - 1st Edit
        # 4 - 2nd Edit
        # 5 - Done
        # See also the STATUS list for conversion.

        self.sceneNotes = None
        # str
        # xml: <Notes>

        self.tags = None
        # list of str
        # xml: <Tags>

        self.field1 = None
        # str
        # xml: <Field1>

        self.field2 = None
        # str
        # xml: <Field2>

        self.field3 = None
        # str
        # xml: <Field3>

        self.field4 = None
        # str
        # xml: <Field4>

        self.appendToPrev = None
        # bool
        # xml: <AppendToPrev> -1

        self.isReactionScene = None
        # bool
        # xml: <ReactionScene> -1

        self.isSubPlot = None
        # bool
        # xml: <SubPlot> -1

        self.goal = None
        # str
        # xml: <Goal>

        self.conflict = None
        # str
        # xml: <Conflict>

        self.outcome = None
        # str
        # xml: <Outcome>

        self.characters = None
        # list of str
        # xml: <Characters><CharID>

        self.locations = None
        # list of str
        # xml: <Locations><LocID>

        self.items = None
        # list of str
        # xml: <Items><ItemID>

        self.date = None
        # str
        # xml: <SpecificDateMode>-1
        # xml: <SpecificDateTime>1900-06-01 20:38:00

        self.time = None
        # str
        # xml: <SpecificDateMode>-1
        # xml: <SpecificDateTime>1900-06-01 20:38:00

        self.minute = None
        # str
        # xml: <Minute>

        self.hour = None
        # str
        # xml: <Hour>

        self.day = None
        # str
        # xml: <Day>

        self.lastsMinutes = None
        # str
        # xml: <LastsMinutes>

        self.lastsHours = None
        # str
        # xml: <LastsHours>

        self.lastsDays = None
        # str
        # xml: <LastsDays>

        self.image = None
        # str
        # xml: <ImageFile>

    @property
    def sceneContent(self):
        return self._sceneContent

    @sceneContent.setter
    def sceneContent(self, text):
        """Set sceneContent updating word count and letter count."""
        self._sceneContent = text
        text = re.sub('\[.+?\]|\.|\,| -', '', self._sceneContent)
        # Remove yWriter raw markup for word count
        wordList = text.split()
        self.wordCount = len(wordList)
        text = re.sub('\[.+?\]', '', self._sceneContent)
        # Remove yWriter raw markup for letter count
        text = text.replace('\n', '')
        text = text.replace('\r', '')
        self.letterCount = len(text)


class Chapter:
    """yWriter chapter representation.
    
    Public instance variables:
        title -- str: chapter title (may be the heading).
        desc -- str: chapter description in a single string.
        chLevel -- int: chapter level (part/chapter).
        oldType -- int: chapter type (Chapter/Other).
        chType -- int: chapter type yWriter 7.0.7.2+ (Normal/Notes/Todo).
        isUnused -- bool: True, if the chapter is marked "Unused".
        suppressChapterTitle -- bool: uppress chapter title when exporting.
        isTrash -- bool: True, if the chapter is the project's trash bin.
        suppressChapterBreak -- bool: Suppress chapter break when exporting.
        srtScenes -- list of str: the chapter's sorted scene IDs.        
    """

    def __init__(self):
        """Initialize instance variables."""
        self.title = None
        # str
        # xml: <Title>

        self.desc = None
        # str
        # xml: <Desc>

        self.chLevel = None
        # int
        # xml: <SectionStart>
        # 0 = chapter level
        # 1 = section level ("this chapter begins a section")

        self.oldType = None
        # int
        # xml: <Type>
        # 0 = chapter type (marked "Chapter")
        # 1 = other type (marked "Other")
        # Applies to projects created by a yWriter version prior to 7.0.7.2.

        self.chType = None
        # int
        # xml: <ChapterType>
        # 0 = Normal
        # 1 = Notes
        # 2 = Todo
        # Applies to projects created by yWriter version 7.0.7.2+.

        self.isUnused = None
        # bool
        # xml: <Unused> -1

        self.suppressChapterTitle = None
        # bool
        # xml: <Fields><Field_SuppressChapterTitle> 1
        # True: Chapter heading not to be displayed in written document.
        # False: Chapter heading to be displayed in written document.

        self.isTrash = None
        # bool
        # xml: <Fields><Field_IsTrash> 1
        # True: This chapter is the yw7 project's "trash bin".
        # False: This chapter is not a "trash bin".

        self.suppressChapterBreak = None
        # bool
        # xml: <Fields><Field_SuppressChapterBreak> 0

        self.srtScenes = []
        # list of str
        # xml: <Scenes><ScID>
        # The chapter's scene IDs. The order of its elements
        # corresponds to the chapter's order of the scenes.



class WorldElement:
    """Story world element representation (may be location or item).
    
    Public instance variables:
        title -- str: title (name).
        image -- str: image file path.
        desc -- str: description.
        tags -- list of tags.
        aka -- str: alternate name.
    """

    def __init__(self):
        """Initialize instance variables."""
        self.title = None
        # str
        # xml: <Title>

        self.image = None
        # str
        # xml: <ImageFile>

        self.desc = None
        # str
        # xml: <Desc>

        self.tags = None
        # list of str
        # xml: <Tags>

        self.aka = None
        # str
        # xml: <AKA>


class Character(WorldElement):
    """yWriter character representation.

    Public instance variables:
        notes -- str: character notes.
        bio -- str: character biography.
        goals -- str: character's goals in the story.
        fullName -- str: full name (the title inherited may be a short name).
        isMajor -- bool: True, if it's a major character.
    """
    MAJOR_MARKER = 'Major'
    MINOR_MARKER = 'Minor'

    def __init__(self):
        """Extends the superclass constructor by adding instance variables."""
        super().__init__()

        self.notes = None
        # str
        # xml: <Notes>

        self.bio = None
        # str
        # xml: <Bio>

        self.goals = None
        # str
        # xml: <Goals>

        self.fullName = None
        # str
        # xml: <FullName>

        self.isMajor = None
        # bool
        # xml: <Major>


def fix_iso_dt(dateTimeStr):
    """Return a date/time string with a four-number year.
    
    Positional arguments:
        dateTimeStr -- str: date/time as read in from Aeon3 csv export.
    
    This is required for comparing date/time strings, 
    and by the datetime.fromisoformat() method.

    Substitute missing time by "00:00:00".
    Substitute missing month by '01'.
    Substitute missing day by '01'.
    If the date is empty or out of yWriter's range, return None. 
    """
    if not dateTimeStr:
        return None

    if dateTimeStr.startswith('BC'):
        return None

    dt = dateTimeStr.split(' ')
    if len(dt) == 1:
        dt.append('00:00:00')
    date = dt[0].split('-')
    while len(date) < 3:
        date.append('01')
    if int(date[0]) < 100:
        return None

    if int(date[0]) > 9999:
        return None

    date[0] = date[0].zfill(4)
    dt[0] = ('-').join(date)
    dateTimeStr = (' ').join(dt)
    return dateTimeStr


class CsvTimeline3(Novel):
    """File representation of a csv file exported by Aeon Timeline 3. 

    Public methods:
        read() -- parse the file and get the instance variables.

    Represents a csv file with a record per scene.
    - Records are separated by line breaks.
    - Data fields are delimited by commas.
    """
    EXTENSION = '.csv'
    DESCRIPTION = 'Aeon Timeline CSV export'
    SUFFIX = ''
    _SEPARATOR = ','

    # Aeon 3 csv export structure (fix part)

    # Types
    _TYPE_EVENT = 'Event'
    _TYPE_NARRATIVE = 'Narrative Folder'

    # Field names
    _LABEL_FIELD = 'Label'
    _TYPE_FIELD = 'Type'
    _SCENE_FIELD = 'Narrative Position'
    _START_DATE_TIME_FIELD = 'Start Date'
    _END_DATE_TIME_FIELD = 'End Date'

    # Narrative position markers
    _PART_MARKER = 'Part'
    _CHAPTER_MARKER = 'Chapter'
    _SCENE_MARKER = 'Scene'
    # Events assigned to the "narrative" become
    # regular scenes, the others become Notes scenes.

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.

        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        Required keyword arguments:
            part_number_prefix -- str: prefix to the part number in the part's heading.
            chapter_number_prefix -- str: prefix to the chapter number in the chapter's heading.
            type_location -- str: label of the "Location" item type representing locations.
            type_item -- str: label of the "Item" item type representing items.
            type_character -- str: label of the "Character" item type representing characters. 
            part_desc_label -- str: label of the csv field for the part's description.
            chapter_desc_label -- str: label of the csv field for the chapter's description.
            scene_desc_label -- str: label of the csv field for the scene's description.
            scene_title_label -- str: label of the csv field for the scene's title.
            notes_label -- str: label of the "Notes" property of events and characters.
            tag_label -- str: label of the csv field for the scene's tags.
            item_label -- str: label of the "Item" role type.
            character_label -- str: label of the "Participant" role type.
            viewpoint_label -- str: label of the "Viewpoint" property of events.
            location_label -- str: label of the "Location" role type.
            character_desc_label1 -- str: label of the character property imported as 1st part of the description.
            character_desc_label2 -- str: label of the character property imported as 2nd part of the description.
            character_desc_label3 -- str: label of the character property imported as 3rd part of the description.
            character_bio_label -- str: 
            character_aka_label -- str: label of the "Nickname" property of characters.           
        
        Extends the superclass constructor.
        """
        super().__init__(filePath, **kwargs)
        self.labels = []
        self.partNrPrefix = kwargs['part_number_prefix']
        if self.partNrPrefix:
            self.partNrPrefix += ' '
        self.chapterNrPrefix = kwargs['chapter_number_prefix']
        if self.chapterNrPrefix:
            self.chapterNrPrefix += ' '
        self.typeLocation = kwargs['type_location']
        self.typeItem = kwargs['type_item']
        self.typeCharacter = kwargs['type_character']
        self.partDescField = kwargs['part_desc_label']
        self.chapterDescField = kwargs['chapter_desc_label']
        self.sceneDescField = kwargs['scene_desc_label']
        self.sceneTitleField = kwargs['scene_title_label']
        self.notesField = kwargs['notes_label']
        self.tagField = kwargs['tag_label']
        self.itemField = kwargs['item_label']
        self.characterField = kwargs['character_label']
        self.viewpointField = kwargs['viewpoint_label']
        self.locationField = kwargs['location_label']
        self.characterDescField1 = kwargs['character_desc_label1']
        self.characterDescField2 = kwargs['character_desc_label2']
        self.characterDescField3 = kwargs['character_desc_label3']
        self.characterBioField = kwargs['character_bio_label']
        self.characterAkaField = kwargs['character_aka_label']
        self.locationDescField = kwargs['location_desc_label']

    def read(self):
        """Parse the file and get the instance variables.
        
        Build a yWriter novel structure from an Aeon3 csv export.
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """

        def get_lcIds(lcTitles):
            """Return a list of location IDs; Add new location to the project."""
            lcIds = []
            for lcTitle in lcTitles:
                if lcTitle in self.locIdsByTitle:
                    lcIds.append(self.locIdsByTitle[lcTitle])
                else:
                    return None
            return lcIds

        def get_itIds(itTitles):
            """Return a list of item IDs; Add new item to the project."""
            itIds = []
            for itTitle in itTitles:
                if itTitle in self.itmIdsByTitle:
                    itIds.append(self.itmIdsByTitle[itTitle])
                else:
                    return None
            return itIds

        def get_crIds(crTitles):
            """Return a list of character IDs; Add new characters to the project."""
            crIds = []
            for crTitle in crTitles:
                if crTitle in self.chrIdsByTitle:
                    crIds.append(self.chrIdsByTitle[crTitle])
                else:
                    return None
            return crIds
        #--- Read the csv file.
        internalDelimiter = ','
        try:
            with open(self.filePath, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=self._SEPARATOR)
                for label in reader.fieldnames:
                    self.labels.append(label)
                eventsAndFolders = []
                characterCount = 0
                self.chrIdsByTitle = {}
                # key = character title
                # value = character ID
                locationCount = 0
                self.locIdsByTitle = {}
                # key = location title
                # value = location ID
                itemCount = 0
                self.itmIdsByTitle = {}
                # key = item title
                # value = item ID
                for row in reader:
                    aeonEntity = {}
                    for label in row:
                        aeonEntity[label] = row[label]
                    if self._TYPE_EVENT == aeonEntity[self._TYPE_FIELD]:
                        eventsAndFolders.append(aeonEntity)
                    elif self._TYPE_NARRATIVE == aeonEntity[self._TYPE_FIELD]:
                        eventsAndFolders.append(aeonEntity)
                    elif self.typeCharacter == aeonEntity[self._TYPE_FIELD]:
                        characterCount += 1
                        crId = str(characterCount)
                        self.chrIdsByTitle[aeonEntity[self._LABEL_FIELD]] = crId
                        self.characters[crId] = Character()
                        self.characters[crId].title = aeonEntity[self._LABEL_FIELD]
                        charDesc = []
                        if self.characterDescField1 in aeonEntity:
                            charDesc.append(aeonEntity[self.characterDescField1])
                        if self.characterDescField2 and self.characterDescField2 in aeonEntity:
                            charDesc.append(aeonEntity[self.characterDescField2])
                        if self.characterDescField3 and self.characterDescField3 in aeonEntity:
                            charDesc.append(aeonEntity[self.characterDescField3])
                        self.characters[crId].desc = ('\n').join(charDesc)
                        if self.characterBioField in aeonEntity:
                            self.characters[crId].bio = aeonEntity[self.characterBioField]
                        if self.characterAkaField in aeonEntity:
                            self.characters[crId].aka = aeonEntity[self.characterAkaField]
                        if self.tagField in aeonEntity and aeonEntity[self.tagField]:
                            self.characters[crId].tags = aeonEntity[self.tagField].split(internalDelimiter)
                        if self.notesField in aeonEntity:
                            self.characters[crId].notes = aeonEntity[self.notesField]
                        self.srtCharacters.append(crId)
                    elif self.typeLocation == aeonEntity[self._TYPE_FIELD]:
                        locationCount += 1
                        lcId = str(locationCount)
                        self.locIdsByTitle[aeonEntity[self._LABEL_FIELD]] = lcId
                        self.locations[lcId] = WorldElement()
                        self.locations[lcId].title = aeonEntity[self._LABEL_FIELD]
                        self.srtLocations.append(lcId)
                        if self.locationDescField in aeonEntity:
                            self.locations[lcId].desc = aeonEntity[self.locationDescField]
                        if self.tagField in aeonEntity:
                            self.locations[lcId].tags = aeonEntity[self.tagField].split(internalDelimiter)
                    elif self.typeItem == aeonEntity[self._TYPE_FIELD]:
                        itemCount += 1
                        itId = str(itemCount)
                        self.itmIdsByTitle[aeonEntity[self._LABEL_FIELD]] = itId
                        self.items[itId] = WorldElement()
                        self.items[itId].title = aeonEntity[self._LABEL_FIELD]
                        self.srtItems.append(itId)
        except(FileNotFoundError):
            return f'{ERROR}"{os.path.normpath(self.filePath)}" not found.'

        except:
            return f'{ERROR}Can not parse csv file "{os.path.normpath(self.filePath)}".'

        try:
            for label in [self._SCENE_FIELD, self.sceneTitleField, self._START_DATE_TIME_FIELD, self._END_DATE_TIME_FIELD]:
                if not label in self.labels:
                    return f'{ERROR}Label "{label}" is missing.'

            scIdsByStruc = {}
            chIdsByStruc = {}
            otherEvents = []
            eventCount = 0
            chapterCount = 0
            for aeonEntity in eventsAndFolders:
                if aeonEntity[self._SCENE_FIELD]:
                    narrativeType, narrativePosition = aeonEntity[self._SCENE_FIELD].split(' ')

                    # Make the narrative position a sortable string.
                    numbers = narrativePosition.split('.')
                    for i in range(len(numbers)):
                        numbers[i] = numbers[i].zfill(4)
                        narrativePosition = ('.').join(numbers)
                else:
                    narrativeType = ''
                    narrativePosition = ''
                if aeonEntity[self._TYPE_FIELD] == self._TYPE_NARRATIVE:
                    if narrativeType == self._CHAPTER_MARKER:
                        chapterCount += 1
                        chId = str(chapterCount)
                        chIdsByStruc[narrativePosition] = chId
                        self.chapters[chId] = Chapter()
                        self.chapters[chId].chLevel = 0
                        if self.chapterDescField:
                            self.chapters[chId].desc = aeonEntity[self.chapterDescField]
                    elif narrativeType == self._PART_MARKER:
                        chapterCount += 1
                        chId = str(chapterCount)
                        chIdsByStruc[narrativePosition] = chId
                        self.chapters[chId] = Chapter()
                        self.chapters[chId].chLevel = 1
                        narrativePosition += '.0000'
                        if self.partDescField:
                            self.chapters[chId].desc = aeonEntity[self.partDescField]
                    continue

                elif aeonEntity[self._TYPE_FIELD] != self._TYPE_EVENT:
                    continue

                eventCount += 1
                scId = str(eventCount)
                self.scenes[scId] = Scene()
                if narrativeType == self._SCENE_MARKER:
                    self.scenes[scId].isNotesScene = False
                    scIdsByStruc[narrativePosition] = scId
                else:
                    self.scenes[scId].isNotesScene = True
                    otherEvents.append(scId)
                self.scenes[scId].title = aeonEntity[self.sceneTitleField]
                startDateTimeStr = fix_iso_dt(aeonEntity[self._START_DATE_TIME_FIELD])
                if startDateTimeStr is not None:
                    startDateTime = startDateTimeStr.split(' ')
                    self.scenes[scId].date = startDateTime[0]
                    self.scenes[scId].time = startDateTime[1]
                    endDateTimeStr = fix_iso_dt(aeonEntity[self._END_DATE_TIME_FIELD])
                    if endDateTimeStr is not None:
                        # Calculate duration of scenes that begin after 99-12-31.
                        sceneStart = datetime.fromisoformat(startDateTimeStr)
                        sceneEnd = datetime.fromisoformat(endDateTimeStr)
                        sceneDuration = sceneEnd - sceneStart
                        lastsHours = sceneDuration.seconds // 3600
                        lastsMinutes = (sceneDuration.seconds % 3600) // 60
                        self.scenes[scId].lastsDays = str(sceneDuration.days)
                        self.scenes[scId].lastsHours = str(lastsHours)
                        self.scenes[scId].lastsMinutes = str(lastsMinutes)
                else:
                    self.scenes[scId].date = Scene.NULL_DATE
                    self.scenes[scId].time = Scene.NULL_TIME
                if self.sceneDescField in aeonEntity:
                    self.scenes[scId].desc = aeonEntity[self.sceneDescField]
                if self.notesField in aeonEntity:
                    self.scenes[scId].sceneNotes = aeonEntity[self.notesField]
                if self.tagField in aeonEntity and aeonEntity[self.tagField]:
                    self.scenes[scId].tags = aeonEntity[self.tagField].split(internalDelimiter)
                if self.locationField in aeonEntity:
                    self.scenes[scId].locations = get_lcIds(aeonEntity[self.locationField].split(internalDelimiter))
                if self.characterField in aeonEntity:
                    self.scenes[scId].characters = get_crIds(aeonEntity[self.characterField].split(internalDelimiter))
                if self.viewpointField in aeonEntity:
                    vpIds = get_crIds([aeonEntity[self.viewpointField]])
                    if vpIds is not None:
                        vpId = vpIds[0]
                        if self.scenes[scId].characters is None:
                            self.scenes[scId].characters = []
                        elif vpId in self.scenes[scId].characters:
                            self.scenes[scId].characters.remove[vpId]
                        self.scenes[scId].characters.insert(0, vpId)
                if self.itemField in aeonEntity:
                    self.scenes[scId].items = get_itIds(aeonEntity[self.itemField].split(internalDelimiter))

                self.scenes[scId].status = 1
                # Set scene status = "Outline".
        except(FileNotFoundError):
            return f'{ERROR}"{os.path.normpath(self.filePath)}" not found.'

        except(KeyError):
            return f'{ERROR}Wrong csv structure.'

        except(ValueError):
            return f'{ERROR}Wrong date/time format.'

        except:
            return f'{ERROR}Can not parse "{os.path.normpath(self.filePath)}".'

        # Build the chapter structure as defined with Aeon v3.
        srtChpDict = sorted(chIdsByStruc.items())
        srtScnDict = sorted(scIdsByStruc.items())
        partNr = 0
        chapterNr = 0
        for ch in srtChpDict:
            self.srtChapters.append(ch[1])
            if self.chapters[ch[1]].chLevel == 0:
                chapterNr += 1
                self.chapters[ch[1]].title = self.chapterNrPrefix + str(chapterNr)
                for sc in srtScnDict:
                    if sc[0].startswith(ch[0]):
                        self.chapters[ch[1]].srtScenes.append(sc[1])
            else:
                partNr += 1
                self.chapters[ch[1]].title = self.partNrPrefix + str(partNr)
        # Create a chapter for the non-narrative events.
        chapterNr += 1
        chId = str(chapterCount + 1)
        self.chapters[chId] = Chapter()
        self.chapters[chId].title = 'Other events'
        self.chapters[chId].desc = 'Scenes generated from events that ar not assigned to the narrative structure.'
        self.chapters[chId].chType = 1
        self.chapters[chId].srtScenes = otherEvents
        self.srtChapters.append(chId)
        return 'Timeline data converted to novel structure.'
import json
from datetime import datetime
from datetime import timedelta
import codecs


def scan_file(filePath):
    """Read and scan the project file.
    
    Positional arguments:
        filePath -- str: Path to the Aeon 3 project file.
    
    Return a string containing either the JSON part or an error message.
    """
    try:
        with open(filePath, 'rb') as f:
            binInput = f.read()
    except(FileNotFoundError):
        return f'{ERROR}"{os.path.normpath(filePath)}" not found.'

    except:
        return f'{ERROR}Cannot read "{os.path.normpath(filePath)}".'
    
    # JSON part: all characters between the first and last curly bracket.
    chrData = []
    opening = ord('{')
    closing = ord('}')
    level = 0
    for c in binInput:
        if c == opening:
            level += 1
        if level > 0:
            chrData.append(c)
            if c == closing:
                level -= 1
                if level == 0:
                    break

    if level != 0:
        return f'{ERROR}Corrupted data.'

    try:
        jsonStr = codecs.decode(bytes(chrData), encoding='utf-8')
    except:
        return f'{ERROR}Cannot decode "{os.path.normpath(filePath)}".'

    return jsonStr


class JsonTimeline3(Novel):
    """File representation of an Aeon Timeline 3 project. 

    Public methods:
        read() -- parse the file and get the instance variables.

    Represents the JSON part of the project file.
    """
    EXTENSION = '.aeon'
    DESCRIPTION = 'Aeon Timeline 3 project'
    SUFFIX = ''
    DATE_LIMIT = (datetime(100, 1, 1) - datetime.min).total_seconds()
    # Dates before 100-01-01 can not be displayed properly in yWriter

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.

        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        Required keyword arguments:
            type_event -- str: label of the "Event" item type representing scenes.
            type_character -- str: label of the "Character" item type representing characters. 
            type_location -- str: label of the "Location" item type representing locations.
            type_item -- str: label of the "Item" item type representing items.
            notes_label -- str: label of the "Notes" property of events and characters.
            character_desc_label1 -- str: label of the character property imported as 1st part of the description.
            character_desc_label2 -- str: label of the character property imported as 2nd part of the description.
            character_desc_label3 -- str: label of the character property imported as 3rd part of the description.
            character_aka_label -- str: label of the "Nickname" property of characters.
            viewpoint_label -- str: label of the "Viewpoint" property of events.
            character_label -- str: label of the "Participant" role type.
            location_label -- str: label of the "Location" role type.
            item_label -- str: label of the "Item" role type.
            part_number_prefix -- str: prefix to the part number in the part's heading.
            chapter_number_prefix -- str: prefix to the chapter number in the chapter's heading.
        
        Extends the superclass constructor.
        """
        super().__init__(filePath, **kwargs)

        # JSON[definitions][types][byId]
        self._labelEventType = kwargs['type_event']
        self._labelCharacterType = kwargs['type_character']
        self._labelLocationType = kwargs['type_location']
        self._labelItemType = kwargs['type_item']

        # JSON[definitions][properties][byId]
        self._labelNotesProperty = kwargs['notes_label']
        self._labelChrDesc1Property = kwargs['character_desc_label1']
        self._labelChrDesc2Property = kwargs['character_desc_label2']
        self._labelChrDesc3Property = kwargs['character_desc_label3']
        self._labelAkaProperty = kwargs['character_aka_label']
        self._labelViewpointProperty = kwargs['viewpoint_label']

        # JSON[definitions][references][byId]
        self._labelParticipantRef = kwargs['character_label']
        self._labelLocationRef = kwargs['location_label']
        self._labelItemRef = kwargs['item_label']

        # Misc.
        self._partHdPrefix = kwargs['part_number_prefix']
        self._chapterHdPrefix = kwargs['chapter_number_prefix']

    def read(self):
        """Parse the file and get the instance variables.
        
        Extract the JSON part of the Aeon Timeline 3 file located at filePath
        and build a yWriter novel structure.
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """
        jsonPart = scan_file(self.filePath)
        if not jsonPart:
            return f'{ERROR}No JSON part found.'
        elif jsonPart.startswith(ERROR):
            return jsonPart
        try:
            jsonData = json.loads(jsonPart)
        except('JSONDecodeError'):
            return f'{ERROR}Invalid JSON data.'

        #--- Find types.
        typeEventUid = None
        typeCharacterUid = None
        typeLocationUid = None
        typeItemUid = None
        NarrativeFolderTypes = []
        for uid in jsonData['definitions']['types']['byId']:

            if jsonData['definitions']['types']['byId'][uid]['isNarrativeFolder']:
                NarrativeFolderTypes.append(uid)

            elif jsonData['definitions']['types']['byId'][uid]['label'] == self._labelEventType:
                typeEventUid = uid

            elif jsonData['definitions']['types']['byId'][uid]['label'] == self._labelCharacterType:
                typeCharacterUid = uid

            elif jsonData['definitions']['types']['byId'][uid]['label'] == self._labelLocationType:
                typeLocationUid = uid

            elif jsonData['definitions']['types']['byId'][uid]['label'] == self._labelItemType:
                typeItemUid = uid

        #--- Find properties.
        propNotesUid = None
        propChrDesc1Uid = None
        propChrDesc2Uid = None
        propChrDesc3Uid = None
        propAkaUid = None
        propViewpointUid = None
        for uid in jsonData['definitions']['properties']['byId']:

            if jsonData['definitions']['properties']['byId'][uid]['label'] == self._labelNotesProperty:
                typeNotesUid = uid

            elif jsonData['definitions']['properties']['byId'][uid]['label'] == self._labelChrDesc1Property:
                propChrDesc1Uid = uid

            elif jsonData['definitions']['properties']['byId'][uid]['label'] == self._labelChrDesc2Property:
                propChrDesc2Uid = uid

            elif jsonData['definitions']['properties']['byId'][uid]['label'] == self._labelChrDesc3Property:
                propChrDesc3Uid = uid

            elif jsonData['definitions']['properties']['byId'][uid]['label'] == self._labelAkaProperty:
                propAkaUid = uid

            elif jsonData['definitions']['properties']['byId'][uid]['label'] == self._labelViewpointProperty:
                propViewpointUid = uid

        #--- Find references.
        refParticipant = None
        refLocation = None
        for uid in jsonData['definitions']['references']['byId']:

            if jsonData['definitions']['references']['byId'][uid]['label'] == self._labelParticipantRef:
                refParticipant = uid

            elif jsonData['definitions']['references']['byId'][uid]['label'] == self._labelLocationRef:
                refLocation = uid

        #--- Read items.
        crIdsByGuid = {}
        lcIdsByGuid = {}
        itIdsByGuid = {}
        scIdsByGuid = {}
        chIdsByGuid = {}
        characterCount = 0
        locationCount = 0
        itemCount = 0
        eventCount = 0
        chapterCount = 0
        vpGuidByScId = {}
        for uid in jsonData['data']['items']['byId']:
            dataItem = jsonData['data']['items']['byId'][uid]
            if dataItem['type'] == typeEventUid:

                #--- Create scenes.
                eventCount += 1
                scId = str(eventCount)
                scIdsByGuid[uid] = scId
                self.scenes[scId] = Scene()
                self.scenes[scId].status = 1
                # Set scene status = "Outline"
                self.scenes[scId].isNotesScene = True
                # Will be set to False later if it is part of the narrative.
                self.scenes[scId].title = dataItem['label']
                self.scenes[scId].desc = dataItem['summary']
                timestamp = dataItem['startDate']['timestamp']

                #--- Get scene tags.
                for tagId in dataItem['tags']:
                    if self.scenes[scId].tags is None:
                        self.scenes[scId].tags = []
                    self.scenes[scId].tags.append(jsonData['data']['tags'][tagId])

                #--- Get scene properties.
                for propId in dataItem['propertyValues']:
                    if propId == propNotesUid:
                        self.scenes[scId].sceneNotes = dataItem['propertyValues'][propId]
                    elif propId == propViewpointUid:
                        vpGuidByScId[scId] = dataItem['propertyValues'][propId]

                #--- Get scene date, time, and duration.
                if timestamp is not None and timestamp >= self.DATE_LIMIT:
                    # Restrict date/time calculation to dates within yWriter's range
                    sceneStart = datetime.min + timedelta(seconds=timestamp)
                    startDateTime = sceneStart.isoformat().split('T')
                    self.scenes[scId].date = startDateTime[0]
                    self.scenes[scId].time = startDateTime[1]

                    # Calculate duration.
                    if dataItem['duration']['years'] > 0 or dataItem['duration']['months'] > 0:
                        endYear = sceneStart.year + dataItem['duration']['years']
                        endMonth = sceneStart.month
                        if dataItem['duration']['months'] > 0:
                            endMonth += dataItem['duration']['months']
                            while endMonth > 12:
                                endMonth -= 12
                                endYear += 1
                        sceneDuration = datetime(endYear, endMonth, sceneStart.day) - \
                                datetime(sceneStart.year, sceneStart.month, sceneStart.day)
                        lastsDays = sceneDuration.days
                        lastsHours = sceneDuration.seconds // 3600
                        lastsMinutes = (sceneDuration.seconds % 3600) // 60
                    else:
                        lastsDays = 0
                        lastsHours = 0
                        lastsMinutes = 0
                    lastsDays += dataItem['duration']['weeks'] * 7
                    lastsDays += dataItem['duration']['days']
                    lastsDays += dataItem['duration']['hours'] // 24
                    lastsHours += dataItem['duration']['hours'] % 24
                    lastsHours += dataItem['duration']['minutes'] // 60
                    lastsMinutes += dataItem['duration']['minutes'] % 60
                    lastsMinutes += dataItem['duration']['seconds'] // 60
                    lastsHours += lastsMinutes // 60
                    lastsMinutes %= 60
                    lastsDays += lastsHours // 24
                    lastsHours %= 24
                    self.scenes[scId].lastsDays = str(lastsDays)
                    self.scenes[scId].lastsHours = str(lastsHours)
                    self.scenes[scId].lastsMinutes = str(lastsMinutes)
            elif dataItem['type'] in NarrativeFolderTypes:
                #--- Create chapters.
                chapterCount += 1
                chId = str(chapterCount)
                chIdsByGuid[uid] = chId
                self.chapters[chId] = Chapter()
                self.chapters[chId].desc = dataItem['label']
            elif dataItem['type'] == typeCharacterUid:
                #--- Create characters.
                characterCount += 1
                crId = str(characterCount)
                crIdsByGuid[uid] = crId
                self.characters[crId] = Character()
                if dataItem['shortLabel']:
                    self.characters[crId].title = dataItem['shortLabel']
                else:
                    self.characters[crId].title = dataItem['label']
                self.characters[crId].fullName = dataItem['label']
                self.characters[crId].bio = dataItem['summary']
                self.srtCharacters.append(crId)

                #--- Get character tags.
                for tagId in dataItem['tags']:
                    if self.characters[crId].tags is None:
                        self.characters[crId].tags = []
                    self.characters[crId].tags.append(jsonData['data']['tags'][tagId])

                #--- Get character properties.
                charDesc = []
                for propId in dataItem['propertyValues']:
                    if propId == propNotesUid:
                        self.characters[crId].notes = dataItem['propertyValues'][propId]
                    elif propId == propAkaUid:
                        self.characters[crId].aka = dataItem['propertyValues'][propId]
                    elif propId == propChrDesc1Uid:
                        charDesc.append(dataItem['propertyValues'][propId])
                    elif propId == propChrDesc2Uid:
                        charDesc.append(dataItem['propertyValues'][propId])
                    elif propId == propChrDesc3Uid:
                        charDesc.append(dataItem['propertyValues'][propId])
                self.characters[crId].desc = ('\n').join(charDesc)
            elif dataItem['type'] == typeLocationUid:
                #--- Create locations.
                locationCount += 1
                lcId = str(locationCount)
                lcIdsByGuid[uid] = lcId
                self.locations[lcId] = WorldElement()
                self.locations[lcId].title = dataItem['label']
                self.locations[lcId].desc = dataItem['summary']
                self.srtLocations.append(lcId)

                #--- Get location tags.
                for tagId in dataItem['tags']:
                    if self.locations[lcId].tags is None:
                        self.locations[lcId].tags = []
                    self.locations[lcId].tags.append(jsonData['data']['tags'][tagId])
            elif dataItem['type'] == typeItemUid:
                #--- Create items.
                itemCount += 1
                itId = str(itemCount)
                itIdsByGuid[uid] = itId
                self.items[itId] = WorldElement()
                self.items[itId].title = dataItem['label']
                self.items[itId].desc = dataItem['summary']
                self.srtItems.append(itId)

                #--- Get item tags.
                for tagId in dataItem['tags']:
                    if self.items[itId].tags is None:
                        self.items[itId].tags = []
                    self.items[itId].tags.append(jsonData['data']['tags'][tagId])
        #--- Read relationships.
        for uid in jsonData['data']['relationships']['byId']:
            if jsonData['data']['relationships']['byId'][uid]['reference'] == refParticipant:
                #--- Assign characters.
                try:
                    scId = scIdsByGuid[jsonData['data']['relationships']['byId'][uid]['subject']]
                    crId = crIdsByGuid[jsonData['data']['relationships']['byId'][uid]['object']]
                    if self.scenes[scId].characters is None:
                        self.scenes[scId].characters = []
                    if not crId in self.scenes[scId].characters:
                        self.scenes[scId].characters.append(crId)
                except:
                    pass
            elif jsonData['data']['relationships']['byId'][uid]['reference'] == refLocation:
                #--- Assign locations.
                try:
                    scId = scIdsByGuid[jsonData['data']['relationships']['byId'][uid]['subject']]
                    lcId = lcIdsByGuid[jsonData['data']['relationships']['byId'][uid]['object']]
                    if self.scenes[scId].locations is None:
                        self.scenes[scId].locations = []
                    if not lcId in self.scenes[scId].locations:
                        self.scenes[scId].locations.append(lcId)
                except:
                    pass
        #--- Set scene viewpoints.
        for scId in vpGuidByScId:
            if vpGuidByScId[scId] in crIdsByGuid:
                vpId = crIdsByGuid[vpGuidByScId[scId]]
                if self.scenes[scId].characters is None:
                    self.scenes[scId].characters = []
                elif vpId in self.scenes[scId].characters:
                    self.scenes[scId].characters.remove[vpId]
                self.scenes[scId].characters.insert(0, vpId)
        #--- Build a narrative structure with 2 or 3 levels.
        for narrative0 in jsonData['data']['narrative']['children']:
            if narrative0['id'] in chIdsByGuid:
                self.srtChapters.append(chIdsByGuid[narrative0['id']])
            for narrative1 in narrative0['children']:
                if narrative1['id'] in chIdsByGuid:
                    self.srtChapters.append(chIdsByGuid[narrative1['id']])
                    self.chapters[chIdsByGuid[narrative0['id']]].chLevel = 1
                    for narrative2 in narrative1['children']:
                        if narrative2['id'] in scIdsByGuid:
                            self.chapters[chIdsByGuid[narrative1['id']]].srtScenes.append(
                                scIdsByGuid[narrative2['id']])
                            self.scenes[scIdsByGuid[narrative2['id']]].isNotesScene = False
                            self.chapters[chIdsByGuid[narrative1['id']]].chLevel = 0
                elif narrative1['id'] in scIdsByGuid:
                    self.chapters[chIdsByGuid[narrative0['id']]].srtScenes.append(scIdsByGuid[narrative1['id']])
                    self.scenes[scIdsByGuid[narrative1['id']]].isNotesScene = False
                    self.chapters[chIdsByGuid[narrative0['id']]].chLevel = 0
        #--- Auto-number untitled chapters.
        partCount = 0
        chapterCount = 0
        for chId in self.srtChapters:
            if self.chapters[chId].chLevel == 1:
                partCount += 1
                if not self.chapters[chId].title:
                    self.chapters[chId].title = f'{self._partHdPrefix} {partCount}'
            else:
                chapterCount += 1
                if not self.chapters[chId].title:
                    self.chapters[chId].title = f'{self._chapterHdPrefix} {chapterCount}'
        #--- Create a "Notes" chapter for non-narrative scenes.
        chId = str(partCount + chapterCount + 1)
        self.chapters[chId] = Chapter()
        self.chapters[chId].title = 'Other events'
        self.chapters[chId].desc = 'Scenes generated from events that ar not assigned to the narrative structure.'
        self.chapters[chId].chType = 1
        self.srtChapters.append(chId)
        for scId in self.scenes:
            if self.scenes[scId].isNotesScene:
                self.chapters[chId].srtScenes.append(scId)
        return 'Timeline data converted to novel structure.'
from string import Template


class Filter:
    """Filter an entity (chapter/scene/character/location/item) by filter criteria.
    
    Public methods:
        accept(source, eId) -- check whether an entity matches the filter criteria.
    
    Strategy class, implementing filtering criteria for template-based export.
    This is a stub with no filter criteria specified.
    """

    def accept(self, source, eId):
        """Check whether an entity matches the filter criteria.
        
        Positional arguments:
            source -- Novel instance holding the entity to check.
            eId -- ID of the entity to check.       
        
        Return True if the entity is not to be filtered out.
        This is a stub to be overridden by subclass methods implementing filters.
        """
        return True


class FileExport(Novel):
    """Abstract yWriter project file exporter representation.
    
    Public methods:
        merge(source) -- update instance variables from a source instance.
        write() -- write instance variables to the export file.
    
    This class is generic and contains no conversion algorithm and no templates.
    """
    SUFFIX = ''
    _fileHeader = ''
    _partTemplate = ''
    _chapterTemplate = ''
    _notesChapterTemplate = ''
    _todoChapterTemplate = ''
    _unusedChapterTemplate = ''
    _notExportedChapterTemplate = ''
    _sceneTemplate = ''
    _firstSceneTemplate = ''
    _appendedSceneTemplate = ''
    _notesSceneTemplate = ''
    _todoSceneTemplate = ''
    _unusedSceneTemplate = ''
    _notExportedSceneTemplate = ''
    _sceneDivider = ''
    _chapterEndTemplate = ''
    _unusedChapterEndTemplate = ''
    _notExportedChapterEndTemplate = ''
    _notesChapterEndTemplate = ''
    _todoChapterEndTemplate = ''
    _characterSectionHeading = ''
    _characterTemplate = ''
    _locationSectionHeading = ''
    _locationTemplate = ''
    _itemSectionHeading = ''
    _itemTemplate = ''
    _fileFooter = ''

    def __init__(self, filePath, **kwargs):
        """Initialize filter strategy class instances.
        
        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        Optional arguments:
            kwargs -- keyword arguments to be used by subclasses.            

        Extends the superclass constructor.
        """
        super().__init__(filePath, **kwargs)
        self._sceneFilter = Filter()
        self._chapterFilter = Filter()
        self._characterFilter = Filter()
        self._locationFilter = Filter()
        self._itemFilter = Filter()

    def merge(self, source):
        """Update instance variables from a source instance.
        
        Positional arguments:
            source -- Novel subclass instance to merge.
        
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """
        if source.title is not None:
            self.title = source.title
        else:
            self.title = ''

        if source.desc is not None:
            self.desc = source.desc
        else:
            self.desc = ''

        if source.authorName is not None:
            self.authorName = source.authorName
        else:
            self.authorName = ''

        if source.authorBio is not None:
            self.authorBio = source.authorBio
        else:
            self.authorBio = ''

        if source.fieldTitle1 is not None:
            self.fieldTitle1 = source.fieldTitle1
        else:
            self.fieldTitle1 = 'Field 1'
        
        if source.fieldTitle2 is not None:
            self.fieldTitle2 = source.fieldTitle2
        else:
            self.fieldTitle2 = 'Field 2'
        
        if source.fieldTitle3 is not None:
            self.fieldTitle3 = source.fieldTitle3
        else:
            self.fieldTitle3 = 'Field 3'
        
        if source.fieldTitle4 is not None:
            self.fieldTitle4 = source.fieldTitle4
        else:
            self.fieldTitle4 = 'Field 4'
        
        if source.srtChapters:
            self.srtChapters = source.srtChapters
        
        if source.scenes is not None:
            self.scenes = source.scenes
        
        if source.chapters is not None:
            self.chapters = source.chapters
        
        if source.srtCharacters:
            self.srtCharacters = source.srtCharacters
            self.characters = source.characters
        
        if source.srtLocations:
            self.srtLocations = source.srtLocations
            self.locations = source.locations
        
        if source.srtItems:
            self.srtItems = source.srtItems
            self.items = source.items
        return 'Export data updated from novel.'

    def _get_fileHeaderMapping(self):
        """Return a mapping dictionary for the project section.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        projectTemplateMapping = dict(
            Title=self._convert_from_yw(self.title, True),
            Desc=self._convert_from_yw(self.desc),
            AuthorName=self._convert_from_yw(self.authorName, True),
            AuthorBio=self._convert_from_yw(self.authorBio, True),
            FieldTitle1=self._convert_from_yw(self.fieldTitle1, True),
            FieldTitle2=self._convert_from_yw(self.fieldTitle2, True),
            FieldTitle3=self._convert_from_yw(self.fieldTitle3, True),
            FieldTitle4=self._convert_from_yw(self.fieldTitle4, True),
        )
        return projectTemplateMapping

    def _get_chapterMapping(self, chId, chapterNumber):
        """Return a mapping dictionary for a chapter section.
        
        Positional arguments:
            chId -- str: chapter ID.
            chapterNumber -- int: chapter number.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        if chapterNumber == 0:
            chapterNumber = ''
        
        chapterMapping = dict(
            ID=chId,
            ChapterNumber=chapterNumber,
            Title=self._convert_from_yw(self.chapters[chId].title, True),
            Desc=self._convert_from_yw(self.chapters[chId].desc),
            ProjectName=self._convert_from_yw(self.projectName, True),
            ProjectPath=self.projectPath,
        )
        return chapterMapping

    def _get_sceneMapping(self, scId, sceneNumber, wordsTotal, lettersTotal):
        """Return a mapping dictionary for a scene section.
        
        Positional arguments:
            scId -- str: scene ID.
            sceneNumber -- int: scene number to be displayed.
            wordsTotal -- int: accumulated wordcount.
            lettersTotal -- int: accumulated lettercount.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        
        #--- Create a comma separated tag list.
        if sceneNumber == 0:
            sceneNumber = ''
        if self.scenes[scId].tags is not None:
            tags = self._get_string(self.scenes[scId].tags)
        else:
            tags = ''

        #--- Create a comma separated character list.
        try:
            # Note: Due to a bug, yWriter scenes might hold invalid
            # viepoint characters
            sChList = []
            for chId in self.scenes[scId].characters:
                sChList.append(self.characters[chId].title)
            sceneChars = self._get_string(sChList)
            viewpointChar = sChList[0]
        except:
            sceneChars = ''
            viewpointChar = ''

        #--- Create a comma separated location list.
        if self.scenes[scId].locations is not None:
            sLcList = []
            for lcId in self.scenes[scId].locations:
                sLcList.append(self.locations[lcId].title)
            sceneLocs = self._get_string(sLcList)
        else:
            sceneLocs = ''

        #--- Create a comma separated item list.
        if self.scenes[scId].items is not None:
            sItList = []
            for itId in self.scenes[scId].items:
                sItList.append(self.items[itId].title)
            sceneItems = self._get_string(sItList)
        else:
            sceneItems = ''

        #--- Create A/R marker string.
        if self.scenes[scId].isReactionScene:
            reactionScene = Scene.REACTION_MARKER
        else:
            reactionScene = Scene.ACTION_MARKER

        #--- Create a combined scDate information.
        if self.scenes[scId].date is not None and self.scenes[scId].date != Scene.NULL_DATE:
            scDay = ''
            scDate = self.scenes[scId].date
            cmbDate = self.scenes[scId].date
        else:
            scDate = ''
            if self.scenes[scId].day is not None:
                scDay = self.scenes[scId].day
                cmbDate = f'Day {self.scenes[scId].day}'
            else:
                scDay = ''
                cmbDate = ''

        #--- Create a combined time information.
        if self.scenes[scId].time is not None and self.scenes[scId].date != Scene.NULL_DATE:
            scHour = ''
            scMinute = ''
            scTime = self.scenes[scId].time
            cmbTime = self.scenes[scId].time.rsplit(':', 1)[0]
        else:
            scTime = ''
            if self.scenes[scId].hour or self.scenes[scId].minute:
                if self.scenes[scId].hour:
                    scHour = self.scenes[scId].hour
                else:
                    scHour = '00'
                if self.scenes[scId].minute:
                    scMinute = self.scenes[scId].minute
                else:
                    scMinute = '00'
                cmbTime = f'{scHour.zfill(2)}:{scMinute.zfill(2)}'
            else:
                scHour = ''
                scMinute = ''
                cmbTime = ''

        #--- Create a combined duration information.
        if self.scenes[scId].lastsDays is not None and self.scenes[scId].lastsDays != '0':
            lastsDays = self.scenes[scId].lastsDays
            days = f'{self.scenes[scId].lastsDays}d '
        else:
            lastsDays = ''
            days = ''
        if self.scenes[scId].lastsHours is not None and self.scenes[scId].lastsHours != '0':
            lastsHours = self.scenes[scId].lastsHours
            hours = f'{self.scenes[scId].lastsHours}h '
        else:
            lastsHours = ''
            hours = ''
        if self.scenes[scId].lastsMinutes is not None and self.scenes[scId].lastsMinutes != '0':
            lastsMinutes = self.scenes[scId].lastsMinutes
            minutes = f'{self.scenes[scId].lastsMinutes}min'
        else:
            lastsMinutes = ''
            minutes = ''
        duration = f'{days}{hours}{minutes}'
        
        sceneMapping = dict(
            ID=scId,
            SceneNumber=sceneNumber,
            Title=self._convert_from_yw(self.scenes[scId].title, True),
            Desc=self._convert_from_yw(self.scenes[scId].desc),
            WordCount=str(self.scenes[scId].wordCount),
            WordsTotal=wordsTotal,
            LetterCount=str(self.scenes[scId].letterCount),
            LettersTotal=lettersTotal,
            Status=Scene.STATUS[self.scenes[scId].status],
            SceneContent=self._convert_from_yw(self.scenes[scId].sceneContent),
            FieldTitle1=self._convert_from_yw(self.fieldTitle1, True),
            FieldTitle2=self._convert_from_yw(self.fieldTitle2, True),
            FieldTitle3=self._convert_from_yw(self.fieldTitle3, True),
            FieldTitle4=self._convert_from_yw(self.fieldTitle4, True),
            Field1=self.scenes[scId].field1,
            Field2=self.scenes[scId].field2,
            Field3=self.scenes[scId].field3,
            Field4=self.scenes[scId].field4,
            Date=scDate,
            Time=scTime,
            Day=scDay,
            Hour=scHour,
            Minute=scMinute,
            ScDate=cmbDate,
            ScTime=cmbTime,
            LastsDays=lastsDays,
            LastsHours=lastsHours,
            LastsMinutes=lastsMinutes,
            Duration=duration,
            ReactionScene=reactionScene,
            Goal=self._convert_from_yw(self.scenes[scId].goal),
            Conflict=self._convert_from_yw(self.scenes[scId].conflict),
            Outcome=self._convert_from_yw(self.scenes[scId].outcome),
            Tags=self._convert_from_yw(tags, True),
            Image=self.scenes[scId].image,
            Characters=sceneChars,
            Viewpoint=viewpointChar,
            Locations=sceneLocs,
            Items=sceneItems,
            Notes=self._convert_from_yw(self.scenes[scId].sceneNotes),
            ProjectName=self._convert_from_yw(self.projectName, True),
            ProjectPath=self.projectPath,
        )
        return sceneMapping

    def _get_characterMapping(self, crId):
        """Return a mapping dictionary for a character section.
        
        Positional arguments:
            crId -- str: character ID.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        if self.characters[crId].tags is not None:
            tags = self._get_string(self.characters[crId].tags)
        else:
            tags = ''
        if self.characters[crId].isMajor:
            characterStatus = Character.MAJOR_MARKER
        else:
            characterStatus = Character.MINOR_MARKER
        
        characterMapping = dict(
            ID=crId,
            Title=self._convert_from_yw(self.characters[crId].title, True),
            Desc=self._convert_from_yw(self.characters[crId].desc),
            Tags=self._convert_from_yw(tags),
            Image=self.characters[crId].image,
            AKA=self._convert_from_yw(self.characters[crId].aka, True),
            Notes=self._convert_from_yw(self.characters[crId].notes),
            Bio=self._convert_from_yw(self.characters[crId].bio),
            Goals=self._convert_from_yw(self.characters[crId].goals),
            FullName=self._convert_from_yw(self.characters[crId].fullName, True),
            Status=characterStatus,
            ProjectName=self._convert_from_yw(self.projectName),
            ProjectPath=self.projectPath,
        )
        return characterMapping

    def _get_locationMapping(self, lcId):
        """Return a mapping dictionary for a location section.
        
        Positional arguments:
            lcId -- str: location ID.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        if self.locations[lcId].tags is not None:
            tags = self._get_string(self.locations[lcId].tags)
        else:
            tags = ''
        
        locationMapping = dict(
            ID=lcId,
            Title=self._convert_from_yw(self.locations[lcId].title, True),
            Desc=self._convert_from_yw(self.locations[lcId].desc),
            Tags=self._convert_from_yw(tags, True),
            Image=self.locations[lcId].image,
            AKA=self._convert_from_yw(self.locations[lcId].aka, True),
            ProjectName=self._convert_from_yw(self.projectName, True),
            ProjectPath=self.projectPath,
        )
        return locationMapping

    def _get_itemMapping(self, itId):
        """Return a mapping dictionary for an item section.
        
        Positional arguments:
            itId -- str: item ID.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        if self.items[itId].tags is not None:
            tags = self._get_string(self.items[itId].tags)
        else:
            tags = ''
        
        itemMapping = dict(
            ID=itId,
            Title=self._convert_from_yw(self.items[itId].title, True),
            Desc=self._convert_from_yw(self.items[itId].desc),
            Tags=self._convert_from_yw(tags, True),
            Image=self.items[itId].image,
            AKA=self._convert_from_yw(self.items[itId].aka, True),
            ProjectName=self._convert_from_yw(self.projectName, True),
            ProjectPath=self.projectPath,
        )
        return itemMapping

    def _get_fileHeader(self):
        """Process the file header.
        
        Apply the file header template, substituting placeholders 
        according to the file header mapping dictionary.
        Return a list of strings.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = []
        template = Template(self._fileHeader)
        lines.append(template.safe_substitute(self._get_fileHeaderMapping()))
        return lines

    def _get_scenes(self, chId, sceneNumber, wordsTotal, lettersTotal, doNotExport):
        """Process the scenes.
        
        Positional arguments:
            chId -- str: chapter ID.
            sceneNumber -- int: number of previously processed scenes.
            wordsTotal -- int: accumulated wordcount of the previous scenes.
            lettersTotal -- int: accumulated lettercount of the previous scenes.
            doNotExport -- bool: scene belongs to a chapter that is not to be exported.
        
        Iterate through a sorted scene list and apply the templates, 
        substituting placeholders according to the scene mapping dictionary.
        Skip scenes not accepted by the scene filter.
        
        Return a tuple:
            lines -- list of strings: the lines of the processed scene.
            sceneNumber -- int: number of all processed scenes.
            wordsTotal -- int: accumulated wordcount of all processed scenes.
            lettersTotal -- int: accumulated lettercount of all processed scenes.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = []
        firstSceneInChapter = True
        for scId in self.chapters[chId].srtScenes:
            dispNumber = 0
            if not self._sceneFilter.accept(self, scId):
                continue
            # The order counts; be aware that "Todo" and "Notes" scenes are
            # always unused.
            if self.scenes[scId].isTodoScene:
                if self._todoSceneTemplate:
                    template = Template(self._todoSceneTemplate)
                else:
                    continue

            elif self.scenes[scId].isNotesScene:
                # Scene is "Notes" type.
                if self._notesSceneTemplate:
                    template = Template(self._notesSceneTemplate)
                else:
                    continue

            elif self.scenes[scId].isUnused or self.chapters[chId].isUnused:
                if self._unusedSceneTemplate:
                    template = Template(self._unusedSceneTemplate)
                else:
                    continue

            elif self.chapters[chId].oldType == 1:
                # Scene is "Info" type (old file format).
                if self._notesSceneTemplate:
                    template = Template(self._notesSceneTemplate)
                else:
                    continue

            elif self.scenes[scId].doNotExport or doNotExport:
                if self._notExportedSceneTemplate:
                    template = Template(self._notExportedSceneTemplate)
                else:
                    continue

            else:
                sceneNumber += 1
                dispNumber = sceneNumber
                wordsTotal += self.scenes[scId].wordCount
                lettersTotal += self.scenes[scId].letterCount
                template = Template(self._sceneTemplate)
                if not firstSceneInChapter and self.scenes[scId].appendToPrev and self._appendedSceneTemplate:
                    template = Template(self._appendedSceneTemplate)
            if not (firstSceneInChapter or self.scenes[scId].appendToPrev):
                lines.append(self._sceneDivider)
            if firstSceneInChapter and self._firstSceneTemplate:
                template = Template(self._firstSceneTemplate)
            lines.append(template.safe_substitute(self._get_sceneMapping(
                        scId, dispNumber, wordsTotal, lettersTotal)))
            firstSceneInChapter = False
        return lines, sceneNumber, wordsTotal, lettersTotal

    def _get_chapters(self):
        """Process the chapters and nested scenes.
        
        Iterate through the sorted chapter list and apply the templates, 
        substituting placeholders according to the chapter mapping dictionary.
        For each chapter call the processing of its included scenes.
        Skip chapters not accepted by the chapter filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = []
        chapterNumber = 0
        sceneNumber = 0
        wordsTotal = 0
        lettersTotal = 0
        for chId in self.srtChapters:
            dispNumber = 0
            if not self._chapterFilter.accept(self, chId):
                continue

            # The order counts; be aware that "Todo" and "Notes" chapters are
            # always unused.
            # Has the chapter only scenes not to be exported?
            sceneCount = 0
            notExportCount = 0
            doNotExport = False
            template = None
            for scId in self.chapters[chId].srtScenes:
                sceneCount += 1
                if self.scenes[scId].doNotExport:
                    notExportCount += 1
            if sceneCount > 0 and notExportCount == sceneCount:
                doNotExport = True
            if self.chapters[chId].chType == 2:
                # Chapter is "ToDo" type (implies "unused").
                if self._todoChapterTemplate:
                    template = Template(self._todoChapterTemplate)
            elif self.chapters[chId].chType == 1:
                # Chapter is "Notes" type (implies "unused").
                if self._notesChapterTemplate:
                    template = Template(self._notesChapterTemplate)
            elif self.chapters[chId].isUnused:
                # Chapter is "really" unused.
                if self._unusedChapterTemplate:
                    template = Template(self._unusedChapterTemplate)
            elif self.chapters[chId].oldType == 1:
                # Chapter is "Info" type (old file format).
                if self._notesChapterTemplate:
                    template = Template(self._notesChapterTemplate)
            elif doNotExport:
                if self._notExportedChapterTemplate:
                    template = Template(self._notExportedChapterTemplate)
            elif self.chapters[chId].chLevel == 1 and self._partTemplate:
                template = Template(self._partTemplate)
            else:
                template = Template(self._chapterTemplate)
                chapterNumber += 1
                dispNumber = chapterNumber
            if template is not None:
                lines.append(template.safe_substitute(self._get_chapterMapping(chId, dispNumber)))

            #--- Process scenes.
            sceneLines, sceneNumber, wordsTotal, lettersTotal = self._get_scenes(
                chId, sceneNumber, wordsTotal, lettersTotal, doNotExport)
            lines.extend(sceneLines)

            #--- Process chapter ending.
            template = None
            if self.chapters[chId].chType == 2:
                if self._todoChapterEndTemplate:
                    template = Template(self._todoChapterEndTemplate)
            elif self.chapters[chId].chType == 1:
                if self._notesChapterEndTemplate:
                    template = Template(self._notesChapterEndTemplate)
            elif self.chapters[chId].isUnused:
                if self._unusedChapterEndTemplate:
                    template = Template(self._unusedChapterEndTemplate)
            elif self.chapters[chId].oldType == 1:
                if self._notesChapterEndTemplate:
                    template = Template(self._notesChapterEndTemplate)
            elif doNotExport:
                if self._notExportedChapterEndTemplate:
                    template = Template(self._notExportedChapterEndTemplate)
            elif self._chapterEndTemplate:
                template = Template(self._chapterEndTemplate)
            if template is not None:
                lines.append(template.safe_substitute(self._get_chapterMapping(chId, dispNumber)))
        return lines

    def _get_characters(self):
        """Process the characters.
        
        Iterate through the sorted character list and apply the template, 
        substituting placeholders according to the character mapping dictionary.
        Skip characters not accepted by the character filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        if self._characterSectionHeading:
            lines = [self._characterSectionHeading]
        else:
            lines = []
        template = Template(self._characterTemplate)
        for crId in self.srtCharacters:
            if self._characterFilter.accept(self, crId):
                lines.append(template.safe_substitute(self._get_characterMapping(crId)))
        return lines

    def _get_locations(self):
        """Process the locations.
        
        Iterate through the sorted location list and apply the template, 
        substituting placeholders according to the location mapping dictionary.
        Skip locations not accepted by the location filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        if self._locationSectionHeading:
            lines = [self._locationSectionHeading]
        else:
            lines = []
        template = Template(self._locationTemplate)
        for lcId in self.srtLocations:
            if self._locationFilter.accept(self, lcId):
                lines.append(template.safe_substitute(self._get_locationMapping(lcId)))
        return lines

    def _get_items(self):
        """Process the items. 
        
        Iterate through the sorted item list and apply the template, 
        substituting placeholders according to the item mapping dictionary.
        Skip items not accepted by the item filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        if self._itemSectionHeading:
            lines = [self._itemSectionHeading]
        else:
            lines = []
        template = Template(self._itemTemplate)
        for itId in self.srtItems:
            if self._itemFilter.accept(self, itId):
                lines.append(template.safe_substitute(self._get_itemMapping(itId)))
        return lines

    def _get_text(self):
        """Call all processing methods.
        
        Return a string to be written to the output file.
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = self._get_fileHeader()
        lines.extend(self._get_chapters())
        lines.extend(self._get_characters())
        lines.extend(self._get_locations())
        lines.extend(self._get_items())
        lines.append(self._fileFooter)
        return ''.join(lines)

    def write(self):
        """Write instance variables to the export file.
        
        Create a template-based output file. 
        Return a message beginning with the ERROR constant in case of error.
        """
        text = self._get_text()
        backedUp = False
        if os.path.isfile(self.filePath):
            try:
                os.replace(self.filePath, f'{self.filePath}.bak')
                backedUp = True            
            except:
                return f'{ERROR}Cannot overwrite "{os.path.normpath(self.filePath)}".'
            
        try:
            with open(self.filePath, 'w', encoding='utf-8') as f:
                f.write(text)
        except:
            if backedUp:
                os.replace(f'{self.filePath}.bak', self.filePath)
            return f'{ERROR}Cannot write "{os.path.normpath(self.filePath)}".'

        return f'"{os.path.normpath(self.filePath)}" written.'

    def _get_string(self, elements):
        """Join strings from a list.
        
        Return a string which is the concatenation of the 
        members of the list of strings "elements", separated by 
        a comma plus a space. The space allows word wrap in 
        spreadsheet cells.
        """
        text = (', ').join(elements)
        return text

    def _convert_from_yw(self, text, quick=False):
        """Return text, converted from yw7 markup to target format.
        
        Positional arguments:
            text -- string to convert.
        
        Optional arguments:
            quick -- bool: if True, apply a conversion mode for one-liners without formatting.
        
        Overrides the superclass method.
        """
        if text is None:
            text = ''
        return(text)


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


class MdFullSynopsis(MdAeon):
    """Markdown scene summaries file representation.

    Export a full synopsis.
    """
    DESCRIPTION = 'Full synopsis'
    SUFFIX = '_full_synopsis'

    _partTemplate = '''# $Title
    
'''

    _chapterTemplate = '''## $Title
    
'''

    _sceneTemplate = '''<!--- $Title --->

$Desc

'''

    _sceneDivider = '''* * *

'''


class MdBrieflSynopsis(MdAeon):
    """Markdown chapter summaries snf scene titles file representation.

    Export a brief synopsis.
    """
    DESCRIPTION = 'Brief synopsis'
    SUFFIX = '_brief_synopsis'

    _partTemplate = '''# $Desc

'''

    _chapterTemplate = '''## $Desc
    
'''

    _sceneTemplate = '''$Title
    
'''


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


class MdCharacterSheets(MdAeon):
    """Markdown character descriptions file representation.

    Export a character sheet.
    """
    DESCRIPTION = 'Character sheets'
    SUFFIX = '_character_sheets'

    _characterTemplate = '''## $Title$FullName$AKA

**Tags:** $Tags


$Bio


$Goals


$Desc


$Notes

'''


class MdLocationSheets(MdAeon):
    """Markdown location descriptions file representation.

    Export a location sheet.
    """
    DESCRIPTION = 'Location sheets'
    SUFFIX = '_location_sheets'

    _locationTemplate = '''## $Title$AKA
    
    
**Tags:** $Tags

$Desc

'''


class MdReport(MdAeon):
    """Markdown scene summaries file representation.

    Export a full synopsis.
    """
    DESCRIPTION = 'Project report'
    SUFFIX = '_report'

    _partTemplate = '''# $Title – $Desc
    
'''

    _chapterTemplate = '''## $Title – $Desc
    
'''

    _sceneTemplate = '''### Scene $SceneNumber – ${Title}
    
**Tags:** $Tags


**Location:** $Locations


**Date/Time/Duration:** $ScDate $ScTime $Duration


**Participants:** $Characters


$Desc


**Notes:** $Notes

'''

    _characterSectionHeading = '''# Characters
    
'''

    _characterTemplate = '''## $Title$FullName$AKA


**Tags:** $Tags


$Bio


$Goals


$Desc


**Notes:** $Notes

'''

    _locationSectionHeading = '''## Locations

'''

    _locationTemplate = '''## ">$Title$AKA
    
**Tags:** $Tags


$Desc

'''


class Aeon3mdConverter(YwCnvFf):
    """A converter for universal export from a yWriter 7 project.

    Overrides the superclass constants EXPORT_SOURCE_CLASSES,
    EXPORT_TARGET_CLASSES.
    """
    EXPORT_SOURCE_CLASSES = [CsvTimeline3, JsonTimeline3]
    EXPORT_TARGET_CLASSES = [MdFullSynopsis,
                             MdBrieflSynopsis,
                             MdChapterOverview,
                             MdCharacterSheets,
                             MdLocationSheets,
                             MdReport,
                             ]

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

