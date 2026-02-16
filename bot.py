import os
import discord
import random
from dotenv import load_dotenv


load_dotenv()

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
ADAM_USER_ID = int(os.environ["ADAM_USER_ID"])
STREAM_WATCHER_ID = int(os.environ["STREAM_WATCHER_ID"])
GENERAL_CHANNEL_ID = int(os.environ["GENERAL_CHANNEL_ID"])
MESSAGES_FILE = os.environ.get("MESSAGES_FILE", "messages.txt")

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True

client = discord.Client(intents=intents)
adam_queue: list[str] = []



def load_messages(filepath: str = MESSAGES_FILE) -> list[str]:
    with open(filepath, "r") as f:
        return [line.strip() for line in f if line.strip()]

def get_next_message(queue: list[str], filepath: str, **kwargs) -> str:
    if not queue:
        queue.extend(load_messages(filepath))
        random.shuffle(queue)
    return queue.pop().format(**kwargs)
    


@client.event
async def on_ready():
    print(f"Bot is online as {client.user}")

@client.event
async def on_voice_state_update(
    member: discord.Member,
    before: discord.VoiceState,
    after: discord.VoiceState
):
    
    general = client.get_channel(GENERAL_CHANNEL_ID)
    if general is None:
        return
    
    if member.id == ADAM_USER_ID:
        if before.channel is not None and after.channel is None:
            msg = get_next_message(
                adam_queue, MESSAGES_FILE,
                name=member.display_name,
                channel=before.channel.name,
            )
            await general.send(msg)
    
    if member.id == STREAM_WATCHER_ID:
        if after.channel is not None and (before.channel is None or before.channel != after.channel):
            streamers = [
                m for m in after.channel.members
                if m.voice and m.voice.self_stream and m.id != member.id
            ]
            if streamers:
                streamer_names = ", ".join(m.display_name for m in streamers)
                await general.send(
                    f"{streamer_names} is streaming and <@{STREAM_WATCHER_ID}> joined. "
                    f"Watch out for the Peeping Tom!"
                )
client.run(DISCORD_TOKEN)