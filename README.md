# PromptShopMCP

![](https://badge.mcpx.dev?type=server 'MCP Server')  

English | [中文](README_ZH.md)   


A powerful MCP (Model Context Protocol) server that transforms images using simple text commands. Edit photos like a professional designer - just describe what you want in natural language!
## Demo
Original Image  
<img src="https://github.com/user-attachments/assets/a987b4c4-3bba-4a52-a2a8-9f088868d857" width="300"/>  

Prompt: **add a coat to the dog**  
<img src="https://github.com/user-attachments/assets/6de3cdd1-a3b9-422b-95dd-12e2172f6f1d" width="300"/>  

Prompt: **Add a hat to it**  
<img src="https://github.com/user-attachments/assets/047289ca-f3d0-4d16-acf7-09d5af641c68" width="300"/>  
 

##  Features

- **Image Generation**: Create images from text prompts using Google's Gemini models
- **Image Modification**: Transform existing images based on text instructions
- **Background Removal**: Remove backgrounds from images using the remove.bg API
- **Image Hosting**: Share generated images via FreeImage.host
- **Resource Management**: Track and manage generated and uploaded images

## Requirements

- Python 3.11 or higher
- Required API keys:
  - Google Gemini API key [Get key](https://aistudio.google.com/apikey)
  - FreeImage.host API key [Get key](https://freeimage.host/page/api)
  - Remove.bg API key [Get key](https://www.remove.bg/dashboard#api-key)

##  Installation

1. Clone this repository:
   ```sh
   git https://github.com/Kira-Pgr/Image-Toolkit-MCP-Server.git
   cd Image-Toolkit-MCP-Server
   ```

2. Install UV (if not already installed):
   ```sh
   # On macOS and Linux.
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # On Windows.
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   # With pip.
   pip install uv
   ```

3. Install dependencies using UV:
   ```sh
   uv venv --python=python3.11
   source .venv/bin/activate #or .venv/Scripts/activate on Windows
   uv pip install -r requirements.txt
   ```

##  Usage

1. **Claude Desktop Integration**: Add the following configuration to your `claude_desktop_config.json` file to run the server directly from Claude Desktop:
   ```json
   "PromptShopMCP": {
     "command": "uv",
     "args": [
       "--directory",
       "/project/dir/",
       "run",
       "mcp",
       "run",
       "/project/dir/server.py"
     ],
     "env": {
       "GEMINI_API_KEY": "key",
       "FREEIMAGE_API_KEY": "key",
       "REMOVEBG_API_KEY": "key"
     }
   }
   ```
   Note: Replace the placeholder `"key"` values with your actual API keys.
2. **Cursor Integration**: Modify the `cursor.sh` file to set your API keys and project directory.   
  * In cursor settings, go to the "MCP" tab, click on `Add new MCP server`,   
  * Name the server whatever you want, and set the command to `sh /absolute/path/to/cursor.sh`.   
  * Wait for the server to start, and you can see the server and available tools.   
  * Then when you use the agent, it would automatically detect whether use the tools.   
  <img width="1240" alt="image" src="https://github.com/user-attachments/assets/b41016fe-a0f8-4029-8f5d-82f25c606a65" />


## Acknowledgements

- [Google Gemini](https://aistudio.google.com/): For the image generation capabilities
- [Remove.bg](https://www.remove.bg/): For background removal services
- [FreeImage.host](https://freeimage.host/): For image hosting services
- [MCP](https://modelcontextprotocol.io/introduction): For the Model Context Protocol
