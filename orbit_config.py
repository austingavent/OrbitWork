# ORBIT System Configuration

from pathlib import Path

# Path to your Obsidian vault - UPDATED PATH
VAULT_PATH = "/Users/austinavent/Nextcloud/Obsidian/Ventura_Orbit"

# Domain folders (core organizational structure)
DOMAINS = {
    "0": "Origins",
    "1": "Self",
    "2": "Health",
    "3": "Philosophy",
    "4": "Expression", 
    "5": "Culture",
    "6": "People",
    "7": "Environment",  # Proper capitalization
    "8": "Work_systems",
    "9": "Meta_resources",
    # Add more domains as needed
}

# Project numbering increment
PROJECT_INCREMENT = 10

# Reserved satellite numbers
INBOX_NUMBER = "0"
SOURCE_NUMBER = "source"  # Special folder for source materials

# Maximum satellites per project (excluding inbox and source)
MAX_SATELLITES = 8

# Hidden inbox directory name
HIDDEN_INBOX = ".0-inbox"

# Hidden index file name
HIDDEN_INDEX = ".index.md"

# Log settings
LOG_LEVEL = "INFO"
LOG_FILE = "orbit_manager.log"

# File watching settings
DEBOUNCE_TIME = 1  # seconds

# Property names for frontmatter
PROP_OBJECT = "object"
PROP_ORBIT = "orbits"  # Using plural to match your templates
PROP_SATELLITES = "satellites"  
PROP_STAGE = "stage"
PROP_DOMAIN = "domain"  
PROP_TRACK_NUMBER = "track_number"  # Using track_number with value 7
PROP_CREATED = "created"

# Stage directories
STAGE_DIRS = {
    0: ".0-inbox",  # Origin/Inbox
    # Other stages as needed
}

# Source directory name (without number prefix)
SOURCE_DIR_NAME = "source"

def get_vault_path() -> Path:
    """Returns the vault path as a Path object."""
    return Path(VAULT_PATH)

def get_fallback_path() -> Path:
    """Returns the fallback path for unprocessed notes."""
    return Path(VAULT_PATH) / ".orbit" / "fallback"

# Global configuration dictionary
config = {
    "vault_path": VAULT_PATH,
    "domains": DOMAINS,
    "project_increment": PROJECT_INCREMENT,
    "inbox_number": INBOX_NUMBER,
    "source_number": SOURCE_NUMBER,
    "max_satellites": MAX_SATELLITES,
    "hidden_inbox": HIDDEN_INBOX,
    "hidden_index": HIDDEN_INDEX,
    "log_level": LOG_LEVEL,
    "log_file": LOG_FILE,
    "debounce_time": DEBOUNCE_TIME,
    "prop_object": PROP_OBJECT,
    "prop_orbit": PROP_ORBIT,
    "prop_satellites": PROP_SATELLITES,
    "prop_stage": PROP_STAGE,
    "prop_domain": PROP_DOMAIN,
    "prop_track_number": PROP_TRACK_NUMBER,
    "prop_created": PROP_CREATED,
    "stage_dirs": STAGE_DIRS,
    "source_dir_name": SOURCE_DIR_NAME,
    "get_vault_path": get_vault_path,
    "get_fallback_path": get_fallback_path
}