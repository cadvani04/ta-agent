import os
import httpx
import asyncio
import json
from dotenv import load_dotenv

load_dotenv()

async def main():
    # Use the exact token from your successful PowerShell command
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    print(DISCORD_TOKEN)
    
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "MyDiscordBot (https://example.com, v1.0)"
    }
    
    # Use the exact same JSON structure
    data = {"name": "My New Server"}
    
    # Make a direct request to Discord API (bypassing your agent)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/create_discord",
            headers=headers,
            json=data
        )
        
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200 or response.status_code == 201:
            guild = response.json()
            print(guild)
            print(f"Created guild with ID: {guild['guild_id']}")
            print(f"Invite link: {guild['invite_link']}")

if __name__ == "__main__":
    asyncio.run(main()) 