# Cloud Engine Bot - Free Fire Bot Control Panel

## Overview
This is a Free Fire game bot control panel with a web interface. The project consists of:
- **Backend Bot (main.py)**: Handles TCP connections to Free Fire game servers, manages bot state, and provides an internal API
- **Web Panel (web_panel.py)**: Flask-based web interface for controlling the bot

## Project Structure
```
.
├── main.py              # Main bot with async TCP connections and aiohttp API
├── web_panel.py         # Flask web interface
├── start.sh             # Startup script that runs both services
├── xC4.py              # Crypto/encoding utilities
├── xHeaders.py         # Headers and helper functions
├── Pb2/                # Protobuf message definitions
│   ├── DEcwHisPErMsG_pb2.py
│   ├── MajoRLoGinrEs_pb2.py
│   ├── PorTs_pb2.py
│   ├── MajoRLoGinrEq_pb2.py
│   ├── sQ_pb2.py
│   └── Team_msg_pb2.py
├── templates/
│   └── index.html      # Web interface HTML
├── static/
│   └── images/         # Emote images (referenced in HTML)
└── requirements.txt    # Python dependencies
```

## Architecture
1. **main.py** runs the bot backend:
   - Connects to Free Fire game servers via TCP
   - Manages bot authentication and session
   - Runs an aiohttp API server on localhost:8080
   - Processes commands from the web panel

2. **web_panel.py** provides the web interface:
   - Flask app running on 0.0.0.0:5000
   - Sends commands to the bot via localhost:8080 API
   - Provides UI for emote management, squad actions, etc.

## Technology Stack
- **Python 3.11**
- **Flask** - Web framework
- **aiohttp** - Async HTTP client/server
- **Protobuf** - Message serialization
- **PyCryptodome** - Encryption/decryption
- **asyncio** - Async/await support

## Running the Project
The project uses a single workflow that runs both services:
```bash
bash start.sh
```

This starts:
1. main.py (bot backend) in the background
2. web_panel.py (web interface) on port 5000

## Features
- Target Management: Add/remove player targets
- Emote Control: Send emotes to players
- Squad Management: Join/create squads, invite players
- Real-time bot status monitoring

## Configuration
- Bot credentials are hardcoded in main.py (lines 390-391)
- Web panel binds to 0.0.0.0:5000 for Replit compatibility
- Backend API runs on localhost:8080

## Recent Changes
- 2025-11-14: Initial setup for Replit environment
  - Installed Python 3.11 and dependencies
  - Updated web_panel.py to bind to 0.0.0.0:5000
  - Created start.sh to run both services
  - Configured workflow for Replit webview
  - Added .gitignore for Python files

## Notes
- The bot connects to Free Fire India (IND) region servers
- Missing emote images in static/images/ will show as broken links but don't affect functionality
- The web interface works properly despite missing image assets
