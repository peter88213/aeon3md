# The aeon3md Python script: Convert Aeon Timeline 3 project data to Markdown

For more information, see the [project homepage](https://peter88213.github.io/aeon3md) with description and download instructions.

## Development

*aeon3md* is organized as an Eclipse PyDev project. The official release branch on GitHub is *main*.

## Important

Please note that this script has not yet been extensively tested. To me, it's actually just a proof of concept. I probably won't develop the script further. Feel free to copy the project and modify it to your own liking.

### Conventions

See https://github.com/peter88213/PyWriter/blob/main/docs/conventions.md

Exceptions:
- No localization is required.
- The directory structure is modified to minimize dependencies:

.
└── aeon3md/
    ├── src/
    │   ├── pywriter/
    │   ├── aeon3ywlib/
    │   └── aeon3mdlib/
    ├── test/
    └── tools/ 
        ├── build_aeon3md.py
        ├── build.xml
        └── inliner.py

### Development tools

- [Python](https://python.org) version 3.9.
- [Eclipse IDE](https://eclipse.org) with [PyDev](https://pydev.org) and EGit.
- Apache Ant is used for building the application.

## License

*aeon3md* is distributed under the [MIT License](http://www.opensource.org/licenses/mit-license.php).
