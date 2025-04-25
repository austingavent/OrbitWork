---
object: index
created: {{date}}
---

# {{folder_name}} Directory Index

This is an auto-generated index file for the Folder Note plugin.

## Contents

```dataview
TABLE object, created, orbits as "Parent Projects"
FROM "{{path}}"
WHERE file.name != ".index"
SORT file.name ASC
```

## Subdirectories

```dataview
TABLE object, created
FROM "{{path}}"
WHERE file.name != ".index" AND object = "index"
SORT file.name ASC
```

## Statistics

- Total notes: {{note_count}}
- Last updated: {{date}}
```

## Create

```button
name Create Relating Note
type append template
action C1yaml
```

```button
name Create Satelliting Directory 
type append template
action Create Satelliting Directory
```

```button
name Create Orbiting Directory
type append template
action Create Orbiting Directory
```
