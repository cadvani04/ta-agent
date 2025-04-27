import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the discord_openai module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Discord.discord_openai import (
    list_discord_channels,
    read_discord_messages,
    create_discord_server
)

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv('discord_token')
if not DISCORD_TOKEN:
    print("Error: discord_token must be set in .env file")
    sys.exit(1)

# Default guild and channel IDs for testing
CSE30_GUILD_ID = "1365757418998464593"
CSE30_CHANNEL_ID = "1365757421938544721"
MATH19B_GUILD_ID = "1365763509006372927"
MATH19B_CHANNEL_ID = "1365763511040610365"

def test_list_channels():
    """Test listing channels in a Discord server."""
    print("\n=== Testing List Channels ===")
    
    for name, guild_id in [("CSE30", CSE30_GUILD_ID), ("MATH19B", MATH19B_GUILD_ID)]:
        try:
            print(f"\nListing channels in {name} server (ID: {guild_id})...")
            channels = list_discord_channels(guild_id)
            print(f"Found {len(channels)} channels:")
            for channel in channels:
                print(f"- {channel['name']} (ID: {channel['id']}, Type: {channel['type']})")
        except Exception as e:
            print(f"Error listing channels in {name} server: {e}")

def test_read_messages():
    """Test reading messages from Discord channels."""
    print("\n=== Testing Read Messages ===")
    
    for name, guild_id, channel_id in [
        ("CSE30", CSE30_GUILD_ID, CSE30_CHANNEL_ID),
        ("MATH19B", MATH19B_GUILD_ID, MATH19B_CHANNEL_ID)
    ]:
        try:
            print(f"\nReading messages from {name} channel (ID: {channel_id})...")
            messages = read_discord_messages(guild_id, channel_id, limit=5)
            print(f"Found {len(messages)} messages:")
            for msg in messages:
                print(f"- {msg['author']}: {msg['content']}")
        except Exception as e:
            print(f"Error reading messages from {name} channel: {e}")

def test_create_server():
    """Test creating a Discord server."""
    print("\n=== Testing Create Server ===")
    
    # Ask for confirmation before creating a server
    confirm = input("Do you want to test creating a Discord server? (y/n): ")
    if confirm.lower() != 'y':
        print("Skipping server creation test.")
        return
    
    try:
        import time
        server_name = f"Test Server {int(time.time())}"
        print(f"\nCreating server '{server_name}'...")
        server = create_discord_server(server_name)
        print(f"Created server: {server['name']} (ID: {server['id']})")
        print(f"Invite link: {server['invite_link']}")
    except Exception as e:
        print(f"Error creating server: {e}")

def main():
    """Run all Discord API tests."""
    print("=== Discord API Testing ===")
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Test Discord API Functions')
    parser.add_argument('--test', choices=['all', 'channels', 'messages', 'server'], 
                      default='all',
                      help='Which test to run (all, channels, messages, or server)')
    args = parser.parse_args()
    
    # Run the specified test(s)
    if args.test == 'all' or args.test == 'channels':
        test_list_channels()
    
    if args.test == 'all' or args.test == 'messages':
        test_read_messages()
    
    if args.test == 'all' or args.test == 'server':
        test_create_server()
    
    print("\n=== Discord API Testing Complete ===")

if __name__ == "__main__":
    main() 