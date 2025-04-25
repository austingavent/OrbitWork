# ORBIT System - Knowledge Management for Obsidian

## Overview

The ORBIT system is a hierarchical knowledge management framework for Obsidian that organizes notes based on parent-child relationships. It uses YAML frontmatter to track relationships between notes and automatically manages their locations in the directory structure.

## Key Concepts

- **Orbit**: A parent-child relationship where notes (satellites) revolve around their parent notes (orbits)
- **Stage**: Determines where a note is stored within its parent's structure (.0-inbox, main directory, etc.)
- **Domain**: Top-level categorization (represented by numbered directories like 1-Self, 2-Health, etc.)
- **Objects**: Different types of notes (note, project, source, index, domain)
- **YAML Frontmatter**: Metadata that controls how notes are organized and related

## Directory Structure

```
VAULT_ROOT/
├── 0-Origins/
├── 1-Self/
├── 2-Health/
├── ...
└── 9-Meta_resources/
```

Each domain directory can contain:
- Projects (orbits)
- Notes (satellites)
- Sources
- Inbox directories (.0-inbox)

## Button Templates

The system includes three main button templates that can be added to any page:

1. **Create Relating Note** - Creates a new note that references (orbits) the current project
2. **Create Satelliting Directory** - Creates a new subdirectory within the current directory
3. **Create Orbiting Directory** - Creates a new parent directory and moves the current directory into it

## Getting Started

1. Configure your vault path in `orbit_config.py`.

2. Run the setup script to create the basic structure:
   ```
   python orbit_setup.py
   ```
   
   The setup script will:
   - Create the domain directories and structure
   - Create template files
   - Copy your existing Obsidian configuration from the specified source
   - Create navigation files and indexes

3. Start the watchdog to monitor your vault:
   ```
   python orbit_watchdog.py
   ```

4. Use the templates to create new notes and directories:
   - Navigate to a project or domain page
   - Use the buttons at the bottom of the page to create new content

## Obsidian Configuration

The system will automatically copy an existing Obsidian configuration from:
```
/Users/austinavent/Library/CloudStorage/Dropbox/Areas/DASR/DASR/.obsidian
```

This preserves your existing Obsidian settings, themes, and plugins. The setup script will:
1. Back up any existing .obsidian folder in your target vault
2. Copy the configuration folder to your vault
3. Check for required plugins

## YAML Frontmatter Properties

Every note in the ORBIT system should have these properties in its YAML frontmatter:

```yaml
---
object: note          # Type of object (note, project, source, index, domain)
created: 2025-04-25   # Creation date
domain: 1-Self        # The domain this note belongs to
orbits: ["Project"]   # Parent note(s) this note revolves around
stage: 0              # Development stage (0=inbox, 1=seedling, etc.)
---
```

Projects may also have:
```yaml
satellites: []        # List of child notes/projects
```

## Working with the System

### Creating a New Project
1. Navigate to a domain dashboard
2. Click "Create Satelliting Directory"
3. Enter a name for your project

### Creating a Note Within a Project
1. Navigate to the project page
2. Click "Create Relating Note"
3. Enter a title for your note
4. The note will be automatically placed in the project's inbox

### Creating a Parent Project
1. Navigate to an existing project
2. Click "Create Orbiting Directory"
3. Enter a name for the parent project
4. The current project will be moved to become a child of the new parent

## Automatic Organization

The watchdog script monitors for changes to notes and automatically:
- Moves notes to the appropriate directories based on their orbit and stage properties
- Places source notes in the source directory of their parent project
- Handles notes without explicit orbits

## Customization

You can customize the system by editing the `orbit_config.py` file:
- Change domain names and numbering
- Adjust stage directories
- Modify property names
- Update file paths

## Troubleshooting

- Check the `orbit_manager.log` file for error messages
- Ensure your notes have proper YAML frontmatter
- Make sure the watchdog script is running
- Verify folder permissions allow the script to move files
- If your Obsidian configuration isn't working correctly, check that all required plugins are installed

## Required Plugins

The system works best with these Obsidian plugins:
- **Templater** - For using the template files
- **Buttons** - For the action buttons on pages
- **Folder Note Core** - For associating index files with folders

## Dependencies

- Python 3.6+
- PyYAML
- Watchdog
- Obsidian with required plugins

## License

This system is free to use and modify for personal knowledge management.

---

*Happy organizing!*