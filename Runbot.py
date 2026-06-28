import discord

TOKEN = "MTUxOTM2NjQ5Njc4OTMzMTk4OA.G2hK9z.p0wGLFQj0J9qYUUkKmchS8UnGLK7-fRYHAHlSc"

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ {client.user} Online")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == "!ping":
        await message.channel.send("🏓 Pong!")

client.run(TOKEN)