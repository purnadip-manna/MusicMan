import discord
import os
import keep_alive

keep_alive.keep_alive()

client = discord.Client()

@client.event
async def on_ready():
    print('Logged on as', client.user)

@client.event
async def on_message(message):
    if message.author != client.user:
        print(message.content)
        msg = message.content.lower()
        msg = msg.strip()

        if "hi" in msg or "hello" in msg:
          await message.channel.send("Hello!")

client.run(os.getenv('TOKEN'))