import os
import sys
import asyncio
import httpx
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# Import Canvas Groups functions
sys.path.append(os.path.join(os.path.dirname(__file__), 'canvas'))
from canvas_groups import (
    list_groups_in_context,
    get_group,
    create_group,
    list_group_users,
    add_user_to_group,
    get_group_activity_stream
)

# Load environment variables from .env file
load_dotenv()

# Get Discord token from environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Get Canvas token from environment variables
CANVAS_API_TOKEN = os.getenv('canvas_token')

# Get Canvas API URL from environment variables
CANVAS_API_URL = os.getenv('CANVAS_API_URL', 'https://canvas.instructure.com/api/v1')

# Default course ID for testing
DEFAULT_COURSE_ID = 11883051  # Replace with your actual course ID

# Models for Discord API
class CreateServerRequest(BaseModel):
    name: str

class CreateServerResponse(BaseModel):
    success: bool
    message: str
    timestamp: int
    guild_id: str = ""
    invite_link: str = ""

class ReadMessagesRequest(BaseModel):
    guild_id: str
    channel_id: str
    limit: int = 50
    before: Optional[str] = None

class Message(BaseModel):
    id: str
    content: str
    author: str
    author_id: str
    timestamp: str
    attachments: List[str] = []

class ReadMessagesResponse(BaseModel):
    success: bool
    message: str
    timestamp: int
    messages: List[Message] = []

class ListChannelsRequest(BaseModel):
    guild_id: str

class Channel(BaseModel):
    id: str
    name: str
    type: int

class ListChannelsResponse(BaseModel):
    success: bool
    message: str
    timestamp: int
    channels: List[Channel] = []

# Discord agent functions
@function_tool()
async def create_discord_server(name: str):
    """
    Create a new Discord server with a general channel and invite link.
    
    Args:
        name (str): The name for the new Discord server
        
    Returns:
        dict: Information about the created server including guild_id and invite_link
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/create_discord",
            json={"name": name}
        )
        
        if response.status_code != 200:
            raise Exception(f"Discord agent error: {response.text}")
            
        result = response.json()
        return {
            "success": result["success"],
            "message": result["message"],
            "guild_id": result.get("guild_id", ""),
            "invite_link": result.get("invite_link", "")
        }

@function_tool()
async def list_discord_channels(guild_id: str):
    """
    List all text channels in a Discord server.
    
    Args:
        guild_id (str): The ID of the Discord server
        
    Returns:
        dict: Information about the channels in the server
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/list_channels",
            json={"guild_id": guild_id}
        )
        
        if response.status_code != 200:
            raise Exception(f"Discord agent error: {response.text}")
            
        return response.json()

@function_tool()
async def read_discord_messages(guild_id: str, channel_id: str, limit: Optional[int] = None, before: Optional[str] = None):
    """
    Read messages from a Discord channel.
    
    Args:
        guild_id (str): The ID of the Discord server
        channel_id (str): The ID of the channel to read messages from
        limit (int, optional): Maximum number of messages to retrieve (default: 50)
        before (str, optional): Message ID to fetch messages before
        
    Returns:
        dict: Information about the messages in the channel
    """
    data = {
        "guild_id": guild_id,
        "channel_id": channel_id,
        "limit": 50 if limit is None else limit
    }
    
    if before:
        data["before"] = before
        
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/read_messages",
            json=data
        )
        
        if response.status_code != 200:
            raise Exception(f"Discord agent error: {response.text}")
            
        return response.json()

