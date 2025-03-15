# AI P图 MCP Server

[English](README.md) | 中文

一个基于 MCP（模型上下文协议）的服务器，通过多种AI服务和API提供高级图像生成、修改和处理能力。

## 演示案例
原图  
<img src="https://github.com/user-attachments/assets/a987b4c4-3bba-4a52-a2a8-9f088868d857" width="300"/>  

提示词：**给狗添加一件外套**  
<img src="https://github.com/user-attachments/assets/6de3cdd1-a3b9-422b-95dd-12e2172f6f1d" width="300"/>  

提示词：**再给它加一顶帽子**  
<img src="https://github.com/user-attachments/assets/047289ca-f3d0-4d16-acf7-09d5af641c68" width="300"/>  

## 功能特性

- **图像生成**: 使用 Google Gemini 模型从文本生成图像
- **图像修改**: 根据文本指令对现有图像进行改造
- **背景移除**: 通过 remove.bg API 实现智能抠图
- **图床托管**: 使用 FreeImage.host 分享生成结果
- **资源管理**: 追踪管理生成和上传的图像资源

## 环境要求

- Python 3.11 或更高版本
- 需要以下 API 密钥：
  - Google Gemini API 密钥 [获取地址](https://aistudio.google.com/apikey)
  - FreeImage.host API 密钥 [获取地址](https://freeimage.host/page/api)
  - Remove.bg API 密钥 [获取地址](https://www.remove.bg/dashboard#api-key)

## 安装指南

1. 克隆仓库：
   ```sh
   git clone https://github.com/Kira-Pgr/Image-Toolkit-MCP-Server.git
   cd Image-Toolkit-MCP-Server
   ```

2. 安装 UV（如未安装）：
   ```sh
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # Windows
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   # 使用pip安装
   pip install uv
   ```

3. 使用 UV 安装依赖：
   ```sh
   uv venv --python=python3.11
   source .venv/bin/activate #Windows上 .venv/Scripts/activate 
   uv pip install -r requirements.txt
   ```

## 使用说明

1. **Claude Desktop 集成**：在 `claude_desktop_config.json` 中添加以下配置，即可直接从 Claude Desktop 启动服务：
   ```json
   "Image Toolkit MCP": {
     "command": "uv",
     "args": [
       "--directory",
       "/项目/路径/",
       "run",
       "mcp",
       "run",
       "/项目/路径/server.py"
     ],
     "env": {
       "GEMINI_API_KEY": "你的密钥",
       "FREEIMAGE_API_KEY": "你的密钥",
       "REMOVEBG_API_KEY": "你的密钥"
     }
   }
   ```
   注意：请将 "你的密钥" 替换为实际的 API 密钥

## 致谢

- [Google Gemini](https://aistudio.google.com/)：图像生成
- [Remove.bg](https://www.remove.bg/)：背景移除服务
- [FreeImage.host](https://freeimage.host/)：图床
- [MCP](https://modelcontextprotocol.io/introduction)：模型上下文协议标准
