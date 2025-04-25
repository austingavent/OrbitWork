<%*
/* Create a note with YAML frontmatter for ORBIT system */
try {
  // Get current directory information
  const currentDir = tp.file.folder(true);
  const currentDirName = currentDir.split('/').pop();
  
  // Prompt for note title
  let noteTitle = await tp.system.prompt("Enter note title");
  if (!noteTitle) return; // User cancelled
  
  // Sanitize filename
  const fileName = noteTitle.replace(/[\\/:*?"<>|]/g, '-');
  
  // Prompt for orbit/parent project
  let orbitProject = await tp.system.prompt("Enter orbit/parent project", currentDirName);
  if (!orbitProject) orbitProject = currentDirName;
  
  // Define default YAML frontmatter
  const yamlContent = `---
object: note
created: ${tp.file.creation_date("YYYY-MM-DD")}
domain: ${currentDir.split('/')[0] || ''}
orbits: ["${orbitProject}"]
stage: 0
---

# ${noteTitle}

## Notes

*Your notes about ${noteTitle} here...*

## Relations

- Orbits: [[${orbitProject}]]
`;

  // Create the note file
  const notePath = currentDir + "/.0-inbox/" + fileName + ".md";
  await app.vault.create(notePath, yamlContent);
  
  // Open the newly created note
  const newFile = app.vault.getAbstractFileByPath(notePath);
  if (newFile) {
    await app.workspace.getLeaf().openFile(newFile);
  }
  
  new Notice(`Created new relating note: ${noteTitle} orbiting ${orbitProject}`);
} catch (error) {
  console.error("Error creating relating note:", error);
  new Notice("Error: " + error.message);
}
%>