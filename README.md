# sb2merge
Merge projects from Scratch, mBlock and so on (*.sb2 files). More info on http://www.algonaut.cz/spoluprace-na-projektech-v-mblock-cooperation-on-mblock-projects/

## Usage:
```
sb2merge.py [--o2a] basePath fileName

--o2a - optional - merge fileName to every other sb2 file in basePath
      - when missing - merge all sb2 files in basePath to fileName (will be stored as merged.sb2)
basePath - directory with sb2 files
fileName - template or target based on --o2a flag
```
