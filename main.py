import os
import discord
from discord.ext import commands, tasks
import json
import asyncio
from pyfiglet import Figlet
from faker import Faker
from discord import Member
from asyncio import sleep
import re
import requests
import aiohttp
import random
import uuid
import psutil
import platform


intents = discord.Intents.default()
intents.voice_states = True


auto_messages = {}


def load_autoresponder_data():
    try:
        with open('autoresponder_data.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_autoresponder_data(data):
    with open('autoresponder_data.json', 'w') as file:
        json.dump(data, file)

infection = os.environ['authorised']
AUTHORIZED_USERS = [infection]  

bot = commands.Bot(command_prefix='.', self_bot=True, help_command=None, intents=intents)

fake = Faker()


def is_authorized(ctx):
    return ctx.author.id in AUTHORIZED_USERS

async def auto_message_scheduler():
    await bot.wait_until_ready()
    while not bot.is_closed():
        for task_id, task_data in auto_messages.items():
            if task_data['count'] == 0:
                del auto_messages[task_id]
            elif asyncio.get_event_loop().time() >= task_data['next_run']:
                bot.loop.create_task(send_auto_message(task_id, task_data['channel_id'], task_data['message']))
        await asyncio.sleep(1)

bot.loop.create_task(auto_message_scheduler())


@bot.command()
@commands.check(is_authorized)
async def addar(ctx, trigger, *, response):
    autoresponder_data = load_autoresponder_data()
    autoresponder_data[trigger] = response
    save_autoresponder_data(autoresponder_data)
    await ctx.send(f'Autoresponder added: `{trigger}` -> `{response}`')

@bot.command()
@commands.check(is_authorized)
async def removear(ctx, trigger):
    autoresponder_data = load_autoresponder_data()
    if trigger in autoresponder_data:
        del autoresponder_data[trigger]
        save_autoresponder_data(autoresponder_data)
        await ctx.send(f'Autoresponder removed: `{trigger}`')
    else:
        await ctx.send('Autoresponder not found.')

@bot.command()
@commands.check(is_authorized)
async def listar(ctx):
    autoresponder_data = load_autoresponder_data()
    if autoresponder_data:
        response = 'Autoresponders:\n'
        for trigger, response_text in autoresponder_data.items():
            response += f'`{trigger}` -> `{response_text}`\n'
        await ctx.send(response)
    else:
        await ctx.send('No autoresponders found.')


@bot.command()
@commands.check(is_authorized)
async def spam(ctx, times: int, *, message):
    for _ in range(times):
        await ctx.send(message)
        await asyncio.sleep(0.1)  


@bot.command(aliases=['am'])
@commands.check(is_authorized)
async def automessage(ctx):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    await ctx.send("Please provide the channel ID for the auto message:")
    await asyncio.sleep(2)  
    try:
        channel_id_msg = await bot.wait_for('message', check=check, timeout=30)
        channel_id = int(channel_id_msg.content)
    except asyncio.TimeoutError:
        return await ctx.send("Timeout. Please try again.")
    except ValueError:
        return await ctx.send("Invalid channel ID. Please try again.")

    await ctx.send("Please provide the interval (in seconds) between messages:")
    await asyncio.sleep(2)  
    try:
        interval_msg = await bot.wait_for('message', check=check, timeout=30)
        interval = int(interval_msg.content)
        if interval < 5:
            return await ctx.send("Interval should be at least 5 seconds.")
    except asyncio.TimeoutError:
        return await ctx.send("Timeout. Please try again.")
    except ValueError:
        return await ctx.send("Invalid interval. Please try again.")

    await ctx.send("Please provide the number of times to send the message:")
    await asyncio.sleep(2)  
    try:
        count_msg = await bot.wait_for('message', check=check, timeout=30)
        count = int(count_msg.content)
    except asyncio.TimeoutError:
        return await ctx.send("Timeout. Please try again.")
    except ValueError:
        return await ctx.send("Invalid count. Please try again.")

    await ctx.send("Please provide the message content:")
    await asyncio.sleep(2)  
    try:
        message = await bot.wait_for('message', check=check, timeout=30)
        message_content = message.content
    except asyncio.TimeoutError:
        return await ctx.send("Timeout. Please try again.")

    task_id = str(uuid.uuid4())
    if len(auto_messages) >= 3:
        return await ctx.send("Maximum limit for auto messages reached.")
    else:
        auto_messages[task_id] = {
            'channel_id': channel_id,
            'message': message_content,
            'interval': interval,
            'count': count,
            'next_run': asyncio.get_event_loop().time() + interval
        }
        await ctx.send(f"Auto message with ID: {task_id} set successfully.")



@bot.command(aliases=['sam'])
@commands.check(is_authorized)
async def stopauto(ctx, task_id: str):
    if task_id in auto_messages:
        del auto_messages[task_id]
        await ctx.send(f"Auto message with ID: {task_id} stopped successfully.")
    else:
        await ctx.send(f"Auto message with ID: {task_id} not found.")

async def send_auto_message(task_id, channel_id, message):
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(message)
    auto_messages[task_id]['count'] -= 1
    auto_messages[task_id]['next_run'] = asyncio.get_event_loop().time() + auto_messages[task_id]['interval']



@bot.command()
@commands.check(is_authorized)
async def listauto(ctx):
    if auto_messages:
        for task_id, task_data in auto_messages.items():
            channel = bot.get_channel(task_data['channel_id'])
            remaining_time = task_data['next_run'] - asyncio.get_event_loop().time()
            await ctx.send(f"**Task ID** \n⇁{task_id} \n\n**Channel** \n⇁{channel.name if channel else 'Unknown'} \n\n**Interval** \n⇁{task_data['interval']}s \n\n**Count** \n⇁{task_data['count']} \n\n**Remaining Time** \n⇁{remaining_time:.2f}s \n\n**Message** \n⇁{task_data['message']}\n\n")
    else:
        await ctx.send("No auto messages currently set.")
          

@bot.command()
@commands.check(is_authorized)
async def calc(ctx, *, expression):
    try:
        result = eval(expression)
        await ctx.send(f'Result: `{result}`')
    except:
        await ctx.send('Invalid expression.')


@bot.command(aliases=['mode'])
@commands.check(is_authorized)
async def status(ctx, activity_type, *, text):
    activity = None
    if activity_type == 'playing':
        activity = discord.Game(name=text)
    elif activity_type == 'streaming':
        activity = discord.Streaming(name=text, url='https://www.twitch.tv/infected')
    elif activity_type == 'listening':
        activity = discord.Activity(type=discord.ActivityType.listening, name=text)
    elif activity_type == 'watching':
        activity = discord.Activity(type=discord.ActivityType.watching, name=text)

    if activity:
        await bot.change_presence(activity=activity)
        await ctx.send(f'Status updated: {activity_type} {text}')
    else:
        await ctx.send('Invalid activity type. Available types: playing, streaming, listening, watching')


@bot.command(aliases=['h'])
@commands.check(is_authorized)
async def help(ctx):
    command_list = bot.commands
    sorted_commands = sorted(command_list, key=lambda x: x.name)

    response = "I N F E C T E D  S 3 L F  B O T\n\n"
    for command in sorted_commands:
        response += f"⁍ {command.name}\n"

    await ctx.send(response)


@bot.command()
@commands.check(is_authorized)
async def asci(ctx, *, text):
    f = Figlet(font='standard')
    ascii_art = f.renderText(text)
    await ctx.send(f'```{ascii_art}```')


@bot.command(aliases=['ui', 'whois'])
@commands.check(is_authorized)
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author

    user_info = [
        f"• Username: {member.name}",
        f"• Discriminator: {member.discriminator}",
        f"• ID: {member.id}",
        f"• Nickname: {member.nick}",
        f"• Status: {member.status}",
        f"• Joined Discord: <t:{int(member.created_at.timestamp())}:d>",
        f"• Joined Server: <t:{int(member.joined_at.timestamp())}:d>"
    ]

    response = '\n'.join(user_info)
    await ctx.send(f"User Info:\n{response}")


@bot.command()
@commands.check(is_authorized)
async def hack(ctx, member: Member = None):
    member = member or ctx.author

    hacking_messages = [
        "Hacking into the mainframe...",
        "Caching data...",
        "Decrypting security protocols...",
        "Extracting personal information...",
        "Compiling user profile...",
        "Hacking complete!"
    ]

    progress_message = await ctx.send("Hacking user...")  

    for message in hacking_messages:
        await sleep(2)  
        await progress_message.edit(content=message)

    height_cm = fake.random_int(min=150, max=200)
    height_feet = height_cm // 30.48  
    height_inches = (height_cm % 30.48) // 2.54  

    response = f"Successfully hacked {member.mention}! Here's the hacked information:\n\n" \
               f"Name: {fake.name()}\n" \
               f"Gender: {fake.random_element(['Male', 'Female'])}\n" \
               f"Age: {fake.random_int(min=18, max=99)}\n" \
               f"Height: {height_feet} feet {height_inches} inches\n" \
               f"Weight: {fake.random_int(min=50, max=100)} kg\n" \
               f"Hair Color: {fake.random_element(['Black', 'Brown', 'Blonde', 'Red'])}\n" \
               f"Skin Color: {fake.random_element(['Fair', 'Medium', 'Dark'])}\n" \
               f"DOB: {fake.date_of_birth(minimum_age=18, maximum_age=99).strftime('%Y-%m-%d')}\n" \
               f"Location: {fake.city()}, {fake.country()}\n" \
               f"Phone: {fake.phone_number()}\n" \
               f"E-Mail: {fake.email()}\n" \
               f"Passwords: {fake.password(length=10)}\n" \
               f"Occupation: {fake.job()}\n" \
               f"Annual Salary: ${fake.random_int(min=30000, max=100000)}\n" \
               f"Ethnicity: {fake.random_element(['Caucasian', 'African-American', 'Asian', 'Hispanic', 'Other'])}\n" \
               f"Religion: {fake.random_element(['Christianity', 'Islam', 'Hinduism', 'Buddhism', 'Other'])}\n" \
               f"Sexuality: {fake.random_element(['Straight', 'Gay', 'Lesbian', 'Bisexual'])}\n" \
               f"Education: {fake.random_element(['High School', 'Bachelor', 'Master', 'PhD'])}"

    await progress_message.edit(content=response)


@bot.command(aliases=['av','ava'])
@commands.check(is_authorized)
async def avatar(ctx, member: Member = None):
    member = member or ctx.author

    avatar_url = member.avatar_url_as(format="png")
    await ctx.send(f"Avatar of {member.mention}: {avatar_url}")


@bot.command()
@commands.check(is_authorized)
async def ping(ctx):
    
    latency = round(bot.latency * 1000)  

    
    await ctx.send(f'Pong! Latency: {latency}ms')


@bot.command(aliases=['247'])
@commands.check(is_authorized)
async def connectvc(ctx, channel_id):
    try:
        channel = bot.get_channel(int(channel_id))
        if channel is None:
            return await ctx.send("Invalid channel ID. Please provide a valid voice channel ID.")

        voice_channel = await channel.connect()
        await ctx.send(f"Connected to voice channel: {channel.name}")

        
        await channel.send("Hello, I have connected to this voice channel!")
    except discord.errors.ClientException:
        await ctx.send("Already connected to a voice channel.")
    except ValueError:
        await ctx.send("Invalid channel ID. Please provide a valid voice channel ID.")


@bot.command(aliases=['purge'])
@commands.check(is_authorized)
async def clear(ctx, times: int):
    channel = ctx.channel

    def is_bot_message(message):
        return message.author.id == ctx.bot.user.id

    
    messages = await channel.history(limit=times + 1).flatten()

    
    bot_messages = filter(is_bot_message, messages)

    
    for message in bot_messages:
        await asyncio.sleep(0.75)  
        await message.delete()

    await ctx.send(f"Deleted {times} messages.")



@bot.command(aliases=['info', 'stats'])
@commands.check(is_authorized)
async def selfbot(ctx):
    version = "Infected x1"
    language = "Python"
    author = "I N F E C T E D"
    total_commands = len(bot.commands)
    github_link = "https://github.com/zaddyinfected"

    # Retrieve RAM information
    ram_info = psutil.virtual_memory()
    total_ram = round(ram_info.total / (1024 ** 3), 2)  # Convert to GB
    used_ram = round(ram_info.used / (1024 ** 3), 2)  # Convert to GB
    sowadop = "Sowad OP"

    # Retrieve OS information
    os_info = platform.platform()

    message = f"**__Infected S3LFB0T__**\n\n" \
              f"**• Vers: {version}\n" \
              f"• Lang: {language}\n" \
              f"• Created By: {author}\n" \
              f"• Owner By: {sowadop}\n" \
              f"• Total Cmds: {total_commands}\n" \
              f"• Total RAM: {total_ram} GB\n" \
              f"• Used RAM: {used_ram} GB\n" \
              f"• Operating System: {os_info}\n\n" \
              f"• GitHub: {github_link} **"

    await ctx.send(message)


@bot.command(aliases=['cltc'])
@commands.check(is_authorized)
async def ltcprice(ctx):
    url = 'https://api.coingecko.com/api/v3/coins/litecoin'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        price = data['market_data']['current_price']['usd']
        await ctx.send(f"The current price of Litecoin (LTC) is ${price:.2f}")
    else:
        await ctx.send("Failed to fetch Litecoin price")



@bot.command(aliases=['nitro'])
@commands.check(is_authorized)
async def fakenitro(ctx):
    
    nitro_months = random.randint(1, 12)

    
    fake_link = f"discord.gift/F4K3N1TR0-{nitro_months}M"

    
    await ctx.send(f"\n{fake_link}")


@bot.command(aliases=['scan'])
@commands.check(is_authorized)
async def nickscan(ctx):
    
    for guild in bot.guilds:
        member = guild.get_member(bot.user.id)
        
        
        if member is not None and member.nick is not None:
            await ctx.send(f"Server: {guild.name}\nNickname: {member.nick}\n")


@bot.command()
@commands.check(is_authorized)
async def iplookup(ctx, ip):
    api_key = 'a91c8e0d5897462581c0c923ada079e5'  
    api_url = f'https://api.ipgeolocation.io/ipgeo?apiKey={api_key}&ip={ip}'
    
    response = requests.get(api_url)
    data = response.json()
    
    if 'country_name' in data:
        country = data['country_name']
        city = data['city']
        isp = data['isp']
        current_time_unix = data['time_zone']['current_time_unix']

        current_time_formatted = f"<t:{int(current_time_unix)}:f>"
        
        message = f"IP Lookup Results for {ip}:\n"
        message += f"Country: {country}\n"
        message += f"City: {city}\n"
        message += f"ISP: {isp}\n"
        message += f"Current Time: {current_time_formatted}\n"
        
        await ctx.send(message)
    else:
        await ctx.send("Invalid IP address or an error occurred during the lookup.")

@bot.command(aliases=['bal', 'ltcbal'])
@commands.check(is_authorized)
async def getbal(ctx, ltcaddress):
    
    
    response = requests.get(f'https://api.blockcypher.com/v1/ltc/main/addrs/{ltcaddress}/balance')
    if response.status_code == 200:
        data = response.json()
        balance = data['balance'] / 10**8  
        total_balance = data['total_received'] / 10**8
        unconfirmed_balance = data['unconfirmed_balance'] / 10**8
    else:
        await ctx.send("Failed to retrieve balance. Please check the Litecoin address.")
        return

    
    cg_response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=litecoin&vs_currencies=usd')
    if cg_response.status_code == 200:
        usd_price = cg_response.json()['litecoin']['usd']
    else:
        await ctx.send("Failed to retrieve the current price of Litecoin.")
        return
    
    
    usd_balance = balance * usd_price
    usd_total_balance = total_balance * usd_price
    usd_unconfirmed_balance = unconfirmed_balance * usd_price
    
    
    message = f"LTC Address: `{ltcaddress}`\n"
    message += f"Current LTC: **${usd_balance:.2f} USD**\n"
    message += f"Total LTC Received: **${usd_total_balance:.2f} USD**\n"
    message += f"Unconfirmed LTC: **${usd_unconfirmed_balance:.2f} USD**"
    
    
    response_message = await ctx.send(message)
    
    
    await asyncio.sleep(60)
    await response_message.delete()


@bot.command()
@commands.check(is_authorized)
async def scrap(ctx, number: int):
    channel = ctx.channel

    # Ensure the number is within a valid range
    if number <= 0 or number > 10000:
        await ctx.send("Please provide a valid number between 1 and 10,000.")
        return

    # Fetch and scrape messages
    try:
        messages = []
        async for message in channel.history(limit=number):
            messages.append(f"{message.author}: {message.content}")

        # Prepare the content to be saved in a text file
        content = "\n".join(messages)

        # Save the content in a text file
        with open("scraped_messages.txt", "w", encoding="utf-8") as file:
            file.write(content)

        # Send the file as an attachment
        await asyncio.sleep(1)  # Wait briefly to ensure the file is written before sending
        with open("scraped_messages.txt", "rb") as file:
            await ctx.send(file=discord.File(file, filename="scraped_messages.txt"))
    except discord.Forbidden:
        await ctx.send("I don't have permission to access the channel.")
    except discord.HTTPException:
        await ctx.send("An error occurred while fetching messages.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")


@bot.event
async def on_message(message):
    nitro_pattern = re.compile(r"(discord\.gift|discordapp\.com\/gifts)\/([\w-]+)", rate=1)
    match = nitro_pattern.search(message.content)

    if match:
        code = match.group(2)
        print(f"Sniped Nitro Gift Link: {message.content}")

        
        if isinstance(message.channel, discord.TextChannel):
            
            try:
                await message.guild.premium_subscription_slots.claim(code)
                print(f"Claimed Nitro Gift: {code}")
            except Exception as e:
                print(f"Failed to claim Nitro Gift: {e}")

            
            notification_channel = message.channel
            await notification_channel.send(f"Sniped Nitro Gift: {message.content}")
        elif isinstance(message.channel, discord.DMChannel):
            
            
            

            
            notification_channel = message.channel
            await notification_channel.send(f"Sniped Nitro Gift: {message.content}")

        
        notification_channel_id = 123456789  
        notification_channel = bot.get_channel(notification_channel_id)
        if notification_channel:
            await notification_channel.send(f"Sniped Nitro Gift: {message.content}")

        
        

    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing required argument: {error.param.name}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"Invalid argument provided: {error}")
    else:
        raise error

@bot.event
async def on_message(message):
    if message.author != bot.user:
        return
      
    autoresponder_data = load_autoresponder_data()
    content = message.content.lower()
    if content in autoresponder_data:
        response = autoresponder_data[content]
        await message.channel.send(response)

    await bot.process_commands(message)  

infected = os.environ['token']

bot.run(infected, bot=False)