"""
Plan Builders Module

Contains all PlanBuilder methods for creating research, content generation,
and storage plans for the Content Creator Agent.
"""

import json
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
            task=f"Analyze the search results from previous steps and identify the top 10 trending topics in {topic}. Focus on recent, engaging topics with good SEO potential. If search results are limited or empty, generate relevant trending topics based on current industry trends. Always return a numbered list (1-10) with substantive topics, never return empty content. Example format: 1. Topic Name - Brief description\n2. Another Topic - Description",
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
    
    # Map topic to valid Notion select options
    topic_lower = topic.lower()
    if 'business' in topic_lower or 'entrepreneur' in topic_lower or 'startup' in topic_lower:
        niche_value = "business"
    elif 'health' in topic_lower or 'medical' in topic_lower or 'wellness' in topic_lower:
        niche_value = "health"  
    elif 'finance' in topic_lower or 'money' in topic_lower or 'investment' in topic_lower:
        niche_value = "finance"
    else:
        niche_value = "technology"  # Default fallback
    
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
        # Determine content type based on what we're creating (mostly this will be multi-format = blog_post)
        content_type = "blog_post" 
        

        safe_content = full_content.replace('"', "'").replace('\n', '\\n').replace('\r', '')
        safe_title = title.replace('"', "'")
        # safe_keywords = ', '.join(keywords[:3]) if keywords else 'content, guide, trends'
        
        plan = (
            PlanBuilder(f"Save complete content to Notion database: {title}")
            .step(
                task=f"""Use notion-create-pages tool to create a page with this exact structure:

{{
  "parent": {{
    "database_id": "{notion_database_id}"
  }},
  "pages": [
    {{
      "properties": {{
        "title": "{safe_title}",
        "Content Type": "{content_type}",
        "Status": "ready",
        "Niche": "{niche_value}"
      }},
      "content": "{safe_content}"
    }}
  ]
}}

Make sure to populate ALL properties in the database correctly. Do NOT include Target Date, Performance Links, or Distributed At properties.""",
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


def create_file_save_plan(content_data: Dict[str, Any], filename: str, output_dir: str):
    """Create a plan to save content files using Portia File Writer tool."""
    plan_builder = PlanBuilder(f"Save content files for: {filename}")
    
    files_created = []
    
    # The entire content will be here in this JSON file
    json_path = f"{output_dir}/{filename}.json"
    json_content = json.dumps(content_data, indent=2, ensure_ascii=False)
    plan_builder = plan_builder.step(
        task=f"Write JSON content to file {json_path}. Filename: {json_path}. Content: {json_content}",
        tool_id="file_writer_tool",
        output="$json_file"
    )
    files_created.append(json_path)
    
    # Individual content files
    if content_data.get('long_form_content'):
        article_path = f"{output_dir}/{filename}_article.md"
        article_content = f"# {content_data.get('title', 'Article')}\n\n{content_data['long_form_content']}"
        plan_builder = plan_builder.step(
            task=f"Write article content to file {article_path}. Filename: {article_path}. Content: {article_content}",
            tool_id="file_writer_tool",
            output="$article_file"
        )
        files_created.append(article_path)
    
    if content_data.get('twitter_thread'):
        twitter_path = f"{output_dir}/{filename}_twitter.txt"
        plan_builder = plan_builder.step(
            task=f"Write Twitter content to file {twitter_path}. Filename: {twitter_path}. Content: {content_data['twitter_thread']}",
            tool_id="file_writer_tool",
            output="$twitter_file"
        )
        files_created.append(twitter_path)
    
    if content_data.get('linkedin_post'):
        linkedin_path = f"{output_dir}/{filename}_linkedin.txt"
        plan_builder = plan_builder.step(
            task=f"Write LinkedIn content to file {linkedin_path}. Filename: {linkedin_path}. Content: {content_data['linkedin_post']}",
            tool_id="file_writer_tool",
            output="$linkedin_file"
        )
        files_created.append(linkedin_path)
    
    if content_data.get('instagram_caption'):
        instagram_path = f"{output_dir}/{filename}_instagram.txt"
        plan_builder = plan_builder.step(
            task=f"Write Instagram content to file {instagram_path}. Filename: {instagram_path}. Content: {content_data['instagram_caption']}",
            tool_id="file_writer_tool",
            output="$instagram_file"
        )
        files_created.append(instagram_path)

    seo_data = {
        "keywords": content_data.get('keywords', []),
        "meta_description": content_data.get('meta_description', ''),
        "tags": content_data.get('tags', [])
    }
    seo_path = f"{output_dir}/{filename}_seo.json"
    seo_content = json.dumps(seo_data, indent=2, ensure_ascii=False)
    plan_builder = plan_builder.step(
        task=f"Write SEO data to file {seo_path}. Filename: {seo_path}. Content: {seo_content}",
        tool_id="file_writer_tool",
        output="$seo_file"
    )
    files_created.append(seo_path)
    
    return plan_builder.build(), files_created