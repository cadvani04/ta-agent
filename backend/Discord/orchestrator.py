# orchestrator_agent.py
from uagents import Agent, Context, on_rest_post
from pydantic import BaseModel
from discord_worker_agent import enqueue_create_job

class CreateServerRequest(BaseModel):
    name: str

agent = Agent(
    name="discord-orchestrator",
    seed="your_super_secret_seed",
    port=8000,
    endpoint=["http://localhost:8000/submit"]
)

@agent.on_event("startup")
async def init(ctx: Context):
    ctx.logger.info("Orchestrator up and running")

@on_rest_post(path="/create_discord")
async def handle_create(req: CreateServerRequest, ctx: Context):
    # enqueue a job message to the worker
    await enqueue_create_job(req.name, ctx)
    return {"status": "queued", "server": req.name}

if __name__ == "__main__":
    agent.run()
