<%*
/* Create ORBIT System Navigation Dashboard */
try {
  // Get vault path
  const vaultPath = app.vault.adapter.basePath;
  
  // Define dashboard path
  const dashboardPath = "ORBIT-Navigation.md";
  
  // Check if it already exists
  const exists = await app.vault.adapter.exists(dashboardPath);
  if (exists) {
    new Notice("ORBIT Navigation dashboard already exists");
    
    // Open the existing dashboard
    const dashboardFile = app.vault.getAbstractFileByPath(dashboardPath);
    if (dashboardFile) {
      await app.workspace.getLeaf().openFile(dashboardFile);
    }
    return;
  }
  
  // Get list of domain directories
  const files = await app.vault.adapter.list("");
  const domainDirs = files.folders
    .map(folder => folder.split('/')[0])
    .filter(dir => dir.match(/^[0-9]-/))
    .sort();
  
  // Create dashboard content
  let dashboardContent = `---
object: dashboard
created: ${tp.file.creation_date("YYYY-MM-DD")}
---

# ORBIT Navigation Dashboard

## Domains

`;

  // Add domain links
  for (const domain of domainDirs) {
    const domainNumber = domain.split('-')[0];
    const domainName = domain.split('-')[1];
    dashboardContent += `- [[${domain}/${domainName}|${domainNumber} ${domainName}]]\n`;
  }
  
  // Add create buttons
  dashboardContent += `
## Quick Access

\`\`\`dataview
TABLE object, created, orbits as "Parent Projects"
FROM "0-Origins/.0-inbox"
WHERE object != "index"
SORT created DESC
LIMIT 5
\`\`\`

## Create New Content

\`\`\`button
name Create Domain Dashboard
type append template
action Create Domain Dashboard
\`\`\`

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

\`\`\`button
name Create Folder Note
type append template
action Create Folder Note
\`\`\`

## ORBIT System Stats

\`\`\`dataview
TABLE length(rows) as "Count"
FROM ""
GROUP BY object
SORT Count DESC
\`\`\`

\`\`\`dataview
TABLE length(rows) as "Count"
FROM ""
GROUP BY stage
SORT stage ASC
\`\`\`

## Recent Activity

\`\`\`dataview
TABLE object, orbits as "Projects", stage
FROM ""
WHERE file.mtime >= date(today) - dur(1 week)
SORT file.mtime DESC
LIMIT 10
\`\`\`
`;

  // Create the dashboard file
  await app.vault.create(dashboardPath, dashboardContent);
  
  // Open the newly created dashboard
  const dashboardFile = app.vault.getAbstractFileByPath(dashboardPath);
  if (dashboardFile) {
    await app.workspace.getLeaf().openFile(dashboardFile);
  }
  
  new Notice("Created ORBIT Navigation dashboard");
} catch (error) {
  console.error("Error creating ORBIT dashboard:", error);
  new Notice("Error: " + error.message);
}
%>