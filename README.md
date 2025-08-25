<h1 align="center">Content Flux 🤖</h1>
<p align="center"><i>⚡ Automating content workflows with AI-powered agents ⚡</i></p>

<h2 align="center">AI-powered Content Creation using PortiaAI</h2>

Content Flux is an intelligent content creation agent that automatically researches trending topics, generates multi-format content, and saves it to a Notion Database. It leverages PortiaAI's capabilities to create comprehensive content including long-form articles, social media posts, and SEO-optimized metadata.

<h4 align="center">Full Demo video ⬇️</h4>

<p align="center">
  <a href="https://youtu.be/7wv6YasLo2o" target="_blank">
    <img src="https://img.youtube.com/vi/7wv6YasLo2o/maxresdefault.jpg" alt="Watch the video" width="600">
  </a>
</p>

## Features

- **Automated Topic Research**: Discovers trending topics in your specified niche.
- **Multi-format Content Generation**: Creates articles, Twitter threads, LinkedIn posts, and Instagram captions.
- **SEO Optimization**: Generates keywords, tags, and meta descriptions.
- **Notion Integration**: Automatically saves content to your Notion database.
- **Web Interface**: User-friendly Streamlit app for easy content management.
- **Local Storage**: Saves all generated content locally in JSON and Markdown formats.

## Technical Architecture

### Portia AI Agent Framework

Content Flux leverages **PortiaAI** as its core AI agent framework, providing advanced capabilities for autonomous content creation. The system demonstrates sophisticated AI agent orchestration with multi-tool integration and intelligent planning.

#### AI Agent Capabilities & Impact

**Autonomous Decision Making & Originality:**

The Portia agent researches topics, studies trends, and changes its plan as needed. It uses PortiaAI’s tools to create more than just basic content, combining information from many sources. From a single word or idea, it can make different types of content that fit each platform’s rules.

#### Tool Integration & Planning

The Portia agent utilizes a sophisticated tool ecosystem:

**Core Tools:**

- **LLM Tool**: Primary reasoning and content generation engine.
- **File Writer Tool**: Automated file creation and management for content storage.
- **Notion MCP with notion_create_pages tool**: Direct database integration for seamless content publishing.
- **Tavily Tool**: Advanced web search and research capabilities for trend discovery

**Intelligent Tool Planning:**

- **Sequential Planning**: Agent plans multi-step workflows **(research → analysis → content creation → publishing)**.
- **Adaptive Execution**: Modifies plans based on tool results and intermediate findings
- **Parallel Processing**: Executes multiple tools simultaneously when possible for efficiency
- **Error Recovery**: Automatically handles tool failures and retries with fallback approaches.

#### Agent Workflow Architecture

```
Research Phase → Analysis Phase → Creation Phase → Publishing Phase
     ↓              ↓                 ↓                    ↓
Tavily Tool    →  LLM Tool      →  LLM Tool      →     Notion MCP
                    ↓                 ↓                File Writer
              Planning Logic      Content Gen.
```

**Dynamic Planning Example:**

1. Agent receives niche specification.
2. Plans research strategy using Tavily.
3. Analyzes trends and selects optimal topics.
4. Plans content formats based on topic characteristics.
5. Generates content using creative writing techniques.
6. Plans publishing strategy (Notion + local storage).
7. Executes publishing with error handling.

## Quick Start

### Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) (automatically installed by startup scripts)
- API keys for required services

### 1. Clone the Repository

```bash
git clone <repository-url>
cd content-flux
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
# Required API Keys
PORTIA_API_KEY=your_portia_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here


# Optional but recomended Notion Integration
NOTION_API_KEY=your_notion_api_key_here
NOTION_DATABASE_ID=your_notion_database_id_here
NOTION_API_VERSION=2022-06-28
```

### 3. Run the Application

**For Windows:**

```bash
start.bat
```

**For Linux/Mac:**

```bash
chmod +x start.sh
./start.sh
```

The Streamlit web interface will be available at: `http://localhost:8501`

## Detailed Setup

### API Keys Setup

1. **Portia API Key** (Required):

   - Sign up at [Portia](https://portia.ai)
   - Generate an API key from your dashboard

2. **Google API Key** (Required):

   - Go to [Google AI for Developers](https://console.cloud.google.com/)
   - Sign in using your google email.
   - Get an API key.

3. **Notion Integration** (Optional, butt recomended):
   - Create a Notion integration at [Notion Developers](https://developers.notion.com/)
   - Get your API key and database ID
   - Ensure the integration has access to your target database

### Manual Installation

If you prefer manual setup:

```bash
# Install uv (if not already installed)
pip install uv

# Install dependencies
uv sync

# Run the web app
uv run streamlit run streamlit_app.py

# Or run the CLI version
uv run python main.py
```

## Usage

### Web Interface

1. Open `http://localhost:8501` in your browser
2. Configure your content niche from the sidebar
3. Optionally specify a custom topic or let AI research trending topics
4. Select desired output formats
5. Click "Generate Content" and wait for the results
6. Download generated content in various formats

### Command Line Interface

```bash
uv run python main.py
```

Follow the prompts to:

- Enter your content niche
- Specify a topic or use trending research
- View and save generated content

## Configuration

### Streamlit Configuration

The app uses custom Streamlit configuration in `.streamlit/config.toml`:

- Runs on port 8501

### Output Formats

Available content formats:

- **Long-form Articles**: Comprehensive blog posts with SEO optimization
- **Twitter Threads**: Multi-tweet threads with engagement hooks
- **LinkedIn Posts**: Professional content optimized for LinkedIn
- **Instagram Captions**: Visual-friendly captions with hashtags

## Troubleshooting

### Common Issues

1. **API Key Errors**:

   - Ensure all required API keys are set in `.env`
   - Verify API keys are valid and have proper permissions

2. **Module Import Errors**:

   - Run `uv sync` to ensure all dependencies are installed
   - Check Python version compatibility (3.11+)

3. **Streamlit Port Issues**:

   - Change port in `.streamlit/config.toml` if 8501 is occupied
   - Kill existing Streamlit processes

4. **Content Generation Fails**:
   - Check internet connection for API calls
   - Verify Google Custom Search API is enabled
   - Review error messages in the web interface

## Acknowledgments

- [PortiaAI](https://portia.ai) for the AI agent framework.
- [Streamlit](https://streamlit.io) for the web interface.
