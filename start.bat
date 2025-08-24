@echo off
echo Starting Content Flux Streamlit App...
echo.

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please create a .env file with your API keys.
    echo.
    echo Example .env content:
    echo PORTIA_API_KEY=your_portia_key_here
    echo GOOGLE_API_KEY=your_google_key_here
    echo NOTION_API_KEY=your_notion_key_here
    echo NOTION_DATABASE_ID=your_database_id_here
    pause
    exit /b 1
)

REM Check if uv is installed
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing uv...
    pip install uv
)

REM Install dependencies
echo Installing dependencies...
uv sync

REM Start Streamlit app
echo Starting Streamlit app...
echo App will be available at: http://localhost:8501
echo.
uv run streamlit run streamlit_app.py

pause