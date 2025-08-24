"""
Streamlit Application for Content Flux - AI-powered Content Creation
"""

import streamlit as st
import os
import json
from datetime import datetime
from src.agent.content_agent import ContentCreatorAgent

# Page config
st.set_page_config(
    page_title="Content Flux 🤖 AI Content Creator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .content-preview {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables."""
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'content_results' not in st.session_state:
        st.session_state.content_results = None
    if 'generation_status' not in st.session_state:
        st.session_state.generation_status = 'idle'

def check_environment_variables():
    """Check if required environment variables are set."""
    required_vars = {
        'PORTIA_API_KEY': 'Portia API Key (required)',
        'GOOGLE_API_KEY': 'Google API Key (required)',
        'TAVILY_API_KEY': 'TAVILY API Key (required)',
        'NOTION_API_KEY': 'Notion API Key (optional but recomended)',
        'NOTION_DATABASE_ID': 'Notion Database ID (optional but recomended)'
    }
    
    missing_required = []
    missing_optional = []
    
    for var, description in required_vars.items():
        if not os.getenv(var):
            if 'required' in description:
                missing_required.append(f"{var}: {description}")
            else:
                missing_optional.append(f"{var}: {description}")
    
    return missing_required, missing_optional

def display_sidebar():
    """Display sidebar with configuration and controls."""
    with st.sidebar:
        st.header("Configuration")
        
        # Environment check
        missing_required, missing_optional = check_environment_variables()
        
        if missing_required:
            st.error("Missing Required Environment Variables:")
            for var in missing_required:
                st.write(f"• {var}")
            st.write("Please set these in your .env file or environment.")
        else:
            st.success("All required environment variables are set!")
        
        if missing_optional:
            st.warning("Optional Configuration:")
            for var in missing_optional:
                st.write(f"• {var}")
            st.write("Set these to enable Notion integration.")
        
        st.divider()
        
        # Content niche selection
        st.subheader("Content Settings")
        niche = st.selectbox(
            "Content Niche",
            ["technology", "business", "health", "education", "finance", "marketing"],
            index=0,
            help="Select the primary niche for content generation"
        )
        
        # Topic input
        custom_topic = st.text_input(
            "Custom Topic (Optional)",
            placeholder="e.g., Machine Learning in Healthcare",
            help="Leave empty to use trending topics research"
        )
        
        # Output settings
        st.subheader("Output Settings")
        output_formats = st.multiselect(
            "Content Formats",
            ["Article", "Twitter Thread", "LinkedIn Post", "Instagram Caption"],
            default=["Article", "Twitter Thread", "LinkedIn Post"],
            help="Select which content formats to generate"
        )
        
        return niche, custom_topic, output_formats

def initialize_agent(niche):
    """Initialize the Content Creator Agent."""
    try:
        with st.spinner("Initializing Content Creator Agent..."):
            agent = ContentCreatorAgent(niche=niche)
            if agent.portia is None:
                st.error("Failed to initialize agent. Please check your API keys.")
                return None
            st.success("Agent initialized successfully!")
            return agent
    except Exception as e:
        st.error(f"Error initializing agent: {str(e)}")
        return None

def run_content_generation(agent, custom_topic):
    """Run the content generation workflow."""
    try:
        st.session_state.generation_status = 'running'
        
        with st.spinner("Generating content... This may take a few minutes."):
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Initializing content generation...")
            progress_bar.progress(10)
            
            # Run the workflow
            if custom_topic:
                status_text.text("Generating content for custom topic...")
                progress_bar.progress(30)
                results = agent.run_content_creation_workflow(specific_topic=custom_topic)
            else:
                status_text.text("Researching trending topics...")
                progress_bar.progress(20)
                results = agent.run_content_creation_workflow()
            
            progress_bar.progress(100)
            status_text.text("Content generation completed!")
            
            st.session_state.content_results = results
            st.session_state.generation_status = 'completed'
            
            return results
            
    except Exception as e:
        st.session_state.generation_status = 'error'
        st.error(f"Error during content generation: {str(e)}")
        return None

def display_content_results(results, output_formats):
    """Display the generated content results."""
    if not results or 'results' not in results:
        return
    
    st.header("Generated Content")
    
    for i, result in enumerate(results['results']):
        topic = result.get('topic', 'Unknown Topic')
        content_data = result.get('content_data', {})
        
        # Topic header
        st.subheader(f"📄 {topic}")
        
        # Status and metadata
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Status", result.get('status', 'Unknown').replace('_', ' ').title())
        with col2:
            st.metric("Created", result.get('created_at', 'Unknown')[:10])
        with col3:
            article_length = len(content_data.get('long_form_content', ''))
            st.metric("Article Length", f"{article_length:,} chars")
        
        # Content tabs
        tabs = st.tabs(["Article", "Social Media", "SEO Info", "Files"])
        
        with tabs[0]:
            if "Article" in output_formats and content_data.get('long_form_content'):
                st.markdown("### 📝 Long-form Article")
                with st.container():
                    st.markdown(f"**Title:** {content_data.get('title', 'N/A')}")
                    st.markdown(f"**Meta Description:** {content_data.get('meta_description', 'N/A')}")
                    st.markdown("---")
                    st.markdown(content_data['long_form_content'])
        
        with tabs[1]:
            col1, col2 = st.columns(2)
            
            with col1:
                if "Twitter Thread" in output_formats and content_data.get('twitter_thread'):
                    st.markdown("### 🐦 Twitter Thread")
                    st.text_area("", content_data['twitter_thread'], height=150, key=f"twitter_{i}")
                
                if "LinkedIn Post" in output_formats and content_data.get('linkedin_post'):
                    st.markdown("### 💼 LinkedIn Post")
                    st.text_area("", content_data['linkedin_post'], height=150, key=f"linkedin_{i}")
            
            with col2:
                if "Instagram Caption" in output_formats and content_data.get('instagram_caption'):
                    st.markdown("### 📷 Instagram Caption")
                    st.text_area("", content_data['instagram_caption'], height=100, key=f"instagram_{i}")
        
        with tabs[2]:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 🔍 Keywords")
                keywords = content_data.get('keywords', [])
                for keyword in keywords:
                    st.write(f"• {keyword}")
            
            with col2:
                st.markdown("### 🏷️ Tags")
                tags = content_data.get('tags', [])
                for tag in tags:
                    st.write(f"• {tag}")
        
        with tabs[3]:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 📁 Local Files")
                local_files = result.get('local_files', 'N/A')
                st.write(f"Saved to: `{local_files}`")
            
            with col2:
                st.markdown("### 🗃️ Notion")
                notion_url = result.get('notion_url', 'N/A')
                if notion_url.startswith('http'):
                    st.markdown(f"[Open in Notion]({notion_url})")
                else:
                    st.write(notion_url)
        
        # Download buttons
        st.markdown("### 📥 Downloads")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(f"Download JSON", key=f"json_{i}"):
                json_data = json.dumps(content_data, indent=2)
                st.download_button(
                    label="💾 Download JSON",
                    data=json_data,
                    file_name=f"{topic.replace(' ', '_').lower()}.json",
                    mime="application/json",
                    key=f"json_download_{i}"
                )
        
        with col2:
            if content_data.get('long_form_content'):
                st.download_button(
                    label="📄 Download Article",
                    data=content_data['long_form_content'],
                    file_name=f"{topic.replace(' ', '_').lower()}_article.md",
                    mime="text/markdown",
                    key=f"article_download_{i}"
                )
        
        if i < len(results['results']) - 1:
            st.divider()

def main():
    """Main Streamlit application."""
    init_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">Content Flux</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">AI-powered Content Creation & Distribution Pipeline</p>', unsafe_allow_html=True)
    
    # Sidebar
    niche, custom_topic, output_formats = display_sidebar()
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 🚀 Generate Content")
        st.write("Create comprehensive, multi-format content using AI-powered research and generation.")
        
        # Topic display
        if custom_topic:
            st.info(f"**Custom Topic:** {custom_topic}")
        else:
            st.info(f"**Mode:** Research trending topics in {niche}")
    
    with col2:
        st.markdown("### 🎛️ Controls")
        
        # Generate button
        if st.button("🎯 Generate Content", type="primary", use_container_width=True):
            # Initialize agent if not already done
            if st.session_state.agent is None or st.session_state.agent.niche != niche:
                st.session_state.agent = initialize_agent(niche)
            
            if st.session_state.agent:
                run_content_generation(st.session_state.agent, custom_topic)
        
        # Clear button
        if st.button("🗑️ Clear Results", use_container_width=True):
            st.session_state.content_results = None
            st.session_state.generation_status = 'idle'
            st.rerun()
    
    # Display results
    if st.session_state.content_results:
        st.divider()
        display_content_results(st.session_state.content_results, output_formats)
    elif st.session_state.generation_status == 'error':
        st.error("Content generation failed. Please check your configuration and try again.")
    elif st.session_state.generation_status == 'idle':
        # Instructions
        st.markdown("### 📋 How to Use")
        st.markdown("""
        1. **Configure Environment**: Set your API keys in the `.env` file
        2. **Select Niche**: Choose your content niche from the sidebar
        3. **Custom Topic** (Optional): Enter a specific topic or let AI research trending topics
        4. **Generate**: Click the "Generate Content" button to start
        5. **Review & Download**: Review generated content and download in various formats
        """)
        
        st.markdown("### ⚙️ Required Setup")
        st.code("""
# Create .env file with:
PORTIA_API_KEY=your_portia_key_here
GOOGLE_API_KEY=your_google_key_here
TAVILY_API_KEY=your_tavily_key_here
NOTION_API_KEY=your_notion_key_here 
NOTION_DATABASE_ID=your_database_id
        """)

if __name__ == "__main__":
    main()