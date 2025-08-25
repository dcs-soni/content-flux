"""
Storage Services Module

Contains all storage operations for the Content Creator Agent,
including Notion and local file storage functionality.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any
from src.plans.plan_builders import create_notion_save_plan, create_file_save_plan


def clean_unicode_in_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively clean Unicode characters from dictionary values - removes ALL non-ASCII."""
    cleaned_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            # Remove ALL non-ASCII characters including emojis
            cleaned_value = value.encode('ascii', 'ignore').decode('ascii')
            # Additional cleanup
            cleaned_value = ''.join(char for char in cleaned_value if ord(char) < 128)
            cleaned_data[key] = cleaned_value
        elif isinstance(value, list):
            cleaned_list = []
            for item in value:
                if isinstance(item, str):
                    clean_item = item.encode('ascii', 'ignore').decode('ascii')
                    clean_item = ''.join(char for char in clean_item if ord(char) < 128)
                    cleaned_list.append(clean_item)
                else:
                    cleaned_list.append(item)
            cleaned_data[key] = cleaned_list
        else:
            cleaned_data[key] = value
    return cleaned_data


def save_content_to_notion(portia, content_data: Dict[str, Any], topic: str, app_config, notion_available: bool) -> str:
    """Save generated content to Notion database using PlanBuilder."""
    print("Saving content to Notion database...")
    
    # Validate content_data
    if not content_data or not isinstance(content_data, dict):
        print("Invalid content_data provided to save_content_to_notion")
        return "Notion storage skipped - invalid content data"
    
    if not notion_available:
        print("Notion is not available - skipping Notion storage")
        return "Notion storage skipped - not available"
        
    if not app_config.notion_api_key:
        print("Notion API key not configured - skipping Notion storage")
        return "Notion storage skipped - missing API key"
    
    if portia is None:
        raise RuntimeError("Portia is not available - cannot save to Notion")
    
    try:
        print("Creating Notion save plan...")
        notion_plan = create_notion_save_plan(content_data, topic, app_config.notion_database_id)
        
        print("Executing Notion save plan...")
        result = portia.run_plan(notion_plan)
        
        # Extract result
        result_text = None
        if hasattr(result, 'outputs') and result.outputs:
            if hasattr(result.outputs, 'final_output') and result.outputs.final_output:
                result_text = result.outputs.final_output.value
            elif hasattr(result.outputs, 'steps') and result.outputs.steps:
                last_step = result.outputs.steps[-1]
                if hasattr(last_step, 'output') and last_step.output:
                    result_text = last_step.output
        
        if result_text is None:
            result_text = str(result) if result else "Page creation attempted"
        
        return f"Notion page created: {result_text}"
            
    except Exception as e:
        print(f"Error during Notion storage: {str(e)}")
        return f"Notion storage failed: {str(e)}"


def save_content_locally(content_data: Dict[str, Any], topic: str, output_dir: str, portia=None) -> str:
    """Save generated content to local files using Portia File Writer tool first, if it fails then fallback to manual file adding."""
    print("Now, Saving content files locally")
    
    # Create filename-safe topic name
    safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_topic = safe_topic.replace(' ', '_').lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Limit the safe_topic length to prevent overly long filenames
    if len(safe_topic) > 50:
        safe_topic = safe_topic[:50].rstrip('_')
    
    filename = f"{safe_topic}_{timestamp}"
    
    # Final check for filename length
    if len(filename) > 100:
        filename = f"content_{timestamp}"
    
    # Try Portia File Writer tool first
    if portia is not None:
        try:
            print("Using Portia File Writer tool...")
            return _save_files_with_portia(portia, content_data, filename, output_dir)
        except Exception as e:
            print(f"Portia File Writer failed: {str(e)}")
            print("Falling back to manual file saving...")
    
    # Fallback to manual saving
    return _save_files_manually(content_data, filename, output_dir)


def _save_files_with_portia(portia, content_data: Dict[str, Any], filename: str, output_dir: str) -> str:
    """Save files using Portia File Writer tool."""
    try:
        print("-------Creating file writing plan with Portia---------")
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Create plan and get file list using plan builder
        file_plan, files_created = create_file_save_plan(content_data, filename, output_dir)
        
        # Execute the plan
        result = portia.run_plan(file_plan)
        print(" --------------------------------------")
        print(f"Portia File Writer saved {len(files_created)} files successfully")
        return f"{output_dir}/{filename}"
        
    except Exception as e:
        print(f"Portia File Writer error: {str(e)}")
        raise e

# Fallback to this if Portia File Writer fails
def _save_files_manually(content_data: Dict[str, Any], filename: str, output_dir: str) -> str:
    """Manually save files when Portia file_writer_tool fails."""
    try:
        print("..........Falling back to manual file saving..........")
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Limit filename length to prevent filesystem issues
        if len(filename) > 100:
            # Create a shortened version with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"content_{timestamp}"
            print(f"Shortened filename to: {filename}")
        
        # Save main JSON file
        json_path = f"{output_dir}/{filename}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, indent=2, ensure_ascii=False)
        
        
        files_created = [json_path] # Save individual files
        
        if content_data.get('long_form_content'):
            article_path = f"{output_dir}/{filename}_article.md"
            with open(article_path, 'w', encoding='utf-8') as f:
                f.write(f"# {content_data.get('title', 'Article')}\n\n")
                f.write(content_data['long_form_content'])
            files_created.append(article_path)
        
        if content_data.get('twitter_thread'):
            twitter_path = f"{output_dir}/{filename}_twitter.txt"
            with open(twitter_path, 'w', encoding='utf-8') as f:
                f.write(content_data['twitter_thread'])
            files_created.append(twitter_path)
        
        if content_data.get('linkedin_post'):
            linkedin_path = f"{output_dir}/{filename}_linkedin.txt"
            with open(linkedin_path, 'w', encoding='utf-8') as f:
                f.write(content_data['linkedin_post'])
            files_created.append(linkedin_path)
        
        if content_data.get('instagram_caption'):
            instagram_path = f"{output_dir}/{filename}_instagram.txt"
            with open(instagram_path, 'w', encoding='utf-8') as f:
                f.write(content_data['instagram_caption'])
            files_created.append(instagram_path)
        
      
        seo_data = {
            "keywords": content_data.get('keywords', []),
            "meta_description": content_data.get('meta_description', ''),
            "tags": content_data.get('tags', [])
        }
        seo_path = f"{output_dir}/{filename}_seo.json"
        with open(seo_path, 'w', encoding='utf-8') as f:
            json.dump(seo_data, f, indent=2, ensure_ascii=False)
        files_created.append(seo_path)
        
        print(f"Manually saved {len(files_created)} files")
        return f"{output_dir}/{filename}"
        
    except Exception as e:
        print(f"Manual file saving also failed: {str(e)}")
        return f"Failed to save files: {str(e)}"