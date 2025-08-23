"""
Content Services Module

Contains research and content generation services for the Content Creator Agent.
"""

from typing import List, Dict, Any
from src.plans.plan_builders import create_research_plan, create_content_research_plan, create_content_generation_plan


def research_trending_topics(portia, niche: str) -> List[str]:
    print(f"Researching trending topics in {niche}...")
    
    if portia is None:
        raise RuntimeError("Portia is not available - cannot perform research")
    
    try:
        # Create and execute research plan
        research_plan = create_research_plan(niche)
        print("Executing research plan...")
        
        result = portia.run_plan(research_plan)
        
        # Extract topics from result
        topics_text = None
        if hasattr(result, 'outputs') and result.outputs:
            if hasattr(result.outputs, 'final_output') and result.outputs.final_output:
                topics_text = result.outputs.final_output.value
            elif hasattr(result.outputs, 'steps') and result.outputs.steps:
                last_step = result.outputs.steps[-1]
                if hasattr(last_step, 'output') and last_step.output:
                    topics_text = last_step.output
        
        if topics_text is None:
            topics_text = str(result) if result else ""
        
        return _extract_topics_from_text(topics_text)
        
    except Exception as e:
        print(f"Research failed: {str(e)}")
        return ["AI Technology", "Machine Learning", "Quantum Computing"]  # Fallback topics


def _extract_topics_from_text(topics_text: str) -> List[str]:
    """Extract topics from numbered list text."""
    topics = []
    for line in str(topics_text).split('\n'):
        line = line.strip()
        # Look for numbered items
        if line and any(line.startswith(f"{i}.") or line.startswith(f"{i})") for i in range(1, 20)):
            # Extract topic after number
            topic = line.split('.', 1)[-1].split(')', 1)[-1].strip()
            if ':' in topic:
                topic = topic.split(':', 1)[0].strip()
            # Clean up the topic
            topic = topic.strip(' ,.;:-')
            if len(topic) > 3 and len(topic) <= 80:
                topics.append(topic)
    
    if not topics:
        print(f"Warning: No topics extracted from: {topics_text[:200]}...")
        return ["AI Technology", "Machine Learning", "Quantum Computing"]  # Fallback
        
    print(f"Found {len(topics)} trending topics")
    return topics[:10]  # Return top 10


def generate_content(portia, topic: str) -> Dict[str, Any]:
    """Generate comprehensive content for a specific topic using PlanBuilder."""
    print(f"Generating content for topic: {topic}")
    
    if portia is None:
        raise RuntimeError("Portia is not available - cannot generate content")
    
    try:
        # Step 1
        print("Creating content research plan...")
        research_plan = create_content_research_plan(topic)
        
        print("Executing research plan...")
        research_result = portia.run_plan(research_plan)
        
        # Extract research data
        research_data = None
        if hasattr(research_result, 'outputs') and research_result.outputs:
            if hasattr(research_result.outputs, 'final_output') and research_result.outputs.final_output:
                research_data = research_result.outputs.final_output.value
            elif hasattr(research_result.outputs, 'steps') and research_result.outputs.steps:
                last_step = research_result.outputs.steps[-1]
                if hasattr(last_step, 'output') and last_step.output:
                    research_data = last_step.output
        
        if research_data is None:
            research_data = str(research_result) if research_result else "No research data available"
        
        if not research_data or len(str(research_data).strip()) < 10:
            raise RuntimeError("Research returned insufficient data")
        
        print(f"Research completed. Data length: {len(str(research_data))}")
        
        # Step 2: Generate content 
        print("-------Creating content generation plan--------")
        content_plan = create_content_generation_plan(topic, research_data)
        
        print("--Executing content generation plan--")
        content_result = portia.run_plan(content_plan)
        
        # Extract content data
        content_text = None
        if hasattr(content_result, 'outputs') and content_result.outputs:
            if hasattr(content_result.outputs, 'final_output') and content_result.outputs.final_output:
                content_text = content_result.outputs.final_output.value
            elif hasattr(content_result.outputs, 'steps') and content_result.outputs.steps:
                last_step = content_result.outputs.steps[-1]
                if hasattr(last_step, 'output') and last_step.output:
                    content_text = last_step.output
        
        if content_text is None:
            content_text = str(content_result) if content_result else ""
        
        if not content_text or len(str(content_text).strip()) < 20:
            raise RuntimeError("Content generation returned insufficient data")
        
        print(f"Content generated. Length: {len(str(content_text))}")
        print(f"Content preview: {str(content_text)[:200]}...")
        
        content_json = {
            'title': f"{topic} - Comprehensive Guide",
            'meta_description': f"Complete guide to {topic} with latest trends, insights and practical applications",
            'long_form_content': content_text,  # Full content from LLM
            'twitter_thread': f"THREAD about {topic}: Key insights and trends you need to know! {content_text[:400]}...",
            'linkedin_post': f"Insights on {topic}: {content_text[:250]}... What are your thoughts? #technology #innovation",
            'instagram_caption': f"Everything you need to know about {topic} 📚✨ #tech #learning #innovation #{topic.lower().replace(' ', '')}",
            'keywords': [topic, "technology", "trends", "innovation", "guide"],
            'tags': [topic.lower(), "technology", "guide", "trends"]
        }
        
        # Validate fields
        required_fields = ['title', 'meta_description', 'long_form_content', 'twitter_thread', 'linkedin_post', 'instagram_caption', 'keywords', 'tags']
        for field in required_fields:
            if field not in content_json or not content_json[field]:
                raise RuntimeError(f"Missing or empty required field: {field}")
        
        print(f"--------Content generation completed successfully--------")
        print(f"   Title: {content_json['title']}")
        print(f"   Article length: {len(content_json['long_form_content'])} characters")
        print(f"   Keywords: {', '.join(content_json['keywords'][:3])}...")
        
        return content_json
            
    except Exception as e:
        print(f"Error during content generation: {str(e)}")
        raise