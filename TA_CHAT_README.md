# TA Agent Chat Interface

A clean, minimalistic, light-purple themed chat interface for the TA Agent system. This interface provides a browser-based UI for the master agent functionality from main-test.py.

## Features

- Pretty light-purple themed UI
- Real-time chat with WebSockets
- Full integration with the master agent (Canvas, Discord, Slack, AI checking)
- Code formatting and markdown support
- Responsive design that works on all devices

## Setup and Running

1. Install required dependencies:
   ```
   pip install fastapi uvicorn python-dotenv jinja2
   ```

2. Make sure you have your environment variables set up in a `.env` file:
   - OPENAI_API_KEY
   - CANVAS_API_URL
   - CANVAS_API_TOKEN
   - Other required tokens for Discord/Slack

3. Run the chat server:
   ```
   python ta_chat_server.py
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

## How it Works

The chat interface consists of two main components:

1. **Backend (`ta_chat_server.py`)**: A FastAPI server that:
   - Connects to the master agent from the backend folder
   - Handles WebSocket communication
   - Processes user messages through the agent
   - Returns responses to the UI

2. **Frontend (`ta_chat.html`)**: A clean HTML/CSS/JavaScript interface that:
   - Connects to the server via WebSockets
   - Displays messages with pretty formatting
   - Shows typing indicators during processing
   - Supports code blocks and formatting

## Usage Tips

- The interface maintains all functionality of the original terminal-based system
- You can ask about Canvas courses, assignments, and quizzes
- You can query Discord and Slack messages
- You can check text for AI-generated content
- Press Enter to send a message (Shift+Enter for a new line)
