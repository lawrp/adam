import os
import discord
import random
from dotenv import load_dotenv


load_dotenv()

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
ADAM_USER_ID = int(os.environ["ADAM_USER_ID"])
GENERAL_CHANNEL_ID = int(os.environ["GENERAL_CHANNEL_ID"])
MESSAGES_FILE = os.environ.get("MESSAGES_FILE", "messages.txt")

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True

client = discord.Client(intents=intents)
message_queue: list[str] = []



def load_messages() -> list[str]:
    with open(MESSAGES_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def get_next_message(name: str, channel: str) -> str:
    global message_queue
    if not message_queue:
        message_queue = load_messages()
        random.shuffle(message_queue)
    return message_queue.pop().format(name=name, channel=channel)
    


@client.event
async def on_ready():
    print(f"Bot is online as {client.user}")

@client.event
async def on_voice_state_update(
    member: discord.member,
    before: discord.VoiceState,
    after: discord.VoiceState
):
    if member.id != ADAM_USER_ID:
        return
    
    if before.channel is not None and after.channel is None:
        channel = client.get_channel(GENERAL_CHANNEL_ID)
        if channel is None:
            return
        
        messages = load_messages()
        if not messages:
            print("couldn't load message file.")
            return
        
        msg = get_next_message(member.display_name, before.channel.name)
        
        await channel.send(msg)

client.run(DISCORD_TOKEN)