async def main():
    # Check if Discord token is set
    if not DISCORD_TOKEN:
        print("Error: DISCORD_TOKEN must be set in .env file")
        sys.exit(1)

    print(f"Using Discord token: {DISCORD_TOKEN[:10]}...")

    # Test 1: Create a Discord server
    # try:
    #     print("\n--- Test 1: Create Discord Server ---")
    #     server_name = "Test Server " + str(int(asyncio.get_event_loop().time()))
    #     print(f"Creating server with name: {server_name}")
        
    #     result = await create_discord_server(server_name)
    #     print(f"Server created: {result}")
        
    #     # Save the guild ID for later tests
    #     new_guild_id = result.get("guild_id", "")
    #     if new_guild_id:
    #         print(f"Using new guild ID for further tests: {new_guild_id}")
    #         guild_id = new_guild_id
    #     else:
    #         print(f"Using default guild ID for further tests: {DEFAULT_GUILD_ID}")
    #         guild_id = DEFAULT_GUILD_ID
            
    # except Exception as e:
    #     print(f"Error creating Discord server: {e}")
    #     guild_id = DEFAULT_GUILD_ID
    #     print(f"Using default guild ID for further tests: {guild_id}")

    # # Test 2: List channels in a server
    # try:
    #     print("\n--- Test 2: List Discord Channels ---")
    #     print(f"Listing channels for guild ID: {guild_id}")
        
    #     result = await list_discord_channels(guild_id)
    #     print(f"Channels response: {result}")
        
    #     if result.get("success") and result.get("channels"):
    #         channels = result.get("channels", [])
    #         print(f"Found {len(channels)} channels:")
    #         for channel in channels:
    #             print(f"- {channel.get('name')} (ID: {channel.get('id')})")
            
    #         # Save the first channel ID for the next test
    #         if channels:
    #             channel_id = channels[0].get("id")
    #             print(f"Using channel ID for next test: {channel_id}")
    #         else:
    #             channel_id = DEFAULT_CHANNEL_ID
    #             print(f"No channels found, using default channel ID: {channel_id}")
    #     else:
    #         channel_id = DEFAULT_CHANNEL_ID
    #         print(f"Failed to list channels, using default channel ID: {channel_id}")
            
    # except Exception as e:
    #     print(f"Error listing Discord channels: {e}")
    #     channel_id = DEFAULT_CHANNEL_ID
    #     print(f"Using default channel ID for further tests: {channel_id}")

    # # Test 3: Read messages from a channel
    # try:
    #     print("\n--- Test 3: Read Discord Messages ---")
    #     print(f"Reading messages from guild ID: {guild_id}, channel ID: {channel_id}")
        
    #     result = await read_discord_messages(guild_id, channel_id, 5)
    #     print(f"Messages response: {result}")
        
    #     if result.get("success") and result.get("messages"):
    #         messages = result.get("messages", [])
    #         print(f"Found {len(messages)} messages:")
    #         for msg in messages:
    #             print(f"[{msg.get('author')}]: {msg.get('content')}")
    #             if msg.get('attachments'):
    #                 print(f"  Attachments: {', '.join(msg.get('attachments', []))}")
    #     else:
    #         print("No messages found or request failed")
            
    # except Exception as e:
    #     print(f"Error reading Discord messages: {e}")

    # # Test 4: Run an interactive agent session
    print("\n--- Test 4: Interactive Discord Agent Session ---")
    print("Type 'exit' or 'quit' to end the session")
    
    agent = Agent(
        name="discord-management-agent",
        instructions=(
            "You are an assistant designed to help the user interact with Discord. "
            "You can create new Discord servers, list channels in a server, and read messages. "
            "When the user asks about Discord, use your tools to help them manage their Discord servers."
            "THis is the info for CSE 30: DEFAULT_GUILD_ID = 1365757418998464593, DEFAULT_CHANNEL_ID = 1365757421938544721"
            "THis is the info for MATh 19b: DEFAULT_GUILD_ID = 1365763509006372927, DEFAULT_CHANNEL_ID = 1365763511040610365"
        ),
        tools=[create_discord_server, list_discord_channels, read_discord_messages],
        model="gpt-4o-mini",
    )

    user_input = None
    result = None
    
    while True:
        user_input = input(" > ")

        if user_input.lower() in ["exit", "quit"]:
            break

        if result is not None:
            user_input = result.to_input_list() + [{"role": "user", "content": user_input}]

        result = await Runner.run(agent, user_input)
        print("Agent response: ", result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
