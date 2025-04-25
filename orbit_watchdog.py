#!/usr/bin/env python3
"""
ORBIT System Watchdog
---------------------
Monitors the Obsidian vault for file changes and triggers the appropriate actions
based on YAML frontmatter properties.
"""

import os
import sys
import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import yaml
import re
import shutil
from datetime import datetime

# Import configuration
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

# Dictionary to track recently modified files and their timestamps
# This helps prevent processing the same file multiple times
recently_modified = {}
DEBOUNCE_SECONDS = config["debounce_time"]

class OrbitFileHandler:
    """Class to handle file operations for the ORBIT system"""
    
    def __init__(self):
        self.vault_path = Path(config["vault_path"])
        logger.info(f"Initializing ORBIT file handler with vault path: {self.vault_path}")
    
    def process_file(self, file_path):
        """Process a file based on its YAML frontmatter"""
        try:
            # Only process markdown files
            if not file_path.endswith('.md'):
                return
            
            # Skip hidden files and index files
            filename = os.path.basename(file_path)
            if filename.startswith('.') or filename == config["hidden_index"]:
                return
            
            # Skip files that don't exist (might have been deleted or moved)
            if not os.path.exists(file_path):
                return
                
            logger.info(f"Processing file: {file_path}")
            
            # Parse frontmatter
            frontmatter = self.parse_frontmatter(file_path)
            if not frontmatter:
                logger.info(f"No frontmatter found in {file_path}, skipping")
                return
            
            # Process based on object type and orbit
            self.handle_file_by_properties(file_path, frontmatter)
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
    
    def parse_frontmatter(self, file_path):
        """Extract YAML frontmatter from a markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for YAML frontmatter
            frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if not frontmatter_match:
                return None
            
            # Parse YAML
            yaml_text = frontmatter_match.group(1)
            frontmatter = yaml.safe_load(yaml_text)
            return frontmatter
            
        except Exception as e:
            logger.error(f"Error parsing frontmatter in {file_path}: {str(e)}")
            return None
    
    def handle_file_by_properties(self, file_path, frontmatter):
        """Handle file based on its frontmatter properties"""
        # Get object type
        object_type = frontmatter.get(config["prop_object"], "note")
        
        # Get orbits (parent projects)
        orbits = frontmatter.get(config["prop_orbit"], [])
        if isinstance(orbits, str):
            orbits = [orbits]  # Convert single string to list
        
        # Get stage
        stage = frontmatter.get(config["prop_stage"], 0)
        
        # Source files go to the source directory
        if object_type == "source":
            logger.info(f"Handling source file: {file_path}")
            self.handle_source_file(file_path, frontmatter, orbits)
        # Files with orbits go to the appropriate orbit directory
        elif orbits:
            logger.info(f"Handling file with orbits: {file_path}, orbits: {orbits}, stage: {stage}")
            self.handle_orbiting_file(file_path, frontmatter, orbits, stage)
        # Handle other files (domain dashboards, etc.)
        else:
            logger.info(f"Handling other file: {file_path}")
            self.handle_other_file(file_path, frontmatter)
    
    def handle_source_file(self, file_path, frontmatter, orbits):
        """Handle source files - move to appropriate source directory"""
        # If the file has orbits, move to the first orbit's source directory
        if orbits:
            orbit_name = orbits[0]
            orbit_path = self.find_orbit_path(orbit_name)
            
            if orbit_path:
                # Create source directory if it doesn't exist
                source_dir = orbit_path / config["source_dir_name"]
                source_dir.mkdir(exist_ok=True)
                
                # Move file to source directory
                self.move_file(file_path, source_dir / os.path.basename(file_path))
            else:
                logger.warning(f"Could not find orbit {orbit_name} for source file {file_path}")
        else:
            # If no orbits, move to domain source directory
            domain = frontmatter.get(config["prop_domain"], "")
            if domain:
                domain_path = self.vault_path / domain
                if domain_path.exists():
                    source_dir = domain_path / config["source_dir_name"]
                    source_dir.mkdir(exist_ok=True)
                    self.move_file(file_path, source_dir / os.path.basename(file_path))
                else:
                    logger.warning(f"Domain {domain} does not exist for source file {file_path}")
            else:
                logger.warning(f"Source file {file_path} has no orbit or domain, leaving in place")
    
    def handle_orbiting_file(self, file_path, frontmatter, orbits, stage):
        """Handle files that orbit other notes/projects"""
        orbit_name = orbits[0]  # Use first orbit in list
        orbit_path = self.find_orbit_path(orbit_name)
        
        if not orbit_path:
            logger.warning(f"Could not find orbit {orbit_name} for file {file_path}")
            return
        
        # Determine target directory based on stage
        if stage == 0 and config["hidden_inbox"]:
            target_dir = orbit_path / config["hidden_inbox"]
        elif str(stage) in config["stage_dirs"]:
            target_dir = orbit_path / config["stage_dirs"][stage]
        else:
            target_dir = orbit_path
        
        # Create target directory if it doesn't exist
        target_dir.mkdir(exist_ok=True)
        
        # Move file to target directory
        self.move_file(file_path, target_dir / os.path.basename(file_path))
    
    def handle_other_file(self, file_path, frontmatter):
        """Handle files without orbits (domain dashboards, etc.)"""
        # For now, just log and leave in place
        logger.info(f"File {file_path} has no orbit, leaving in place")
    
    def find_orbit_path(self, orbit_name):
        """Find the path of an orbit (project) by name"""
        # First, search for exact match in the vault
        for root, dirs, files in os.walk(self.vault_path):
            for file in files:
                if file.endswith('.md') and file.lower() == f"{orbit_name.lower()}.md":
                    return Path(root)
        
        # If not found, try to find a similar match
        for root, dirs, files in os.walk(self.vault_path):
            for file in files:
                if file.endswith('.md') and orbit_name.lower() in file.lower():
                    return Path(root)
        
        return None
    
    def move_file(self, source, destination):
        """Move a file to a new location"""
        try:
            # Skip if source and destination are the same
            if Path(source) == Path(destination):
                logger.info(f"File {source} is already in the correct location")
                return
            
            # Check if destination exists
            if os.path.exists(destination):
                logger.warning(f"Destination file {destination} already exists, not moving {source}")
                return
            
            # Create parent directories if needed
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            
            # Move file
            shutil.move(source, destination)
            logger.info(f"Moved file {source} to {destination}")
            
            # Update recently modified to prevent re-processing
            recently_modified[str(destination)] = time.time()
            
        except Exception as e:
            logger.error(f"Error moving file {source} to {destination}: {str(e)}")

class OrbitEventHandler(FileSystemEventHandler):
    """Watchdog event handler for ORBIT system"""
    
    def __init__(self, orbit_handler):
        self.orbit_handler = orbit_handler
    
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
        
        # Normalize path for consistent handling
        file_path = os.path.abspath(event.src_path)
        
        # Check if file was recently modified
        if file_path in recently_modified:
            if time.time() - recently_modified[file_path] < DEBOUNCE_SECONDS:
                return  # Skip if modified too recently (debounce)
        
        # Record modification time
        recently_modified[file_path] = time.time()
        
        # Process the file
        self.orbit_handler.process_file(file_path)
    
    def on_created(self, event):
        """Handle file creation events"""
        if event.is_directory:
            return
        
        # Normalize path
        file_path = os.path.abspath(event.src_path)
        
        # Record creation time
        recently_modified[file_path] = time.time()
        
        # Process after a short delay to ensure file is fully written
        time.sleep(0.5)
        self.orbit_handler.process_file(file_path)

def main():
    """Main function to start the ORBIT watchdog"""
    orbit_handler = OrbitFileHandler()
    event_handler = OrbitEventHandler(orbit_handler)
    
    observer = Observer()
    observer.schedule(
        event_handler, 
        path=config["vault_path"], 
        recursive=True
    )
    
    logger.info(f"Starting ORBIT watchdog for vault: {config['vault_path']}")
    print(f"ORBIT watchdog started. Monitoring vault: {config['vault_path']}")
    print("Press Ctrl+C to stop")
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("ORBIT watchdog stopped by user")
        print("ORBIT watchdog stopped")
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    main()