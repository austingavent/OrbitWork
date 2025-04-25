import os
import sys
import shutil
import time
from pathlib import Path
import logging
import yaml
from datetime import datetime
from orbit_config import config

# Setup logging
logging.basicConfig(
    level=getattr(logging, config["log_level"]),
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename=config["log_file"],
    filemode='a'
)
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(getattr(logging, config["log_level"]))
formatter = logging.Formatter('%(asctime)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

def create_directory_structure():
    """Create the basic directory structure for the ORBIT system."""
    vault_path = Path(config["vault_path"])
    
    # Create .orbit directory for system files
    orbit_dir = vault_path / ".orbit"
    orbit_dir.mkdir(exist_ok=True)
    
    # Create fallback directory
    fallback_path = config["get_fallback_path"]()
    fallback_path.mkdir(exist_ok=True, parents=True)
    
    # Ensure Templates directory exists
    templates_dir = vault_path / "Templates"
    templates_dir.mkdir(exist_ok=True)
    
    # Create domain directories with minimal structure
    for domain_num, domain_name in config["domains"].items():
        domain_dir = vault_path / f"{domain_num}-{domain_name}"
        domain_dir.mkdir(exist_ok=True)
        
        # Create domain dashboard file
        create_domain_dashboard(domain_dir, domain_name, domain_num)
        
        # Create the inbox directory in each domain
        inbox_dir = domain_dir / config["hidden_inbox"]
        inbox_dir.mkdir(exist_ok=True)

    # Copy template files to Templates directory (skipped since files are already there)
    # copy_templates(templates_dir)
    
    # Create navigation file
    create_orbit_navigation(vault_path)
    
    logger.info("ORBIT directory structure setup complete!")
    logger.info(f"Vault path: {vault_path}")

def copy_templates(templates_dir):
    """Copy template files from this script's directory to the vault templates directory"""
    script_dir = Path(__file__).parent
    template_source_dir = script_dir / "Templates"
    
    if template_source_dir.exists():
        # Copy each template file
        for template_file in template_source_dir.glob('*.md'):
            dest_file = templates_dir / template_file.name
            try:
                shutil.copy2(template_file, dest_file)
                logger.info(f"Copied template: {template_file.name}")
            except Exception as e:
                logger.error(f"Error copying template {template_file.name}: {str(e)}")
    else:
        logger.warning(f"Template source directory not found: {template_source_dir}")
        print(f"Warning: Template source directory not found. Please make sure the Templates directory exists in: {script_dir}")

def create_domain_dashboard(domain_dir, domain_name, domain_number):
    """Create a domain dashboard file"""
    dashboard_path = domain_dir / f"{domain_name}.md"
    
    if not dashboard_path.exists():
        # Create domain dashboard content
        dashboard_content = f"""---
object: domain
created: {datetime.now().strftime("%Y-%m-%d")}
domain: {domain_name}
track_number: 7
---

# {domain_name} Dashboard

## Overview

Main dashboard for {domain_name} domain.

## Designated Projects

```dataview
TABLE satellites as "Sub-Projects", created
FROM "{str(domain_dir.relative_to(Path(config['vault_path'])))}"
WHERE object = "project" AND contains(file.folder, "{str(domain_dir.relative_to(Path(config['vault_path'])))}")
SORT file.name ASC
```

## Inbox Projects

```dataview
TABLE orbits as "Parent Projects", created
FROM "{str(domain_dir.relative_to(Path(config['vault_path'])))}/.0-inbox"
WHERE object = "project"
SORT file.name ASC
```

## Notes in Inbox

```dataview
TABLE object, orbits as "Projects", created
FROM "{str(domain_dir.relative_to(Path(config['vault_path'])))}/.0-inbox"
WHERE object != "project" AND object != "domain"
SORT created DESC
LIMIT 10
```

## Recent Notes in Projects

```dataview
TABLE object, orbits as "Projects", created
FROM "{str(domain_dir.relative_to(Path(config['vault_path'])))}"
WHERE object != "project" AND object != "domain"
SORT created DESC
LIMIT 10
```

## Create New Project

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
"""
        
        # Write domain dashboard
        dashboard_path.write_text(dashboard_content)
        logger.info(f"Created domain dashboard: {dashboard_path}")

def create_orbit_navigation(vault_path):
    """Create the main navigation file for the ORBIT system."""
    nav_content = """# ORBIT Navigation

## Domains
"""
    
    # Add domain navigation
    for domain_num, domain_name in config["domains"].items():
        nav_content += f"- [[{domain_num}-{domain_name}/{domain_name}|{domain_num} {domain_name}]]\n"
    
    nav_content += """
## Quick Create

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

## Stage Management
- [[Set Stage to 0|Move to Inbox]]
"""
    
    nav_path = vault_path / "ORBIT-Navigation.md"
    if not nav_path.exists():
        nav_path.write_text(nav_content)
        logger.info(f"Created navigation file: {nav_path}")

def check_required_plugins():
    """Check if the required Obsidian plugins are likely installed"""
    obsidian_config = Path(config["vault_path"]) / ".obsidian"
    plugins_folder = obsidian_config / "plugins"
    
    required_plugins = [
        "templater-obsidian",
        "buttons",
        "folder-note-core"
    ]
    
    if plugins_folder.exists():
        installed_plugins = [d.name for d in plugins_folder.iterdir() if d.is_dir()]
        missing_plugins = [p for p in required_plugins if p not in installed_plugins]
        
        if missing_plugins:
            print("WARNING: The following recommended plugins may not be installed:")
            for plugin in missing_plugins:
                print(f"  - {plugin}")
            print("\nPlease install these plugins in Obsidian for the best experience.")
        else:
            print("All recommended plugins appear to be installed!")
    else:
        print("WARNING: Could not check for installed plugins. .obsidian/plugins folder not found.")
        print("Please ensure you have the following plugins installed:")
        for plugin in required_plugins:
            print(f"  - {plugin}")

def main():
    """Main function to set up the ORBIT system."""
    print("Setting up ORBIT system...")
    
    # Verify vault path
    vault_path = Path(config["vault_path"])
    if not vault_path.exists():
        logger.error(f"Vault path does not exist: {vault_path}")
        print(f"ERROR: Vault path does not exist: {vault_path}")
        print("Please update the VAULT_PATH in orbit_config.py to a valid path.")
        return
    
    # Create basic structure
    try:
        create_directory_structure()
        
        # Check for required plugins
        check_required_plugins()
        
        print("\nORBIT system setup complete!")
        print("\nStructure created:")
        print("- Domain directories (0-Origins, 1-Self, etc.)")
        print("- Inbox directory (.0-inbox) in each domain")
        print("- ORBIT-Navigation.md")
        
        print("\nNext steps:")
        print("1. Ensure your templates are correctly set up in the Templates directory:")
        print("   - C1yaml.md")
        print("   - Create Satelliting Directory.md")
        print("   - Create Orbiting Directory.md")
        print("   - index.md")
        print("2. Start the ORBIT watcher: python orbit_watchdog.py")
        print("3. Create notes with proper frontmatter in your Obsidian vault")
        print("4. The system will automatically organize notes based on their orbits and stage")
        print("5. Use the index template to manually create folder indices when needed")
    
    except KeyboardInterrupt:
        print("\nSetup aborted by user.")
    except Exception as e:
        logger.error(f"Error during setup: {str(e)}")
        print(f"\nERROR during setup: {str(e)}")
        print("Please check the log file for details.")

if __name__ == "__main__":
    main()