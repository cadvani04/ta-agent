import time
import os
import httpx
from typing import Any, Dict
from uagents import Agent, Context, Model
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is not set")

# Define request/response models
class CreateServerRequest(Model):
    name: str

class CreateServerResponse(Model):
    success: bool
    message: str
    timestamp: int
    guild_id: str = ""
    invite_link: str = ""  # New field for the invite link

# Create the agent
agent = Agent(
    name="discord-agent", 
    seed="discord_seed_phrase", 
    port=8000, 
    endpoint=["http://localhost:8000/submit"]
)

# Discord API functions
async def create_discord_guild(name: str, ctx: Context):
    BASE_URL = "https://discord.com/api/v10"
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "MyDiscordBot (https://example.com, v1.0)"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Create guild
            ctx.logger.info(f"Creating Discord server: {name}")
            ctx.logger.info(f"Using token: {DISCORD_TOKEN[:10]}...")
            
            resp = await client.post(
                f"{BASE_URL}/guilds", 
                json={"name": name},
                headers=headers
            )
            
            # Log response for debugging
            ctx.logger.info(f"Discord API response: {resp.status_code}")
            ctx.logger.info(f"Response body: {resp.text}")
            
            if resp.status_code >= 400:
                ctx.logger.error(f"Error response: {resp.text}")
                raise Exception(f"Discord API error: {resp.status_code} - {resp.text}")
                
            resp.raise_for_status()
            guild = resp.json()
            guild_id = guild['id']
            ctx.logger.info(f"Created server with ID: {guild_id}")
            
            # Create a general channel
            ctx.logger.info(f"Creating #general channel in guild {guild_id}")
            channel_resp = await client.post(
                f"{BASE_URL}/guilds/{guild_id}/channels", 
                json={"name": "general", "type": 0},  # 0 = text channel
                headers=headers
            )
            
            if channel_resp.status_code >= 400:
                ctx.logger.error(f"Error creating channel: {channel_resp.text}")
                raise Exception(f"Discord API error: {channel_resp.status_code} - {channel_resp.text}")
                
            channel_resp.raise_for_status()
            channel = channel_resp.json()
            channel_id = channel['id']
            ctx.logger.info(f"Created channel with ID: {channel_id}")
            
            # Create an invite for the channel
            ctx.logger.info(f"Creating invite for channel {channel_id}")
            invite_resp = await client.post(
                f"{BASE_URL}/channels/{channel_id}/invites",
                json={
                    "max_age": 0,  # Never expire
                    "max_uses": 0,  # Unlimited uses
                    "temporary": False
                },
                headers=headers
            )
            
            if invite_resp.status_code >= 400:
                ctx.logger.error(f"Error creating invite: {invite_resp.text}")
                raise Exception(f"Discord API error: {invite_resp.status_code} - {invite_resp.text}")
                
            invite_resp.raise_for_status()
            invite = invite_resp.json()
            invite_code = invite['code']
            invite_link = f"https://discord.gg/{invite_code}"
            ctx.logger.info(f"Created invite link: {invite_link}")
            
            # Add the invite link to the guild object
            guild['invite_link'] = invite_link
            
            return guild
    except Exception as e:
        ctx.logger.error(f"Error in Discord API operations: {str(e)}")
        raise

# HTTP endpoint
@agent.on_rest_post("/create_discord", CreateServerRequest, CreateServerResponse)
async def handle_create_server(ctx: Context, req: CreateServerRequest) -> CreateServerResponse:
    ctx.logger.info(f"Received request to create server: {req.name}")
    
    try:
        # Create the Discord server
        guild = await create_discord_guild(req.name, ctx)
        
        return CreateServerResponse(
            success=True,
            message=f"Created Discord server '{req.name}'",
            timestamp=int(time.time()),
            guild_id=guild['id'],
            invite_link=guild['invite_link']# Include the invite link in the response
        )
    except Exception as e:
        ctx.logger.error(f"Failed to create server: {str(e)}")
        return CreateServerResponse(
            success=False,
            message=f"Error: {str(e)}",
            timestamp=int(time.time())
        )

if __name__ == "__main__":
    agent.run() 