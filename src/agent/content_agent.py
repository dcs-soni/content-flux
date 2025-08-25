"""
Content Creator Agent Module

Contains the main ContentCreatorAgent class with initialization,
validation, and workflow orchestration functionality.
"""

import json
import os
import random
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

from portia import (
    Portia,
    Config,
    DefaultToolRegistry,
    McpToolRegistry,
)
from portia.cli import CLIExecutionHooks
from config import get_config
from src.services.content_services import research_trending_topics, generate_content
from src.services.storage_services import save_content_to_notion, save_content_locally


class ContentCreatorAgent:
    def __init__(self, niche: str = "technology"):
        load_dotenv()
        
        self.niche = niche
        self.app_config = get_config()
        self.config = Config.from_default(default_log_level="INFO")
        
        
        try:
            self.registry = DefaultToolRegistry(self.config)
            print(" Tool registry initialized (default tools only)")
        except Exception as e:
            print(f"Tool registry initialization warning: {str(e)}")
            self.registry = None
        
        # Notion MCP
        self.notion_available = False
        if self.app_config.notion_api_key and self.registry is not None:
            try:
                print("Setting up Notion MCP!!")
                
                # Method 1 - OPENAPI_MCP_HEADERS
                headers_dict = {
                    "Authorization": f"Bearer {self.app_config.notion_api_key}",
                    "Notion-Version": self.app_config.notion_api_version
                }
                headers_json = json.dumps(headers_dict)
                
                print("------------Connecting with OPENAPI_MCP_HEADERS-----------")
                notion_mcp_registry = McpToolRegistry.from_stdio_connection(
                    server_name="notionApi", 
                    command="npx",
                    args=["-y", "@notionhq/notion-mcp-server"],
                    env={
                        "OPENAPI_MCP_HEADERS": headers_json
                    },
                    tool_list_read_timeout=30.0
                )
                
                self.registry = self.registry + notion_mcp_registry
                self.notion_available = True
                print("-=-=-=-=-=-=Notion MCP connected successfully (OPENAPI_MCP_HEADERS)-=-=-=-=-=-=")
                
            except Exception as e:
                print(f"Notion MCP connection failed: {str(e)}")
                
                # Alternative setup (if the above one fails and it failed sometimes though, DEBUG THIS)
                try:
                    print("Trying NOTION_TOKEN method")
              
                    notion_mcp_registry = McpToolRegistry.from_stdio_connection(
                        server_name="notionApi",
                        command="npx",
                        args=["-y", "@notionhq/notion-mcp-server"],
                        env={
                            "NOTION_TOKEN": self.app_config.notion_api_key
                        },
                        tool_list_read_timeout=30.0
                    )
                    
                    self.registry = self.registry + notion_mcp_registry
                    self.notion_available = True
                    print("Notion MCP connected successfully (NOTION_TOKEN)")
                    
                except Exception as e2:
                    print(f"Both official methods failed:")
                    print("Debug info:")
                    print(f"   - API Key format: {'Valid' if self.app_config.notion_api_key.startswith('ntn_') else 'Invalid - should start with ntn_'}")
                    print(f"   - Notion Version: {self.app_config.notion_api_version}")
                    print("Notion integration disabled & content will be saved locally only")
                    self.notion_available = False
        else:
            missing_items = []
            if not self.app_config.notion_api_key:
                missing_items.append("NOTION_API_KEY")
            if self.registry is None:
                missing_items.append("Tool Registry")
                
            print(f"-----XXXXXXXXXX------ Missing Notion configuration:-----XXXXXXXXXX------ {', '.join(missing_items)}")
            print("Notion integration disabled now content will be saved locally only")
            self.notion_available = False
        
        # Initialize Portia
        if self.registry is not None:
            try:
                # Validateion
                if not self.app_config.portia_api_key:
                    raise RuntimeError("PORTIA_API_KEY not found in environment variables")
                if not self.app_config.google_api_key:
                    raise RuntimeError("GOOGLE_API_KEY not found in environment variables")
                
                self.portia = Portia(
                    config=self.config,
                    tools=self.registry,
                    execution_hooks=CLIExecutionHooks()
                )
                print("Portia initialized successfully")
                
                # Debug: List available tools
                if hasattr(self.registry, 'get_tool_names'):
                    available_tools = self.registry.get_tool_names()
                    print(f"Available tools-- {available_tools}")
                elif hasattr(self.portia, 'tools') and hasattr(self.portia.tools, '__dict__'):
                    tool_names = [attr for attr in dir(self.portia.tools) if not attr.startswith('_')]
                    print(f"Available Portia tools-- {tool_names}")
                    
            except Exception as e:
                print(f"Portia initialization failed: {str(e)}")
                if "PORTIA_API_KEY" in str(e) or "GOOGLE_API_KEY" in str(e):
                    print("ERROR: Missing required API keys. Please check your .env file contains:")
                    print("  - PORTIA_API_KEY=your_portia_key")
                    print("  - GOOGLE_API_KEY=your_google_key")
                    self.portia = None
                    return
                
                print("Trying with minimal tool registry!!")
                try:
                    # Try with just the default registry without open source tools
                    minimal_registry = DefaultToolRegistry(self.config)
                    self.portia = Portia(
                        config=self.config,
                        tools=minimal_registry,
                        execution_hooks=CLIExecutionHooks()
                    )
                    print("Portia initialized with minimal tools")
                except Exception as e2:
                    print(f"Portia initialization completely failed: {str(e2)}")
                    self.portia = None
        else:
            print("No tool registry available - Portia cannot be initialized")
            self.portia = None
        
        self.output_dir = self.app_config.output_directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Validate configuration
        self._validate_setup()
        
        # Final check - if Portia is not available, can't proceed
        if self.portia is None:
            print("\nCRITICAL ERROR: Portia is not initialized")
            print("The agent cannot function without Portia. Please check:")
            print("1. PORTIA_API_KEY is set in your .env file")
            print("2. GOOGLE_API_KEY is set in your .env file")
            print("3. Your internet connection is working and portia is accessible")
            
    def _validate_setup(self):
        print("Validating Content Creator Agent setup...")
        
        validation = self.app_config.validate_config()
        
        if validation["errors"]:
            print("Configuration Errors Found:")
            for error in validation["errors"]:
                print(f"   • {error}")
            print("\nPlease check your .env file and ensure all required API keys are set.")
        
        if validation["warnings"]:
            print("Configuration Warnings:")
            for warning in validation["warnings"]:
                print(f"   • {warning}")
        
        if not validation["errors"] and not validation["warnings"]:
            print("All configurations validated successfully")
        
        # Check Portia specifically
        if self.portia is None:
            print("Portia is not initialized, planning operations will fail")
            print("Missing API keys or tool registry issues")
            print("Check your PORTIA_API_KEY and GOOGLE_API_KEY in .env file")
            
        # Check Notion availability
        if not self.notion_available:
            print("--XXXXXXX--Notion integration is disabled - content will only be saved locally")
        
        print("=" * 50)

    def run_content_creation_workflow(self, specific_topic: str = None) -> Dict[str, Any]:
        """Run the complete content creation workflow."""
        print("Starting Content Creator Agent workflow...........")
        
        try:
            # Validate setup before proceeding
            if self.portia is None:
                raise RuntimeError("\n------XXXXXXXXXXXXXX-----CRITICAL ERROR: Portia is not initialized.------XXXXXXXXXXXXXX-----\n" +
                                 "Please check your API keys and configuration:\n" +
                                 "1. PORTIA_API_KEY is set correctly\n" +
                                 "2. GOOGLE_API_KEY is set correctly\n" +
                                 "3. Your internet connection is working and portia is accessible")
            
            # Step 1: Research trending topics (unless specific topic provided)
            if specific_topic:
                topics = [specific_topic]
                print(f"Using specified topic: {specific_topic}")
            else:
                print("Researching trending topics...............")
                trending_topics = research_trending_topics(self.portia, self.niche)
                
                if not trending_topics or (isinstance(trending_topics, str) and len(trending_topics.strip()) < 10):
                    raise RuntimeError("No trending topics found from research - research may have failed")
                
                # Use a random topic from research
                if isinstance(trending_topics, list) and trending_topics:
                    # Clean and filter the list first
                    clean_topics = [str(topic).strip() for topic in trending_topics if str(topic).strip()]
                    if clean_topics:
                        topic = random.choice(clean_topics)
                    else:
                        topic = str(trending_topics[0]).strip()
                else:
                    # Parse from string format and collect all topics
                    lines = str(trending_topics).split('\n')
                    topic_candidates = []
                    
                    # Extract all numbered topics (1., 2., 3., etc.)
                    for line in lines:
                        line = line.strip()
                        if line and any(line.startswith(f'{i}.') or line.startswith(f'{i})') for i in range(1, 11)):
                            # Extract topic text after number
                            clean_topic = line.split('.', 1)[-1].split(')', 1)[-1].strip()
                            if clean_topic and len(clean_topic) > 5:
                                topic_candidates.append(clean_topic)
                    
                    if topic_candidates:
                        topic = random.choice(topic_candidates)
                        print(f"Found {len(topic_candidates)} topics, randomly selected one")
                    else:
                        # Fallback, use first non-empty line
                        topic = None
                        for line in lines:
                            if line.strip() and len(line.strip()) > 5:
                                topic = line.strip()
                                break
                
                if not topic or len(topic.strip()) < 5:
                    raise RuntimeError("Could not extract valid topic from research results")
                
                # Clean topic of markdown and special characters
                topic = topic.replace('*', '').replace('#', '').strip()
                topics = [topic]
                print(f"Selected topic: {topics[0]}")
            
            results = []
            
            for topic in topics[:1]:  # Process one topic for now
                print(f"\nProcessing topic: {topic}")
                
                try:
                    # 2: Generate comprehensive content
                    content_data = generate_content(self.portia, topic)
                    
                    print(f"   Generated content with {len(content_data)} fields")
                    print(f"   Title: {content_data.get('title', 'No title')}")
                    print(f"   Article length: {len(str(content_data.get('long_form_content', '')))} characters")
                    print(f"   Keywords: {', '.join(content_data.get('keywords', [])[:3])}")
                    
                    # Step 3: Save to Notion database (if available)
                    if self.notion_available:
                        try:
                            notion_url = save_content_to_notion(self.portia, content_data, topic, self.app_config, self.notion_available)
                            print(f"Notion save result: {notion_url}")
                        except Exception as e:
                            print(f"------XXXXXXX-----Notion save failed:------XXXXXXX----- {e}")
                            notion_url = f"Failed: {str(e)}"
                    else:
                        notion_url = "Skipped - Notion not available"
                    
                    # Step 4: Save files locally
                    try:
                        local_files = save_content_locally(content_data, topic, self.output_dir, self.portia)
                        print(f"Local files saved to: {local_files}")
                    except Exception as e:
                        print(f"------XXXXXXX-----Local file save failed------XXXXXXX-----: {e}")
                        local_files = f"Failed: {str(e)}"
                    
                    result = {
                        "topic": topic,
                        "content_data": content_data,
                        "notion_url": notion_url,
                        "local_files": local_files,
                        "status": "ready_for_distribution",
                        "created_at": datetime.now().isoformat()
                    }
                    
                    results.append(result)
                    print(f"Content created successfully for: {topic}")
                    
                except Exception as content_error:
                    print(f"------XXXXXXX-----Failed to generate content for topic------XXXXXXX----- '{topic}': {content_error}")
                    # Continue with next topic instead of failing completely :(
                    continue
            
            if not results:
                raise RuntimeError("No content was successfully generated")
            
            print("\nContent Creator Agent workflow completed, YAYYYYY!!!!!!!!!")
            
            # Print Notion URL
            for i, result in enumerate(results, 1):
                notion_url = result.get('notion_url', '')
                if notion_url and notion_url.startswith('Notion page created:'):
            
                    try:
                        response_text = notion_url.replace('Notion page created: ', '')
                        response_data = json.loads(response_text)
                        if 'content' in response_data and response_data['content']:
                            content_text = response_data['content'][0]['text']
                            pages_data = json.loads(content_text)
                            if 'pages' in pages_data and pages_data['pages']:
                                page_url = pages_data['pages'][0]['url']
                                print(f"Topic {i}: {result['topic']}")
                                print(f"Notion URL 🔗: {page_url}")
                    except:
                        print(f"Topic {i}: {result['topic']} - Notion URL parsing failed")
                elif notion_url and not notion_url.startswith(('Failed:', 'Skipped')):
                    print(f"Topic {i}: {result['topic']}")
                    print(f"Notion URL 🔗: {notion_url}")

            return {"results": results, "total_created": len(results)}
            
        except Exception as e:
            print(f"❌ Error in content creation workflow: {str(e)}")
            raise