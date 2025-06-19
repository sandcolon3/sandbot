import discord
from discord.ext import commands, tasks
import random
import tweepy
import os
from collections import deque
import time
import asyncio
import markovify
import re
from dotenv import load_dotenv

######### SETUPS AND SHIET ###########
######################################

load_dotenv()

## DISCORD STUFF

description = "my creature. my child. go my child...."

# discord intents (idk what that is)
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# both of these are useless now i think
allowed_servers = [1298988489072709712, 1047320338205249626]
my_server_id = 1298988489072709712

bot = commands.Bot(command_prefix='!', description=description, intents=intents)

## TWITTER STUFF

client = tweepy.Client(
    consumer_key=os.getenv('consumer_key'), consumer_secret=os.getenv('consumer_secret'),
    access_token=os.getenv('access_token'), access_token_secret=os.getenv('access_token_secret')
)

## COMMANDS RELATED STUFF

q = deque()
triggers_responses = []
queue_file = 'tweet_queue.txt'
tg_file = 'triggers_responses.txt'
ez_messages = ['I have really enjoyed playing with you!', 'I had something to say, then I forgot it.', "Why can't the Ender Dragon read a book? Because he always starts at the End.", 'Your clicks per second are godly. :o', 'Behold, the great and powerful, my magnificent and almighty nemesis!', 'In my free time I like to watch cat videos on youtube', 'Your personality shines brighter than the sun.', 'I have really enjoyed playing with you! <3', "Pineapple doesn't go on pizza!", 'If the world in Minecraft is infinite....how can the sun revolve around it?', 'Can you paint with all the colors of the wind', 'Doing a bamboozle fren.', 'Maybe we can have a rematch?', 'ILY<3', "Hello everyone! I'm an innocent player who loves everything Hypixel", 'I like minecraft pvp, but you are better than me!', 'If the Minecraft World is infinite, how does the sun spin around it?', 'Sometimes I try to say bad things, and then this happens.', 'I enjoy long walks on the beach and playing Hypixel', 'Welcome to the Hypixel zoo!', "Let's be friends instead of fighting okay?", 'I need help, teach me how to play!', 'I like to eat pasta, do you prefer nachos?', "You're a great person! Do you want to play some Hypixel games with me?", 'Your personality shines brighter than the sun.', 'Pls give me doggo memes!', 'Sometimes I sing soppy, love songs in the car', 'When I saw the guy with a potion I knew there was trouble brewing.', 'Hey Helper, how play game?', "Wait... this isn't what I typed!", 'I like pineapple on my pizza', 'When nothing is going right, go left.', 'What happens if I add chocolate milk to macaroni and cheese?', 'Anybody else really like Rick Astley?', 'I enjoy long walks on the beach and playing Hypixel', 'I had something to say, then I forgot it.', 'Please go easy on me, this is my first game!', 'You are very good at this game friend!', 'I heard you like minecraft, so I built a computer so you can minecraft, while minecrafting in your minecraft.', 'Blue is greener than purple for sure']

# the tweet list for the markov model
with open("tweets_definitivo.txt", encoding="utf-8") as tweet_file:
    text = tweet_file.read()

# Build the markov model.
text_model = markovify.Text(text, state_size=1)

# the tweet list for the random lines
with open('revelations.txt', 'r') as file:
    randomlines = file.readlines()

# loads the queue from the text file
def load_queue():
    """Load the queue from a text file."""
    if os.path.exists(queue_file):
        with open(queue_file, 'r') as f:
            for line in f:
                tweet_content, author_id = line.strip().split('|')  # Split line into tweet and author ID
                q.append((tweet_content, author_id))

# saves the tweet queue into the text file
def save_queue():
    """Save the queue to a text file."""
    with open(queue_file, 'w') as f:
        for item in q:
            f.write(f"{item[0]}|{item[1]}\n")  # Write tweet and author ID separated by '|'

# saves the text triggers file
def save_triggers():
    with open(tg_file, 'w') as f:
        for trigger, response in triggers_responses:
            f.write(f"{trigger}|{response}\n")

# loads the text triggers file
def load_triggers():
    if os.path.exists(tg_file):
        with open(tg_file, 'r') as f:
            for line in f:
                trigger, response = line.strip().split('|')
                triggers_responses.append((trigger, response))

## BOT EVENTS

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='!shelp'))
    load_queue()
    load_triggers()

#@bot.event
#async def on_guild_join(guild):
#    if guild.id not in allowed_servers:
#        try:
#            await guild.leave()
#            print(f'leaving this bitch {guild.id}')
#        except Exception as e:
#            print(f'error leaving guild {guild.id}: {e}')

######### COMMANDS ###########
##############################

@bot.command()
async def test(ctx):
    await ctx.send("fuck you")

# TODO: make all of this useless and just build it all into !help
@bot.command()
async def shelp(ctx):
    await ctx.send("list of commands:\n!test - tests if the bot works\n!tweet - tweets something on the sandbot account\n!tweetpic - tweets a picture\n!queue - shows the tweet queue if the api limit has been hit\n!markov - generates a sand tweet mashing strings together (no ai)\n\nif ur an admin do !sadminhelp")

