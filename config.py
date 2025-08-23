"""
Configuration module for Content Flux

This module handles all configuration settings, environment variables,
and provides utility functions for the Content Flux agents.
"""

import os
from typing import Dict, List, Optional
from dotenv import load_dotenv


class ContentFluxConfig:
    """Configuration class for Content Flux agents."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        load_dotenv()
        
        self.portia_api_key = os.getenv('PORTIA_API_KEY')
        
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        
        self.notion_api_key = os.getenv('NOTION_API_KEY')
        self.notion_database_id = os.getenv('NOTION_DATABASE_ID')
        self.notion_api_version = os.getenv('NOTION_API_VERSION', '2022-06-28')
        
        self.default_niche = os.getenv('DEFAULT_NICHE', 'technology')  # NOT USED
        self.output_directory = os.getenv('OUTPUT_DIRECTORY', 'generated_content')  # USED
        

    
    def validate_config(self) -> Dict[str, List[str]]:
        """Validate configuration and return any missing/invalid settings."""
        errors = []
        warnings = []
        
        # Check required settings
        if not self.portia_api_key:
            errors.append("PORTIA_API_KEY is required")
        
        if not self.google_api_key:
            errors.append("GOOGLE_API_KEY is required for LLM functionality")
        
        # Check optional but recommended settings
        if not self.notion_api_key:
            warnings.append("NOTION_API_KEY not set - content storage will be limited to local files")
        
        return {"errors": errors, "warnings": warnings}
    
    
# Global config instance
config = ContentFluxConfig()


# Utility functions
def get_config() -> ContentFluxConfig:
    """Get the global configuration instance."""
    return config


def validate_setup() -> bool:
    """Validate the setup and print any issues."""
    validation = config.validate_config()
    
    if validation["errors"]:
        print("❌Configuration Errors:")
        for error in validation["errors"]:
            print(f"   • {error}")
        print("\nPlease fix these errors before running Content Flux.")
        return False
    
    if validation["warnings"]:
        print("⚠️Configuration Warnings:")
        for warning in validation["warnings"]:
            print(f"   • {warning}")
        print("\nThese warnings won't prevent Content Flux from running but may limit functionality.")
    
    return True