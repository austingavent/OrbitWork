<%*
/* Set Stage for Note in ORBIT System */
try {
  // Get the current file
  const currentFile = app.workspace.getActiveFile();
  if (!currentFile) {
    new Notice("No active file");
    return;
  }
  
  // Read current file content
  const fileContent = await app.vault.read(currentFile);
  
  // Parse frontmatter
  const frontmatterRegex = /^---\n([\s\S]*?)\n---/;
  const frontmatterMatch = fileContent.match(frontmatterRegex);
  
  if (!frontmatterMatch) {
    new Notice("No frontmatter found in current file");
    return;
  }
  
  // Get current stage
  const stageLine = frontmatterMatch[1].split('\n').find(line => line.startsWith('stage:'));
  const currentStage = stageLine ? stageLine.split(':')[1].trim() : "not set";
  
  // Stage definitions
  const stageOptions = [
    { value: "0", label: "0 - Inbox/Initial" },
    { value: "1", label: "1 - Seedling/Idea" },
    { value: "2", label: "2 - Development" },
    { value: "3", label: "3 - Organizing" },
    { value: "4", label: "4 - Drafting" },
    { value: "5", label: "5 - Refining" },
    { value: "6", label: "6 - Integration" },
    { value: "7", label: "7 - Review" },
    { value: "8", label: "8 - Final" },
    { value: "9", label: "9 - Archive" }
  ];
  
  // Create suggest options array
  const suggestOptions = stageOptions.map(option => option.label);
  
  // Prompt for new stage
  const selectedOption = await tp.system.suggester(suggestOptions, suggestOptions, false, `Current stage: ${currentStage}`);
  if (!selectedOption) return; // User cancelled
  
  const newStage = selectedOption.split(' - ')[0];
  
  // Update the frontmatter
  let updatedFrontmatter = '';
  let stageFound = false;
  
  // Process each line in the frontmatter
  for (const line of frontmatterMatch[1].split('\n')) {
    if (line.startsWith('stage:')) {
      // Replace stage
      updatedFrontmatter += `stage: ${newStage}\n`;
      stageFound = true;
    } else {
      updatedFrontmatter += line + '\n';
    }
  }
  
  // If stage wasn't found, add it
  if (!stageFound) {
    updatedFrontmatter += `stage: ${newStage}\n`;
  }
  
  // Create updated content
  const updatedContent = fileContent.replace(frontmatterRegex, `---\n${updatedFrontmatter}---`);
  
  // Update file
  await app.vault.modify(currentFile, updatedContent);
  
  new Notice(`Updated stage to ${newStage}`);
  
  // Note: In a complete implementation, this would also trigger the 
  // file movement logic based on the new stage. However, that would 
  // typically be handled by the Python backend (orbit_manager.py).
  // Here we're just updating the YAML frontmatter.
  
} catch (error) {
  console.error("Error setting note stage:", error);
  new Notice("Error: " + error.message);
}
%>