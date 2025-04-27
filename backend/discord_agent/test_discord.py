import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def main():
    # payload must match your CreateServerRequest (expects "name", not "server_name")
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    print(DISCORD_TOKEN)
    data = {
        "name": "My Test Discord Server"
    }
    
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",     # your bot token
        "Content-Type": "application/json",
        "User-Agent": "RevampAgent (https://github.com/cadvani04/revamp, v1.0)"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/create_discord",
            headers=headers,
            json=data
        )
        
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    asyncio.run(main())
