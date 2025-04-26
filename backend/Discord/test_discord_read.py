import os
import httpx
import asyncio
import json
from dotenv import load_dotenv

load_dotenv()

# Hardcoded IDs from your logs
DEFAULT_GUILD_ID = "1365645827237871788"
DEFAULT_CHANNEL_ID = "1365645829183901768"

# Get the guild ID from environment variable, hardcoded value, or prompt the user
def get_guild_id():
    guild_id = os.getenv("DISCORD_GUILD_ID")
    if not guild_id:
        print(f"Using hardcoded Guild ID: {DEFAULT_GUILD_ID}")
        return DEFAULT_GUILD_ID
    return guild_id

async def test_list_channels():
    print("\n=== Testing List Channels ===")
    guild_id = get_guild_id()
    print(f"Using guild ID: {guild_id}")
    
    data = {"guild_id": guild_id}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/list_channels",
            json=data
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            
            if result['success'] and result['channels']:
                print("\nAvailable channels:")
                for channel in result['channels']:
                    print(f"- {channel['name']} (ID: {channel['id']})")
                
                # Save the first channel ID for the next test
                return result['channels'][0]['id']
            else:
                print("No channels found or request failed")
                return None
        else:
            print(f"Error: {response.text}")
            return None

async def test_read_messages(channel_id=None):
    print("\n=== Testing Read Messages ===")
    guild_id = get_guild_id()
    
    if not channel_id:
        print(f"Using hardcoded Channel ID: {DEFAULT_CHANNEL_ID}")
        channel_id = DEFAULT_CHANNEL_ID
    
    print(f"Using guild ID: {guild_id}")
    print(f"Using channel ID: {channel_id}")
    
    data = {
        "guild_id": guild_id,
        "channel_id": channel_id,
        "limit": 10  # Fetch 10 most recent messages
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/read_messages",
            json=data
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            
            if result['success'] and result['messages']:
                print("\nMessages:")
                for msg in result['messages']:
                    print(f"[{msg['author']}]: {msg['content']}")
                    if msg['attachments']:
                        print(f"  Attachments: {', '.join(msg['attachments'])}")
            else:
                print("No messages found or request failed")
        else:
            print(f"Error: {response.text}")

async def main():
    print("=== Discord Read Agent Test ===")
    
    # Test option 1: Run both tests in sequence
    channel_id = await test_list_channels()
    await test_read_messages(channel_id)
    
    # Test option 2: Skip to reading messages with hardcoded channel ID
    # Uncomment the line below to test just reading messages
    # await test_read_messages()

if __name__ == "__main__":
    asyncio.run(main()) 