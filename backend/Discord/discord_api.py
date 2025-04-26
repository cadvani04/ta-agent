# discord_api.py
import os, httpx
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
        # 1) create guild
        resp = await client.post(f"{BASE_URL}/guilds", json={"name": name}, headers=headers)
        resp.raise_for_status()
        guild = resp.json()
        ctx.logger.info(f"Created guild {guild['id']}")

        # 2) create a #general channel
        await create_channel(guild["id"], "general", client, headers, ctx)
        return guild

async def create_channel(guild_id, channel_name, client, headers, ctx: Context):
    body = {"name": channel_name, "type": 0}
    resp = await client.post(f"{BASE_URL}/guilds/{guild_id}/channels", json=body, headers=headers)
    resp.raise_for_status()
    channel = resp.json()
    ctx.logger.info(f"Created channel {channel['id']}")
    return channel
