# discord_api.py
import os, httpx, json
from uagents import Context
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Discord token from environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is not set")

BASE_URL = "https://discord.com/api/v10"

async def create_discord_guild(name: str, ctx: Context):
    headers = {
      "Authorization": f"Bot {DISCORD_TOKEN}",
      "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            # 1) create guild
            ctx.logger.info(f"Attempting to create guild with name: {name}")
            resp = await client.post(f"{BASE_URL}/guilds", json={"name": name}, headers=headers)
            
            # Log the full response for debugging
            ctx.logger.info(f"Discord API response status: {resp.status_code}")
            ctx.logger.info(f"Discord API response body: {resp.text}")
            
            resp.raise_for_status()
            guild = resp.json()
            ctx.logger.info(f"Created guild {guild['id']} with name {guild['name']}")

            # 2) create a #general channel
            await create_channel(guild["id"], "general", client, headers, ctx)
            return guild
        except httpx.HTTPStatusError as e:
            ctx.logger.error(f"HTTP error creating guild: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            ctx.logger.error(f"Error creating guild: {str(e)}")
            raise

async def create_channel(guild_id, channel_name, client, headers, ctx: Context):
    try:
        body = {"name": channel_name, "type": 0}
        ctx.logger.info(f"Creating channel {channel_name} in guild {guild_id}")
        resp = await client.post(f"{BASE_URL}/guilds/{guild_id}/channels", json=body, headers=headers)
        resp.raise_for_status()
        channel = resp.json()
        ctx.logger.info(f"Created channel {channel['id']} with name {channel['name']}")
        return channel
    except Exception as e:
        ctx.logger.error(f"Error creating channel: {str(e)}")
        raise
