#!/bin/bash
echo "Starting Content Flux Streamlit App..."
echo

# Check if .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please create a .env file with your API keys."
    echo
    echo "Example .env content:"
    echo "PORTIA_API_KEY=your_portia_key_here"
    echo "GOOGLE_API_KEY=your_google_key_here"
    echo "NOTION_API_KEY=your_notion_key_here"
    echo "NOTION_DATABASE_ID=your_database_id_here"
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    pip install uv
fi

# Install dependencies
echo "Installing dependencies..."
uv sync

# Start Streamlit app
echo "Starting Streamlit app..."
echo "App will be available at: http://localhost:8501"
echo
uv run streamlit run streamlit_app.py