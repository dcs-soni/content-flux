<h1 align="center">Content Flux 🤖</h1>
<p align="center"><i>⚡ Automating content workflows with AI-powered agents ⚡</i></p>

## **AI-powered Content Creation using PortiaAI**

Content Flux is an intelligent content creation agent that automatically researches trending topics, generates multi-format content, and saves it to a Notion Database. It leverages PortiaAI's capabilities to create comprehensive content including long-form articles, social media posts, and SEO-optimized metadata.

<p align="center">
  <a href="https://youtu.be/WQeThBQeKhY" target="_blank">
    <img src="https://img.youtube.com/vi/WQeThBQeKhY/maxresdefault.jpg" alt="Watch the video" width="600">
  </a>
</p>

## Features

- **Automated Topic Research**: Discovers trending topics in your specified niche.
- **Multi-format Content Generation**: Creates articles, Twitter threads, LinkedIn posts, and Instagram captions.
- **SEO Optimization**: Generates keywords, tags, and meta descriptions.
- **Notion Integration**: Automatically saves content to your Notion database.
- **Web Interface**: User-friendly Streamlit app for easy content management.
- **Local Storage**: Saves all generated content locally in JSON and Markdown formats.

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

   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Custom Search API
   - Create credentials and get your API key

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
