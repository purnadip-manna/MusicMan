import discord
import os
import asyncio
from threading import Timer
import keep_alive
import youtube_dl
from helpM import help_msg
from replit import db

keep_alive.keep_alive()
client = discord.Client()

stopFlag = 0
playlist = ""
msg_channel = ""
ytPlaying = False
class Queue:
    def __init__(self, arr):
        self.playlist = arr
        self.prevList = []

    def enqueue(self, value):
        self.playlist.append(value)

    def dequeue(self):
        if len(self.playlist) != 0:
            ele = self.playlist.pop(0)
            self.prevList.append(ele)
            return ele

        else: return 'end'

    def previous(self):
        if len(self.prevList) != 0:
            self.playlist.insert(0, self.prevList.pop())
            if len(self.prevList) != 0:
                return self.prevList[len(self.prevList)-1]
            else: return 'end'

        else: return 'end'


YTDL_OPTIONS_AUDIO = {
    'format': 'bestaudio/best', 'extractaudio': True, 'audioformat': 'mp3', 'outtmpl': './ytmusic/song.%(ext)s', 'restrictfilenames': True, 'noplaylist': True, 'nocheckcertificate': True, 'ignoreerrors': False, 'logtostderr': False, 'quiet': True, 'no_warnings': True, 'default_search': 'auto', 'source_address': '0.0.0.0'}

def download_audio(linkOfVideo):
    with youtube_dl.YoutubeDL(YTDL_OPTIONS_AUDIO) as ydl:
        ydl.download([linkOfVideo])

def setPlaylist(name):
    global playlist
    if name == "youtube":
        playlist = Queue([])

    else:
        play_ls = list(db['my_playlist']).copy()
        playlist = Queue(play_ls)

def checkSource(name):
    if "youtube" in name or "youtu.be" in name:
        if "list" in name or "playlist" in name:
            return 'no'
        else:
            return 'youtube'

    elif "youtube" not in name and "youtu.be" not in name:
        return 'playlist'


def clearYTfolder():
    try:
        song_ls = os.listdir("./ytmusic/")
        name = song_ls[0]
        if (os.path.isfile('./ytmusic/' + name) == True):
            os.remove('./ytmusic/' + name)
            print("Removing...", name)
    except Exception as e:
        print(e)

#function for sending any message to the channel
def msg_sender(msg):
    global stopFlag
    if stopFlag == 0:
        coro = msg_channel.send(msg)
        fut = asyncio.run_coroutine_threadsafe(coro, client.loop)
        try:
            fut.result()
        except:
            # an error happened sending the message
            pass
    else:
        return

#This function is storing the channel object reference
def storeChannel(var):
    global msg_channel
    msg_channel = var


def timesUp():
    msg_sender("Time's up!")

@client.event
async def on_ready():
    print('Logged on as', client.user)

