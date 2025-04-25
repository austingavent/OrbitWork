<%*
/* Create Orbiting Directory (Parent Orbit) and Move Current Directory */
try {
  // Get current file information
  const currentFile = app.workspace.getActiveFile();
  const currentDir = tp.file.folder(true);
  const currentDirName = currentDir.split('/').pop();
  
  // Get parent directory (where we'll create the new orbit)
  const parentDir = currentDir.substring(0, currentDir.lastIndexOf('/'));
  
  // Log start of process
  console.log("Starting orbiting directory creation");
  console.log("Current directory:", currentDir);
  console.log("Parent directory:", parentDir);
  
  // Prompt for orbit name
  let orbitName = await tp.system.prompt("Enter orbiting directory name");
  if (!orbitName) return; // User cancelled
  
  // Basic sanitization
  orbitName = orbitName.replace(/\s+/g, '-').toLowerCase();
  
  // Create full orbit directory path
  const orbitPath = parentDir + "/" + orbitName;
  console.log("Creating orbit path:", orbitPath);
  
  // Create the directory
  await app.vault.createFolder(orbitPath);
  console.log("Directory created successfully");
  
  // Create index file for folder notes plugin
  const indexContent = `---
object: index
created: ${tp.file.creation_date("YYYY-MM-DD")}
---

# ${orbitName} Directory Index

This is an auto-generated index file for the Folder Note plugin.

## Contents

\`\`\`dataview
TABLE object, created, orbits as "Parent Projects"
FROM "${orbitPath.replace(/\\/g, "/")}"
WHERE file.name != ".index"
SORT file.name ASC
\`\`\`

## Subdirectories

\`\`\`dataview
TABLE object, created
FROM "${orbitPath.replace(/\\/g, "/")}"
WHERE file.name != ".index" AND object = "index"
SORT file.name ASC
\`\`\`

## Statistics

- Total notes: 0
- Last updated: ${tp.file.creation_date("YYYY-MM-DD")}
`;

  // Create hidden index file
  await app.vault.create(orbitPath + "/.index.md", indexContent);
  console.log("Index file created successfully");
  
  // Create main page for the orbit
  const mainContent = `---
object: project
created: ${tp.file.creation_date("YYYY-MM-DD")}
satellites: ["${currentDirName}"]
domain: ${parentDir.split('/').pop()}
orbits: []
stage: 1
---

# ${orbitName} Project

## Overview

Project dashboard for ${orbitName}.

## Satellites

\`\`\`dataview
TABLE object, created
FROM "${orbitPath.replace(/\\/g, "/")}"
WHERE file.name != ".index" AND file.name != "${orbitName}"
SORT file.name ASC
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
  await app.vault.create(orbitPath + "/" + orbitName + ".md", mainContent);
  console.log("Main page created successfully");
  
  // Create inbox directory
  await app.vault.createFolder(orbitPath + "/.0-inbox");
  
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
FROM "${orbitPath.replace(/\\/g, "/")}/.0-inbox"
WHERE object != null AND object != "index"
SORT created DESC
\`\`\`

## Statistics

- Total notes: 0
- Last updated: ${tp.file.creation_date("YYYY-MM-DD")}
`;

  // Create hidden index file for inbox
  await app.vault.create(orbitPath + "/.0-inbox/.index.md", inboxIndexContent);
  console.log("Inbox created successfully");
  
  // Step: Update the current directory's main file to reference the new parent orbit
  // First, find the main file for the current directory (same name as directory)
  const currentMainFileName = currentDirName + ".md";
  const currentMainFilePath = currentDir + "/" + currentMainFileName;
  const currentMainFile = app.vault.getAbstractFileByPath(currentMainFilePath);
  
  if (currentMainFile) {
    // Read current main file content
    const mainFileContent = await app.vault.read(currentMainFile);
    console.log("Read current directory's main file content");
    
    // Parse frontmatter
    const frontmatterRegex = /^---\n([\s\S]*?)\n---/;
    const frontmatterMatch = mainFileContent.match(frontmatterRegex);
    
    if (frontmatterMatch) {
      // File has frontmatter, update it
      const frontmatter = frontmatterMatch[1];
      const frontmatterLines = frontmatter.split('\n');
      
      // Create a modified frontmatter with updated orbits
      let updatedFrontmatter = '';
      let orbitsFound = false;
      
      for (const line of frontmatterLines) {
        if (line.startsWith('orbits:')) {
          // Replace orbits line
          updatedFrontmatter += `orbits: ["${orbitName}"]\n`;
          orbitsFound = true;
        } else {
          updatedFrontmatter += line + '\n';
        }
      }
      
      // If orbits wasn't found, add it
      if (!orbitsFound) {
        updatedFrontmatter += `orbits: ["${orbitName}"]\n`;
      }
      
      // Replace old frontmatter with new
      const newMainContent = mainFileContent.replace(frontmatterRegex, `---\n${updatedFrontmatter}---`);
      
      // Update file content before moving
      await app.vault.modify(currentMainFile, newMainContent);
      console.log("Updated the main file with new orbits reference");
      
      // Move the entire directory to the new orbit
      // Define target path
      const targetPath = orbitPath + "/" + currentDirName;
      console.log("Target path for directory move:", targetPath);
      
      try {
        // Move directory using the fileManager
        // @ts-ignore
        await app.fileManager.renameFile(app.vault.getAbstractFileByPath(currentDir), targetPath);
        console.log("Moved directory to new orbit successfully");
        
        // Open the orbit's main page
        const mainFile = app.vault.getAbstractFileByPath(orbitPath + "/" + orbitName + ".md");
        if (mainFile) {
          await app.workspace.getLeaf().openFile(mainFile);
          console.log("Opened main page");
        }
        
        // Also open the moved directory's main file
        const movedMainFile = app.vault.getAbstractFileByPath(targetPath + "/" + currentMainFileName);
        if (movedMainFile) {
          await app.workspace.getLeaf('split').openFile(movedMainFile);
          console.log("Opened moved directory's main page in split view");
        }
        
        new Notice(`Created orbiting directory '${orbitName}' and moved '${currentDirName}' into it`);
      } catch (moveError) {
        console.error("Error moving directory:", moveError);
        new Notice("Error moving directory: " + moveError.message);
      }
    } else {
      new Notice("Current directory main file has no frontmatter to update");
    }
  } else {
    new Notice("Could not find main file for current directory");
  }
} catch (error) {
  console.error("Error creating orbiting directory:", error);
  new Notice("Error: " + error.message);
}
%>