import os
import time
import httpx
from typing import List, Optional
from uagents import Agent, Context, Model
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is not set")

# Define request/response models
class ReadMessagesRequest(Model):
    guild_id: str
    channel_id: str
    limit: int = 50  # Default to 50 messages
    before: Optional[str] = None  # Message ID to fetch messages before

class Message(Model):
    id: str
    content: str
    author: str
    author_id: str
    timestamp: str
    attachments: List[str] = []

class ReadMessagesResponse(Model):
    success: bool
    message: str
    timestamp: int
    messages: List[Message] = []

# Create the agent
agent = Agent(
    name="discord-read-agent", 
    seed="discord_read_seed_phrase", 
    port=8001,  # Different port from discord-agent
    endpoint=["http://localhost:8001/submit"]
)

# Discord API functions
async def fetch_discord_messages(guild_id: str, channel_id: str, limit: int, before: Optional[str], ctx: Context):
    BASE_URL = "https://discord.com/api/v10"
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "MyDiscordBot (https://example.com, v1.0)"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Build query parameters
            params = {"limit": limit}
            if before:
                params["before"] = before
                
            ctx.logger.info(f"Fetching messages from guild {guild_id}, channel {channel_id}")
            
            # Fetch messages
            resp = await client.get(
                f"{BASE_URL}/channels/{channel_id}/messages", 
                params=params,
                headers=headers
            )
            
            # Log response for debugging
            ctx.logger.info(f"Discord API response: {resp.status_code}")
            
            if resp.status_code >= 400:
                ctx.logger.error(f"Error response: {resp.text}")
                raise Exception(f"Discord API error: {resp.status_code} - {resp.text}")
                
            resp.raise_for_status()
            messages_data = resp.json()
            
            # Process messages
            messages = []
            for msg in messages_data:
                # Extract attachments URLs
                attachment_urls = [attachment["url"] for attachment in msg.get("attachments", [])]
                
                messages.append(Message(
                    id=msg["id"],
                    content=msg["content"],
                    author=msg["author"]["username"],
                    author_id=msg["author"]["id"],
                    timestamp=msg["timestamp"],
                    attachments=attachment_urls
                ))
            
            ctx.logger.info(f"Fetched {len(messages)} messages")
            return messages
            
    except Exception as e:
        ctx.logger.error(f"Error in Discord API operations: {str(e)}")
        raise

# HTTP endpoint
@agent.on_rest_post("/read_messages", ReadMessagesRequest, ReadMessagesResponse)
async def handle_read_messages(ctx: Context, req: ReadMessagesRequest) -> ReadMessagesResponse:
    ctx.logger.info(f"Received request to read messages from guild: {req.guild_id}, channel: {req.channel_id}")
    
    try:
        # Fetch messages from Discord
        messages = await fetch_discord_messages(
            req.guild_id, 
            req.channel_id, 
            req.limit, 
            req.before, 
            ctx
        )
        
        return ReadMessagesResponse(
            success=True,
            message=f"Retrieved {len(messages)} messages",
            timestamp=int(time.time()),
            messages=messages
        )
    except Exception as e:
        ctx.logger.error(f"Failed to read messages: {str(e)}")
        return ReadMessagesResponse(
            success=False,
            message=f"Error: {str(e)}",
            timestamp=int(time.time())
        )

# Add a function to fetch channels in a guild
class ListChannelsRequest(Model):
    guild_id: str

class Channel(Model):
    id: str
    name: str
    type: int

class ListChannelsResponse(Model):
    success: bool
    message: str
    timestamp: int
    channels: List[Channel] = []

async def fetch_guild_channels(guild_id: str, ctx: Context):
    BASE_URL = "https://discord.com/api/v10"
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "MyDiscordBot (https://example.com, v1.0)"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            ctx.logger.info(f"Fetching channels for guild {guild_id}")
            
            resp = await client.get(
                f"{BASE_URL}/guilds/{guild_id}/channels", 
                headers=headers
            )
            
            if resp.status_code >= 400:
                ctx.logger.error(f"Error response: {resp.text}")
                raise Exception(f"Discord API error: {resp.status_code} - {resp.text}")
                
            resp.raise_for_status()
            channels_data = resp.json()
            
            channels = []
            for channel in channels_data:
                # Only include text channels (type 0)
                if channel["type"] == 0:
                    channels.append(Channel(
                        id=channel["id"],
                        name=channel["name"],
                        type=channel["type"]
                    ))
            
            ctx.logger.info(f"Fetched {len(channels)} text channels")
            return channels
            
    except Exception as e:
        ctx.logger.error(f"Error fetching channels: {str(e)}")
        raise

@agent.on_rest_post("/list_channels", ListChannelsRequest, ListChannelsResponse)
async def handle_list_channels(ctx: Context, req: ListChannelsRequest) -> ListChannelsResponse:
    ctx.logger.info(f"Received request to list channels for guild: {req.guild_id}")
    
    try:
        channels = await fetch_guild_channels(req.guild_id, ctx)
        
        return ListChannelsResponse(
            success=True,
            message=f"Retrieved {len(channels)} channels",
            timestamp=int(time.time()),
            channels=channels
        )
    except Exception as e:
        ctx.logger.error(f"Failed to list channels: {str(e)}")
        return ListChannelsResponse(
            success=False,
            message=f"Error: {str(e)}",
            timestamp=int(time.time())
        )

if __name__ == "__main__":
    agent.run()