@client.event
async def on_message(message):
    global stopFlag
    global playlist
    global ytPlaying

    # storing the Channel Id:
    storeChannel(message.channel)
    msg = message.content.lower()
    msg = msg.strip()

    # next song --------------------
    if msg == ".next" or msg == ".n":
        await message.channel.purge(limit=1)
        try:
            voice_client: discord.VoiceClient = discord.utils.get(client.voice_clients, guild=message.guild)
            name = playlist.dequeue()
            print("Dequeued:", name)
            clearYTfolder()
            if voice_client.is_playing():
                voice_client.pause()
                print("Pause...")

            if ytPlaying:
                if name != 'end':
                    download_audio(name)
                    song_ls = os.listdir("./ytmusic/")
                    name = song_ls[0]
                    voice_client.play(discord.FFmpegPCMAudio('./ytmusic/' + name, executable='ffmpeg'),after=lambda e: msg_sender(".next"))

                else:
                    ytPlaying = False
                    del playlist
                    await message.channel.send("Playlist Ended!")

            else:
                if name != 'end':
                    print("Downloading...", name)
                    download_audio(name)
                    song_ls = os.listdir("./ytmusic/")
                    name = song_ls[0]
                    voice_client.play(discord.FFmpegPCMAudio('./ytmusic/' + name, executable='ffmpeg'), after=lambda e: msg_sender(".next"))

                else:
                    del playlist
                    await message.channel.send("Playlist Ended!")

        except:
            await message.channel.send("Playlist is not initialized!")

    elif message.content == "Time's up!" and message.author == client.user:
        voice_client = discord.utils.get(client.voice_clients, guild=message.guild)
        voice_client.pause()

    if message.author != client.user:
        print(message.content)

        # help ------------------
        if msg == ".help" or msg == ".h":
            await message.channel.send(help_msg)

        
        # Join ------------------
        elif msg.startswith(".join") or msg.startswith(".j"):
            try:
               msg, voice_channel_name = map(str, message.content.split(" "))

            except:
                if(len(message.guild.voice_channels)):
                    voice_channel_name = message.guild.voice_channels[0].name

                else:
                    return await message.channel.send("There is no Voice Channel")

            voiceChannel = discord.utils.get(message.guild.voice_channels, name=voice_channel_name)

            voice = discord.utils.get(client.voice_clients, guild=message.guild)
            if (voice):
                if voice.is_connected():
                    await voice.disconnect()
            if(voiceChannel):
                await voiceChannel.connect()
                await message.channel.send("Joined to " + voice_channel_name)

            else:
                return await message.channel.send("Incorrect Voice Channel")            

        
        # Pause ------------------
        elif msg == ".pause" or msg == ".pp":
            voice_client = discord.utils.get(client.voice_clients,guild=message.guild)
            if voice_client.is_playing():
                voice_client.pause()
            else:
                await message.channel.send("Currently no audio is playing.")


        # Previous Song ------------------
        elif msg == ".prev" or msg == ".pr":
            if ytPlaying:
                await message.channel.send("Previous not available in Youtube Music")
            else:
                voice_client: discord.VoiceClient = discord.utils.get(client.voice_clients, guild=message.guild)
                if voice_client.is_playing():
                    voice_client.pause()
                name = playlist.previous()
                clearYTfolder()
                if name == "end":
                    name = playlist.dequeue()
                    download_audio(name)
                    song_ls = os.listdir("./ytmusic/")
                    name = song_ls[0]
                else:
                    download_audio(name)
                    song_ls = os.listdir("./ytmusic/")
                    name = song_ls[0]

                voice_client.play(discord.FFmpegPCMAudio("./ytmusic/" + name, executable='ffmpeg'), after=lambda e: msg_sender(".next"))

            return


        # Play ------------------
        elif msg.startswith(".play") or msg.startswith(".p"):
            stopFlag = 0
            voice_client: discord.VoiceClient = discord.utils.get(client.voice_clients, guild=message.guild)
            if voice_client.is_playing():
                await voice_client.pause()

            ins_list = list(map(str, message.content.split(" ")))
            if(len(ins_list) > 1):
                if checkSource(ins_list[1]) == 'youtube':
                    linkOfVideo = ins_list[1].strip()
                    if ytPlaying == False:
                        setPlaylist('youtube')
                        clearYTfolder()
                        try:
                            download_audio(linkOfVideo)
                            song_ls = os.listdir("./ytmusic/")
                            name = song_ls[0]
                            voice_client.play(discord.FFmpegPCMAudio('./ytmusic/' + name, executable='ffmpeg'),after=lambda e: msg_sender(".next"))
                            ytPlaying = True
                            await message.channel.purge(limit=1)
                            
                        except:
                            await message.channel.send("Error with the link")

                    else:
                        playlist.enqueue(linkOfVideo)
                        await message.channel.purge(limit=1)
                        await message.channel.send("Added to queue")

                else:
                    # code for my playlist
                    setPlaylist('myplaylist')
                    clearYTfolder()
                    name = playlist.dequeue()
                    if name != "end":
                        try:
                            download_audio(name)
                            song_ls = os.listdir("./ytmusic/")
                            name = song_ls[0]
                            voice_client.play(discord.FFmpegPCMAudio('./ytmusic/' + name, executable='ffmpeg'),after=lambda e: msg_sender(".next"))
                            await message.channel.purge(limit=1)
                            
                        except:
                            await message.channel.send("Error with the link")
                    else:
                        await message.channel.send("Empty Playlist")

                
            else:
                await message.channel.send("Error in command")


        # Resume ------------------
        elif msg == ".resume" or msg == ".r":
            voice_client = discord.utils.get(client.voice_clients,guild=message.guild)
            if voice_client.is_paused():
                voice_client.resume()
            else:
                await message.channel.send("The audio is not paused.")

        
        # Stop ------------------
        elif msg == ".stop" or msg == ".s":
            stopFlag = 1
            ytPlaying = False
            try:
                del playlist
            except:
                pass
            stopFlag = 1
            clearYTfolder()
            voice_client = discord.utils.get(client.voice_clients, guild=message.guild)
            voice_client.pause()
            voice_client.stop()

        
        # leave -------------
        elif msg == ".leave" or msg == ".l":
            stopFlag = 1
            voice = discord.utils.get(client.voice_clients, guild=message.guild)
            if voice.is_connected():
                await voice.disconnect()
            else:
                await message.channel.send("I am not connected to a Voice channel.")


        # Timer ------------------
        elif msg.startswith(".timer"):
            ctx, t = map(str, msg.split(".timer"))
            timer_time = float(t.strip()) * 60
            timerObj = Timer(timer_time, timesUp)
            timerObj.start()
            await message.channel.send("Alright, :timer: " + t + "mins.. Starting... now.")
            

client.run(os.environ['TOKEN'])