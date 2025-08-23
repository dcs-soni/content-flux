"""
Content Flux - Content Research & Creator Agent

Purpose: Automatically research trending topics, generate high-quality content, 
and create a notion database.

Main entry point for the Content Creator Agent.
"""

import json
from src.agent.content_agent import ContentCreatorAgent


def main():
    """Main function to run the Content Creator Agent."""
    print("Content Flux 🤖 Content Creator Agent")
    print("--------------------------------------")
    
    # Get user input for content niche
    niche = input("Enter content niche (default: technology): ").strip() or "technology"
    specific_topic = input("Enter specific topic (leave empty for trend research): ").strip() or None
    
    # Create and run the agent
    agent = ContentCreatorAgent(niche=niche)
    results = agent.run_content_creation_workflow(specific_topic=specific_topic)
    
    print("\n----------Final Results--------:")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()