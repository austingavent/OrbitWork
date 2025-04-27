<%*
/* Create Domain Dashboard for ORBIT system with FolderNotes Integration */
try {
  // Prompt for domain number and name
  const domainNumber = await tp.system.prompt("Enter domain number (0-9)");
  if (!domainNumber || !domainNumber.match(/^[0-9]$/)) {
    new Notice("Domain number must be a single digit 0-9");
    return;
  }
  
  const domainName = await tp.system.prompt("Enter domain name");
  if (!domainName) return; // User cancelled
  
  // Sanitize domain name
  const sanitizedDomainName = domainName.replace(/\s+/g, '_');
  
  // Create full domain directory path
  const vaultPath = app.vault.adapter.basePath;
  const domainPath = `${domainNumber}-${sanitizedDomainName}`;
  const fullDomainPath = `${vaultPath}/${domainPath}`;
  
  // Check if domain directory already exists
  if (await app.vault.adapter.exists(domainPath)) {
    new Notice(`Domain ${domainPath} already exists!`);
    
    // Open the existing domain dashboard if it exists
    const dashboardFile = app.vault.getAbstractFileByPath(`${domainPath}/${sanitizedDomainName}.md`);
    if (dashboardFile) {
      await app.workspace.getLeaf().openFile(dashboardFile);
      return;
    }
  } else {
    // Create the domain directory
    await app.vault.createFolder(domainPath);
    console.log(`Created domain directory: ${domainPath}`);
    
    // Create the .0-inbox directory
    await app.vault.createFolder(`${domainPath}/.0-inbox`);
    console.log(`Created inbox directory: ${domainPath}/.0-inbox`);
  }
  
  // Create the FolderNotes index file
  const indexContent = `---
object: index
created: ${tp.file.creation_date("YYYY-MM-DD")}
domain: ${sanitizedDomainName}
---

# ${domainName} Directory Index

This is an auto-generated index file for the Folder Note plugin.

## Projects

\`\`\`dataview
TABLE object, created, satellites
FROM "${domainPath}"
WHERE object = "project"
SORT file.name ASC
\`\`\`

## Recent Files

\`\`\`dataview
TABLE object, created, orbits as "Parent Projects"
FROM "${domainPath}"
WHERE file.name != ".index"
SORT file.ctime DESC
LIMIT 10
\`\`\`

## Statistics

- Total projects: 0
- Last updated: ${tp.file.creation_date("YYYY-MM-DD")}
`;

  // Create the hidden index file
  await app.vault.create(`${domainPath}/.index.md`, indexContent);
  console.log(`Created index file: ${domainPath}/.index.md`);
  
  // Create the inbox index file
  const inboxIndexContent = `---
object: index
created: ${tp.file.creation_date("YYYY-MM-DD")}
---

# Inbox Index

This is an auto-generated index file for the Folder Note plugin.

## Notes Waiting for Processing

\`\`\`dataview
TABLE object, orbits as "Projects", created
FROM "${domainPath}/.0-inbox"
WHERE object != null AND object != "index"
SORT created DESC
\`\`\`

## Statistics

- Total notes: 0
- Last updated: ${tp.file.creation_date("YYYY-MM-DD")}
`;

  // Create the inbox index file
  await app.vault.create(`${domainPath}/.0-inbox/.index.md`, inboxIndexContent);
  console.log(`Created inbox index file: ${domainPath}/.0-inbox/.index.md`);
  
  // Create the domain dashboard file
  const dashboardContent = `---
object: domain
created: ${tp.file.creation_date("YYYY-MM-DD")}
domain: ${sanitizedDomainName}
track_number: 7
stage: 2
---

# ${domainName} Dashboard

## Overview

Main dashboard for ${domainName} domain.

## Designated Projects

\`\`\`dataview
TABLE satellites as "Sub-Projects", created
FROM "${domainPath}"
WHERE object = "project" AND contains(file.folder, "${domainPath}")
SORT file.name ASC
\`\`\`

## Inbox Projects

\`\`\`dataview
TABLE orbits as "Parent Projects", created
FROM "${domainPath}/.0-inbox"
WHERE object = "project"
SORT file.name ASC
\`\`\`

## Notes in Inbox

\`\`\`dataview
TABLE object, orbits as "Projects", created
FROM "${domainPath}/.0-inbox"
WHERE object != "project" AND object != "domain"
SORT created DESC
LIMIT 10
\`\`\`

## Recent Notes in Projects

\`\`\`dataview
TABLE object, orbits as "Projects", created
FROM "${domainPath}"
WHERE object != "project" AND object != "domain"
SORT created DESC
LIMIT 10
\`\`\`

## Create New Project

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

  // Create the dashboard file
  await app.vault.create(`${domainPath}/${sanitizedDomainName}.md`, dashboardContent);
  console.log(`Created dashboard file: ${domainPath}/${sanitizedDomainName}.md`);
  
  // Open the dashboard file
  const dashboardFile = app.vault.getAbstractFileByPath(`${domainPath}/${sanitizedDomainName}.md`);
  if (dashboardFile) {
    await app.workspace.getLeaf().openFile(dashboardFile);
  }
  
  new Notice(`Created domain dashboard for ${domainName}`);
} catch (error) {
  console.error("Error creating domain dashboard:", error);
  new Notice("Error: " + error.message);
}
%>