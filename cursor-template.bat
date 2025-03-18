@echo off
REM Set environment variables from .cursor/mcp.json
set GEMINI_API_KEY=key

REM Define absolute directory path
set ABSOLUTE_DIR=/path/to/your/project

REM Set UV path
set UV_PATH=/path/to/your/uv.exe

REM Change to the project directory
cd "%ABSOLUTE_DIR%"
call "%ABSOLUTE_DIR%\.venv\Scripts\activate.bat"

REM Run with uv directly using the environment variable
"%UV_PATH%" --directory "%ABSOLUTE_DIR%" run mcp run "%ABSOLUTE_DIR%\server.py"