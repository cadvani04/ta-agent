import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Print all environment variables that start with SLACK
print("Slack-related environment variables:")
for key, value in os.environ.items():
    if key.startswith("SLACK"):
        # Print only the first few characters of the token for security
        masked_value = value[:10] + "..." if value else "None"
        print(f"{key}: {masked_value}")

# Check specific tokens
math_token = os.environ.get("SLACK_BOT_MATH")
cse_token = os.environ.get("SLACK_BOT_CSE")

print("\nSLACK_BOT_MATH token:")
if math_token:
    print(f"- Starts with: {math_token[:10]}...")
    print(f"- Length: {len(math_token)} characters")
    print(f"- Valid format: {'Yes' if math_token.startswith(('xoxb-', 'xoxp-')) else 'No'}")
else:
    print("- Not found")

print("\nSLACK_BOT_CSE token:")
if cse_token:
    print(f"- Starts with: {cse_token[:10]}...")
    print(f"- Length: {len(cse_token)} characters")
    print(f"- Valid format: {'Yes' if cse_token.startswith(('xoxb-', 'xoxp-')) else 'No'}")
else:
    print("- Not found") 