## SINCLAIR IF UR READING THIS i know this is the dumbest idea ever i just idk 
@bot.command()
async def sadminhelp(ctx):
    await ctx.send("please input the passwordsd // will come up with a better system later")

    def check2(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    try:
        # Wait for a response from the user
        response_message2 = await bot.wait_for('message', check=check2, timeout=30)  # 30 seconds timeout
        response_text2 = response_message2.content
        if response_text2 == "randyfromthe222":
            await ctx.send("list of commands:\n!startqueue - starts the tweet queue\n!delqueue - clears the queue\n!addtg - adds a chat trigger and its response\n!tglist - shows the list of triggers and its responses")

    except asyncio.TimeoutError:
        await ctx.send("you took too long to send the password. you don't know it lol")

@bot.command()
async def tweet(ctx, *, tweet_content):
    author_id = ctx.author.id
    try:
        response = client.create_tweet(text=tweet_content)
    except tweepy.errors.TooManyRequests:
        await ctx.send("twitter rate limited you. you've been added to the queue")
        q.append((tweet_content, author_id))
        save_queue()
    except Exception as e:
        await ctx.send("twitter sent a weird exception. not adding you to the queue tag sand")
    else:
        await ctx.send(f"https://fxtwitter.com/user/status/{response.data['id']}")

# TODO: fix this lol
@bot.command()
async def tweetpic(ctx):
    await ctx.send("this commad has been seized")
#    if ctx.message.attachments:
#        attachment = ctx.message.attachments[0]
#        
#        file_path = f"./{attachment.filename}"
#        await attachment.save(file_path)
#
#        media = client.create_tweet(text="", media_ids=[file_path])
#        
#        await ctx.send(f"https://twitter.com/user/status/{media.data['id']}")
#
#        os.remove(file_path)
#    else:
#        await ctx.send("please attach media. dummy")

@bot.command()
async def queue(ctx):
    if not q:
        await ctx.send("the queue is empty just liek my heart")
        return
    queue_contents = []
    for item in q:
        tweet = item[0]
        author_id = item[1]  # author's discord id
        user = await bot.fetch_user(author_id) # author's user
        queue_contents.append(f"{tweet} | author: {user.name}") # gets the username from the user so it can tell you who it is and not the id

    await ctx.send("\n".join(queue_contents))

# TODO: it's very stupid to just have it all be in one channel in dds server like do something idk
@tasks.loop(minutes=15)  # runs this task every 15 minutes
async def tweet_queue():
    channel_commands = bot.get_channel(1367985244489388153)  # ############# REPLACE WITH THE CHANNEL ID WHERE YOU WANT YOUR "TWEET IS READY NOTIFICATIONS TO BE SHOWN"
    while len(q) > 0:
        tweet_content, author_id = q.popleft()
        try:
            response = client.create_tweet(text=tweet_content)
        except tweepy.errors.TooManyRequests:
            print("twitter rate limited you. readding to the queue")
            save_queue()
            q.append((tweet_content, author_id))  # readd to the queue if rate limited
            break
        except Exception as e:
            await channel_commands.send("<@1016738092100632647> twitter sent a weird exception you might wanna check that")
            break
        else:
            await channel_commands.send(f"<@{author_id}> your tweet is ready:\nhttps://fxtwitter.com/user/status/{response.data['id']}")
            await asyncio.sleep(30)

# starts the looping task. YOU HAVE TO USE THIS OR ELSE THE QUEUE WON'T DO ANYTHING. yes on every restart
@bot.command()
async def startqueue(ctx):
    tweet_queue.start()
    await ctx.send("tweet queue started")

@bot.command()
async def stopqueue(ctx):
    tweet_queue.stop()
    await ctx.send("tweet queue stopped")

@bot.command()
async def markov(ctx):
    await ctx.send(text_model.make_short_sentence(280))

@bot.command()
@commands.has_role(1307399056904945684)  ############# REPLACE WITH THE ROLE OF THE USERS THAT YOU WANT TO BE ABLE TO DELETE THE QUEUE
async def delqueue(ctx):
    q.clear()
    save_queue()
    await ctx.send("queue has been cleared high one")

@bot.command()
async def testrandom(ctx):
    random_line = random.choice(randomlines)
    formatted_line = random_line.replace('\\n', '\n')  # this replaces \n, which it takes as a literal, to an actual salto de linea
    await ctx.send(formatted_line)

## TEXT TRIGGERS!!!!!!
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if random.random() < 0.005:
        random_line = random.choice(randomlines)
        formatted_line = random_line.replace('\\n', '\n')   # this replaces \n, which it takes as a literal, to an actual salto de linea
        await message.channel.send(formatted_line)
    
    ## bite command
    #if re.search('bite', message.content.lower()):
    #    try:
    #        with open('bite.txt', 'r') as file:
    #            bite_counter = int(file.read().strip())
    #    except FileNotFoundError:
    #        bite_counter = 87  # if the file doesn't exist, start with 0
    #    except ValueError:
    #        bite_counter = 87  # if the file is not a valid integer

    #    bite_counter += 1

    #    with open('bite.txt', 'w') as file:
    #        file.write(str(bite_counter))

    #    await message.channel.send(f'WAS THAT THE BITE OF {bite_counter}????')


    if re.search(r'\bez\b', message.content.lower()):
        if message.author.id != 807778576152789002:
            await message.channel.send(random.choice(ez_messages))

    for trigger, response in triggers_responses:
        if trigger in message.content.lower():
            await message.channel.send(response)
            break
    
    await bot.process_commands(message)

@bot.command()
@commands.has_role(1307399056904945684)
async def addtg(ctx, trigger_text):
    
    await ctx.send(f"please provide a response for the trigger '{trigger_text}':")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        # wait for user to give you the response
        response_message = await bot.wait_for('message', check=check, timeout=30)  # 30 seconds timeout
        response_text = response_message.content

        # add the trigger and response to the list
        triggers_responses.append((trigger_text, response_text))
        save_triggers()
        await ctx.send("ok done. !tglist to show")

    except asyncio.TimeoutError:
        await ctx.send("you took too long to respond the inspiration is not gonna come just give up. burn all those books you started writing this is clearly not your thing")


@bot.command()
async def tglist(ctx):
    await ctx.send(triggers_responses)

bot.run(os.getenv('TOKEN'))