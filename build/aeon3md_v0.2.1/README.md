[Project home page](https://peter88213.github.io/aeon3md/) > Main help page

------------------------------------------------------------------------

# Aeon Timeline 3 data conversion

## Usage: 

```
aeon3md.py [-h] [--silent] Sourcefile Suffix

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
```


## Document hierarchy

In the narrative of an **".aeon" project file**, the top three levels of hierarchy are considered. There are two alternatives:

### 1. Three level narrative structure

- First narrative level (narrative folder) = first document level (part).
- Second narrative level (narrative folder) = second document level (chapter).
- Third narrative level (event) = third document level (scene).

### 2. Two level narrative structure

- First narrative level (narrative folder) = second document level (chapter).
- Second narrative level (event) = third document level (scene).

When using a **".csv" export file** instead, the document structure is given by the label in the *Narrative Position* row:

- **Part** = first document level (part).
- **Chapter** = second document level (chapter).
- **Scene** = third document level (scene). 


## Set up your timeline

The *aeon3md* script uses the type designations as defined in Aeon's novel template:

### Types and roles

- **Summary** as detailed description. 
- **Character** as item type for persons.
- **Location** as item type for places.
- **Participant** as character role for scenes.
- **Location** as location role for scenes.

If you use labels other than the ones listed above, you can customize this script by providing an *aeon3yw.ini* configuration file as described in the [aeon3yw](https://peter88213.github.io/aeon3yw/) project.

- Global configuration file on Windows: `c:\Users\<user name>\.pywriter\aeon3yw\config\aeon3yw.ini`
- Local project configuration file name on Windows: `<project directory>\aeon3yw.ini`

### Date/Time

- Scene dates with years that are outside the range of 100--9999 are not shown in the report.
- If there is no scene time set, *00:00:00* may be shown in the reoprt as a substitute.
- If the scene date has no day, *01* may be shown in the report as a substitute. 
- If the scene date has no month, *01* may be shown in the report as a substitute. 

## csv export from Aeon Timeline 3 (optional)

Instead of an *.aeon* file, you can optionally select a *.csv* file exported by Aeon Timeline 3.

- In the "Narrative" settings select **Outline Style** as numbering system. Make sure that at least chapters are auto assigned to *folders*, and scenes are auto assigned to *other types*.

![Screenshot: Narrative settings](https://raw.githubusercontent.com/peter88213/aeon3md/main/docs/Screenshots/narrative_settings.png)

- The csv file exported by Aeon Timeline 3 must be **comma**-separated.
- Make sure all *Item Types for Export* checkboxes are ticked.

![Screenshot: Aeon 3 Export settings](https://raw.githubusercontent.com/peter88213/aeon3md/main/docs/Screenshots/csv_export.png)

------------------------------------------------------------------------

## Markdown reference

By default, *aeon3md* uses a Markdown subset according to the following specificatiions:

### Paragraphs

Paragraphs in Markdown are separated by a blank line.

### Headings

#### Level 1 heading used for parts (chapters marked as beginning of a new section in yWriter)
`# One hash character at the start of the line`

#### Level 2 heading used for chapters
`## Two hash characters at the start of the line`

### Emphasis

#### Italic 
`*single asterisks*`

**Note** : A `*` surrounded with spaces will be treated as a literal asterisk.

#### Bold 
`**double asterisks**`

### Comments

- Comments at the start of a scene are scene titles.

`<!---A HTML comment with one additional hyphen--->`

