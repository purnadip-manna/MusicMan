import discord
import os
import keep_alive

keep_alive.keep_alive()

client = discord.Client()

help_msg = """
Help:
*Every Command should start with . (full stop)*
1. Join a Voice Channel:
`.join <voice_channel_name>` or `.j <voice_channel_name>`
<voice_channel_name> = general (Default) [if blank]
2. Leave a Voice Channel:
`.leave` or `.l`
3. Play a song from youtube:
`.play https://www.youtube.com/watch?url_sample_id` or `.p https://www.youtube.com/watch?url_sample_id`
4. Pause the song:
`.pause` or `.pp`
5. Resume the song:
`.resume` or `.r`
6. Stop the song:
`.stop` or `.s`
7. Set a timer:
`.timer <time_in_min>` or `.t <time_in_min>`
*e.g- .timer 2* 
(timer is set for 2min)
"""

@client.event
async def on_ready():
    print('Logged on as', client.user)

@client.event
async def on_message(message):
    if message.author != client.user:
        print(message.content)
        msg = message.content.lower()
        msg = msg.strip()

        # help ------------------
        if msg == ".help" or msg == ".h":
            await message.channel.send(help_msg)

        elif msg.startswith(".join") or msg.startswith(".j"):
            await message.channel.send("Join")

        elif msg == ".pause" or msg == ".pp":
            return await message.channel.send("Pause")

        elif msg.startswith(".play") or msg.startswith(".p"):
            await message.channel.send("Play")

        elif msg == ".resume" or msg == ".r":
            await message.channel.send("Resume")

        elif msg == ".stop" or msg == ".s":
            await message.channel.send("Stop")

        elif msg == ".leave" or msg == ".l":
            await message.channel.send("Leave")

        elif msg.startswith(".timer") or msg.startswith(".t"):
            await message.channel.send("Timer")
        

client.run(os.getenv('TOKEN'))
