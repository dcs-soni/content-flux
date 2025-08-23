"""
Plan Builders Module

Contains all PlanBuilder methods for creating research, content generation,
and storage plans for the Content Creator Agent.
"""

from datetime import datetime
from typing import Dict, Any
from portia import PlanBuilder


def create_research_plan(topic: str):
    """Create a research plan using PlanBuilder."""
    plan = (
        PlanBuilder(f"Research trending topics in {topic}")
        .step(
            task="Search for trending topics",
            tool_id="search_tool",
            output="$trending_search"
        )
        .step(
            task="Search for latest news", 
            tool_id="search_tool",
            output="$news_search"
        )
        .step(
            task="Search for discussions",
            tool_id="search_tool", 
            output="$discussion_search"
        )
        .step(
            task=f"Analyze search results and identify the top 10 trending topics in {topic}. Focus on recent, engaging topics with good SEO potential. Return a simple numbered list.",
            tool_id="llm_tool",
            output="$trending_topics"
        )
        .build()
    )
    return plan


def create_content_research_plan(topic: str):
    """Create a content research plan using PlanBuilder."""
    plan = (
        PlanBuilder(f"Research content for topic: {topic}")
        .step(
            task=f"Search for latest trends about {topic}",
            tool_id="search_tool",
            output="$trends_search"
        )
        .step(
            task=f"Search for statistics about {topic}",
            tool_id="search_tool",
            output="$stats_search"
        )
        .step(
            task=f"Search for expert opinions about {topic}",
            tool_id="search_tool",
            output="$expert_search"
        )
        .step(
            task=f"Search for best practices about {topic}",
            tool_id="search_tool",
            output="$practices_search"
        )
        .step(
            task=f"Compile comprehensive research summary about {topic} using the search results. Include key findings, statistics, and insights.",
            tool_id="llm_tool",
            output="$research_summary"
        )
        .build()
    )
    return plan


def create_content_generation_plan(topic: str, research_data: str):
    """Create a content generation plan using PlanBuilder."""
    plan = (
        PlanBuilder(f"Generate comprehensive content for: {topic}")
        .step(
            task=f"""Based on this research about "{topic}":

{research_data}

Generate comprehensive content with the following elements:

1. SEO-optimized title (60-70 characters max)
2. Meta description (150-160 characters max)
3. Comprehensive 800-1200 word article with headers and bullet points
4. 6-tweet Twitter thread starting with 'THREAD about {topic}:' (NO EMOJIS)
5. Professional 150-200 word LinkedIn post with call-to-action (NO EMOJIS)
6. Instagram caption with hashtags (NO EMOJIS OR SYMBOLS)
7. 5-7 relevant SEO keywords
8. 3-5 relevant content tags

IMPORTANT: Use only basic ASCII text - no emojis, symbols, or unicode characters.
Format as clear sections with headers.""",
            tool_id="llm_tool",
            output="$generated_content"
        )
        .build()
    )
    return plan


def create_notion_save_plan(content_data: Dict[str, Any], topic: str, notion_database_id: str = None):
    """Create a plan to save content to Notion using PlanBuilder."""
    title = content_data.get('title', topic)
    long_form = content_data.get('long_form_content', 'Content not available')
    twitter = content_data.get('twitter_thread', 'Twitter content not available')
    linkedin = content_data.get('linkedin_post', 'LinkedIn content not available')
    instagram = content_data.get('instagram_caption', 'Instagram content not available')
    keywords = content_data.get('keywords', [])
    meta_desc = content_data.get('meta_description', '')
    
    # Create comprehensive content for Notion with proper structure
    full_content = f"""# {title}

## Overview
{meta_desc}

## Complete Article
{long_form}

## Social Media Content

### Twitter Thread
{twitter}

### LinkedIn Post
{linkedin}

### Instagram Caption
{instagram}

## SEO Information
**Keywords:** {', '.join(keywords)}
**Tags:** {', '.join(content_data.get('tags', []))}

## Content Metadata
- **Topic:** {topic}
- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Status:** Ready for Distribution
"""
    notion_create_tool = "portia:mcp:mcp.notion.com:notion_create_pages"
    
    if notion_database_id:
        # Create page in database 
        plan = (
            PlanBuilder(f"Save complete content to Notion database: {title}")
            .step(
                task=f"""Create a comprehensive page in Notion database {notion_database_id} with:

Title: {title}
Parent Database: {notion_database_id}

Complete Content:
{full_content}

Make sure to include ALL sections: Overview, Complete Article, Social Media Content, SEO Information, and Content Metadata. Do not truncate any content.""",
                tool_id=notion_create_tool,
                output="$database_page"
            )
            .build()
        )
    else:
        # Create standalone page with complete content
        plan = (
            PlanBuilder(f"Create comprehensive Notion page: {title}")
            .step(
                task=f"""Create a new standalone Notion page with:

Title: {title}

Complete Content:
{full_content}

Ensure all sections are included: Overview, Complete Article, Social Media Content, SEO Information, and Content Metadata. Include the full article content without truncation.""",
                tool_id=notion_create_tool,
                output="$notion_page"
            )
            .build()
        )
    return plan