import os
import sys
import asyncio
import httpx
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool
from pydantic import BaseModel
from typing import Optional, List

# Load environment variables from .env file
load_dotenv()

# Get Discord token from environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')


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
