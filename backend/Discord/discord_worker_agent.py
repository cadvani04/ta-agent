# discord_worker_agent.py
from uagents import Agent, Context, on_envelope
from discord_api import create_discord_guild

worker = Agent(
    name="discord-worker",
    seed="another_secret_seed",
    port=8001,
    endpoint=["http://localhost:8001/submit"]
)

@worker.on_event("startup")
async def init(ctx: Context):
    ctx.logger.info("Worker ready to process Discord jobs")

@on_envelope  # listens for any envelope addressed to “discord-worker”
async def process_job(msg: dict, ctx: Context):
    # msg would contain something like {"name": "My New Server", ...}
    guild = await create_discord_guild(msg["name"], ctx)
    ctx.logger.info(f"Done creating guild {guild['id']}")

# helper to let orchestrator enqueue onto the Fetch network
async def enqueue_create_job(server_name: str, ctx: Context):
    envelope = {"agent": "discord-worker", "body": {"name": server_name}}
    await ctx.send_envelope(envelope)

if __name__ == "__main__":
    worker.run()
