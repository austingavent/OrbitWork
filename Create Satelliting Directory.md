<%*
/* ORBIT Satelliting Directory Creation with Index Files */
try {
  // Get current directory
  const currentDir = tp.file.folder(true);
  
  // Prompt for directory name
  let dirname = await tp.system.prompt("Enter satelliting directory name");
  if (!dirname) return; // User cancelled
  
  // Basic sanitization
  dirname = dirname.replace(/\s+/g, '-').toLowerCase();
  
  // Create full directory path
  const dirPath = currentDir + "/" + dirname;
  
  // Create the directory (by creating a file in it which creates the dir)
  // First create index file for folder notes plugin
  const indexContent = `---
object: index
created: ${tp.file.creation_date("YYYY-MM-DD")}
---

# ${dirname} Directory Index

This is an auto-generated index file for the Folder Note plugin.

## Contents

\`\`\`dataview
TABLE object, created, orbits as "Parent Projects"
FROM "${dirPath.replace(/\\/g, "/")}"
WHERE file.name != ".index"
SORT file.name ASC
\`\`\`

## Subdirectories

\`\`\`dataview
TABLE object, created
FROM "${dirPath.replace(/\\/g, "/")}"
WHERE file.name != ".index" AND object = "index"
SORT file.name ASC
\`\`\`

## Statistics

- Total notes: 0
- Last updated: ${tp.file.creation_date("YYYY-MM-DD")}
`;

  // Create hidden index file
  await app.vault.createFolder(dirPath);
  await app.vault.create(dirPath + "/.index.md", indexContent);
  
  // Create main page for the directory
  const mainContent = `---
object: project
created: ${tp.file.creation_date("YYYY-MM-DD")}
satellites: []
domain: ${currentDir.split('/').pop()}
orbits: []
stage: 1
---

# ${dirname} Project

## Overview

Project dashboard for ${dirname}.

## Sources

\`\`\`dataview
TABLE file.ctime as Created
FROM "${dirPath.replace(/\\/g, "/")}/source"
SORT file.ctime DESC
\`\`\`

## Notes

\`\`\`dataview
TABLE object, file.ctime as Created
FROM "${dirPath.replace(/\\/g, "/")}/0-inbox"
SORT file.ctime DESC
\`\`\`

## Create New Note

This section contains buttons to create new notes in this project:

\`\`\`button
name Create Relating Note
type append template
action C1yaml
\`\`\`

\`\`\`button
name Create Satelliting Directory 
type append template
action Create Satelliting Directory
\`\`\`

\`\`\`button
name Create Orbiting Directory
type append template
action Create Orbiting Directory
\`\`\`
`;

  // Create main page file
  await app.vault.create(dirPath + "/" + dirname + ".md", mainContent);
  
  // Create inbox directory
  await app.vault.createFolder(dirPath + "/.0-inbox");
  
  // Create inbox index
  const inboxIndexContent = `---
object: index
created: ${tp.file.creation_date("YYYY-MM-DD")}
---

# Inbox Index

This is an auto-generated index file for the Folder Note plugin.

## Notes Waiting for Processing

\`\`\`dataview
TABLE object, orbits as "Projects", created
FROM "${dirPath.replace(/\\/g, "/")}/.0-inbox"
WHERE object != null AND object != "index"
SORT created DESC
\`\`\`

## Statistics

- Total notes: 0
- Last updated: ${tp.file.creation_date("YYYY-MM-DD")}
`;

  // Create hidden index file for inbox
  await app.vault.create(dirPath + "/.0-inbox/.index.md", inboxIndexContent);
  
  // Open the main page
  const mainFile = app.vault.getAbstractFileByPath(dirPath + "/" + dirname + ".md");
  if (mainFile) {
    await app.workspace.getLeaf().openFile(mainFile);
  }
  
  new Notice(`Created satelliting directory: ${dirname} with index files`);
} catch (error) {
  new Notice("Error creating satelliting directory: " + error.message);
  console.error(error);
}
%>