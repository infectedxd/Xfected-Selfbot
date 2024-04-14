#
# ▒██   ██▒  █████▒▓█████  ▄████▄  ▄▄▄█████▓▓█████ ▓█████▄ 
# ▒▒ █ █ ▒░▓██   ▒ ▓█   ▀ ▒██▀ ▀█  ▓  ██▒ ▓▒▓█   ▀ ▒██▀ ██▌
# ░░  █   ░▒████ ░ ▒███   ▒▓█    ▄ ▒ ▓██░ ▒░▒███   ░██   █▌
#  ░ █ █ ▒ ░▓█▒  ░ ▒▓█  ▄ ▒▓▓▄ ▄██▒░ ▓██▓ ░ ▒▓█  ▄ ░▓█▄   ▌
# ▒██▒ ▒██▒░▒█░    ░▒████▒▒ ▓███▀ ░  ▒██▒ ░ ░▒████▒░▒████▓ 
# ▒▒ ░ ░▓ ░ ▒ ░    ░░ ▒░ ░░ ░▒ ▒  ░  ▒ ░░   ░░ ▒░ ░ ▒▒▓  ▒ 
# ░░   ░▒ ░ ░       ░ ░  ░  ░  ▒       ░     ░ ░  ░ ░ ▒  ▒ 
# ░    ░   ░ ░       ░   ░          ░         ░    ░ ░  ░ 
# ░    ░             ░  ░░ ░                  ░  ░   ░    
#                        ░                         ░      
#               AGPL-3.0 license
#
#
import subprocess
try: 
    import os
    import sys
    import discord
    from discord.ext import commands, tasks
    import json
    import asyncio 
    from pyfiglet import Figlet
    from faker import Faker
    from discord import Member
    from asyncio import sleep 
    from decouple import config
    import re
    import requests
    import aiohttp
    import random
    import uuid
    import base64
    import string
    import ctypes
    import datetime
    import psutil
    import platform
    import colorama
    from colorama import Fore, Style
except ImportError:
    import os
    if sys.platform == 'win32' or 'win64':
     subprocess.check_call([sys.executable, "-m", "pip", "install", '-r' , 'requirements.txt'])
    else:
     subprocess.check_call([sys.executable, "-m", "pip3", "install", '-r' , 'requirements.txt'])
    import sys
    import discord
    from discord.ext import commands, tasks
    import json
    import asyncio 
    from pyfiglet import Figlet
    from faker import Faker
    from discord import Member
    from asyncio import sleep 
    from decouple import config
    import re
    import requests
    import aiohttp
    import random
    import uuid
    import base64
    import string
    import ctypes
    import datetime
    import psutil
    import platform
    import colorama
    from colorama import Fore, Style
    
os.system('cls' if os.name == 'nt' else 'clear')
colorama.init()

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

infection = int(config("userid"))
AUTHORIZED_USERS = [infection]  
prefix = config('prefix', default='')
bot = commands.Bot(command_prefix=prefix, self_bot=True, help_command=None)
xfected_version = "v2.2.5"
fake = Faker()

def is_authorized(ctx):
    return ctx.author.id in AUTHORIZED_USERS


@bot.command(description="Adds Auto Responses", aliases=['addresponse', 'aar'])
async def addar(ctx, trigger, *, response):
    autoresponder_data = load_autoresponder_data()
    autoresponder_data[trigger] = response
    save_autoresponder_data(autoresponder_data)
    await ctx.send(f'AR Added\n- **Trigger**~ _{trigger}_\n- **Response**~ _{response}_', delete_after=10)

@bot.command(description="Deletes Auto Responses", aliases=['deleteresponse', 'dar'])
async def deletear(ctx, trigger):
    autoresponder_data = load_autoresponder_data()
    if trigger in autoresponder_data:
        del autoresponder_data[trigger]
        save_autoresponder_data(autoresponder_data)
        await ctx.send(f'AR deleted\n- **Trigger**~ _{trigger}_', delete_after=10)
    else:
        await ctx.send('AR not found', delete_after=10)

@bot.command(description="Shows all Auto Responses", aliases=['listresponses', 'lar'])
@commands.check(is_authorized)
async def listar(ctx):
    autoresponder_data = load_autoresponder_data()
    if autoresponder_data:
        response = 'Xfected ARs\n'
        for trigger, response_text in autoresponder_data.items():
            response += f'- **{trigger}**~ ***{response_text}***\n'
        await ctx.send(response, delete_after=10)
    else:
        await ctx.send('No AR found', delete_after=10)


@bot.command(description="starts spammin the msges")
async def spam(ctx, xt: int, *, msg):
    for _ in range(xt):
        await ctx.send(msg)
        await asyncio.sleep(0.1)
        
@bot.command(description="calculates number and also can eval", aliases=['calculate', 'eval'])
async def calc(ctx, *, exps):
    try:
        ret = eval(exps)
        if isinstance(ret, str):
            if bot.http.token in ret:
                ret = ret.replace(bot.http.token, 'Xfected Token Redacted')
        await ctx.send(f'***{ret}***', delete_after=30)
    except Exception as e:
        await ctx.send(f'An error occurred', delete_after=10)
        
@bot.command(aliases=['mode'], description="sets user activities")
async def status(ctx, activity_type, *, text):
    activity = None
    if activity_type == 'playing':
        activity = discord.Game(name=text)
    elif activity_type == 'streaming':
        activity = discord.Streaming(name=text, url='https://www.twitch.tv/infectedxd')
    elif activity_type == 'listening':
        activity = discord.Activity(type=discord.ActivityType.listening, name=text)
    elif activity_type == 'watching':
        activity = discord.Activity(type=discord.ActivityType.watching, name=text)

    if activity:
        await bot.change_presence(activity=activity)
        await ctx.send(f'# Xfected Status updated~ {activity_type} {text}', delete_after=10)
    else:
        await ctx.send('- Invalid activity\n- Activies Supported\n- ***playing, streaming, listening, watching***', delete_after=10)

@bot.command(aliases=['h'], description="shows all cmds")
async def help(ctx, *, cmdname=None):
    if cmdname is None:
        cmdlist = bot.commands
        sortcmds = sorted(cmdlist, key=lambda x: x.name)

        hmsg = "**# X F E C T E D**\n"
        hmsg += f"- **{prefix}help** `<cmds>` for info\n\n"

        for i, command in enumerate(sortcmds):
            hmsg += f"***{command.name}*** , " if command.description else f"***{command.name}*** , "

        hmsg = hmsg[:-2]
        await ctx.send(hmsg, delete_after=60)
    else:
        command = bot.get_command(cmdname)
        if not command:
            await ctx.send(f"Cmd `{cmdname}` not found", delete_after=10)
            return

        xfechelpmsg = f"# Xfected Selfbot\n"
        xfechelpmsg += f"**{command.name}** : _{command.description}_\n"
        xfechelpmsg += f"- _`{prefix}{command.name} {command.signature}`_\n"
        await ctx.send(xfechelpmsg, delete_after=20)

@bot.command(aliases=['reboot'], description="restart the Xfected")
async def restart(ctx):
    restmsg = await ctx.send("# Xfected Rebooting !!")
    os.execv(sys.executable, ['python'] + sys.argv)
    await restmsg.channel.send("Rebooted")
    
@bot.command(description="converts text to ascii")
async def asci(ctx, *, text):
    f = Figlet(font='standard')
    xfecasc = f.renderText(text)

    border = '+' + '-' * (len(xfecasc.split('\n')[0]) + 2) + '+'
    xfecascb = f'```\n{border}\n| {xfecasc.strip()} |\n{border}\n```'

    await ctx.send(xfecascb, delete_after=45)


@bot.command(aliases=['ui', 'whois'], description="gives userinfo")
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    xfecusrrole = len(member.roles) - 1
    xfecsvrrole = len(ctx.guild.roles) - 1
    xfectusricon = member.avatar_url
    xfecui = [
        f"**@{member.name}** ({member.id})",
        f"- **Dates**\n - **Acc Created:** <t:{int(member.created_at.timestamp())}:f>\n - **Joined Server:** <t:{int(member.joined_at.timestamp())}:f>",
        f"- **Server**\n**Roles:** {xfecusrrole}\{xfecsvrrole}",
        f"[Icon URL](<{xfectusricon}>)"
    ]
    resp = '\n'.join(xfecui)
    await ctx.send(f"{resp}", delete_after=60)


@bot.command(description="trolls user with hack cmd")
async def hack(ctx, member: discord.Member = None):
    member = member or ctx.author

    hacking_messages = [
        "Infecting into the mainframe...",
        "Caching data...",
        "Decrypting security protocols...",
        "Extracting personal information...",
        "Compiling user profile...",
        f"{member.name} is now infected...."
    ]

    progress_message = await ctx.send("Hackin user...")
    for message in hacking_messages:
        await asyncio.sleep(2)
        await progress_message.edit(content=message)

    xfecfaked = {
        "Name": fake.name(),
        "Gender": fake.random_element(["Male", "Female", "Transgender"]),
        "Age": fake.random_int(min=18, max=99),
        "Height": f"{fake.random_int(min=150, max=200)} cm",
        "Weight": f"{fake.random_int(min=50, max=100)} kg",
        "Hair Color": fake.random_element(["Black", "Brown", "Blonde", "Red"]),
        "Skin Color": fake.random_element(["Fair", "Medium", "Dark"]),
        "DOB": fake.date_of_birth(minimum_age=18, maximum_age=99).strftime("%Y-%m-%d"),
        "Location": f"{fake.city()}, {fake.country()}",
        "Phone": fake.phone_number(),
        "E-Mail": fake.email(),
        "Passwords": fake.password(length=10),
        "Occupation": fake.job(),
        "Annual Salary": f"${fake.random_int(min=30000, max=100000)}",
        "Ethnicity": fake.random_element(["Caucasian", "African", "Indian", "Hispanic", "Nepali", "Other"]),
        "Religion": fake.random_element(["Christianity", "Islam", "Hinduism", "Buddhism", "Other", "Sanatani"]),
        "Sexuality": fake.random_element(["Straight", "Gay", "Lesbian", "Bisexual"]),
        "Education": fake.random_element(["High School", "Bachelor", "Master", "PhD"])
    }

    resp = f"Successfully hacked **@{member.name}**! Heres the hacked info\n\n"
    for key, value in xfecfaked.items():
        resp += f"{key}: {value}\n"

    await progress_message.edit(content=resp)


@bot.command(aliases=['av', 'ava'], description="shows avatar of users")
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author

    avatar_url = member.avatar_url
    await ctx.send(f"[Xfected]({avatar_url})", delete_after=45)


@bot.command(aliases=['latency'], description="shows selfbot latency")
async def ping(ctx):
    latency = round(bot.latency * 1000)  
    
    await ctx.send(f'**~ {latency}ms**', delete_after=10)


@bot.command(aliases=['247'], description="connect selfbot to vcs")
async def connectvc(ctx, channel_id):
    try:
        channel = bot.get_channel(int(channel_id))

        if channel is None:
            return await ctx.send("- invalid vc id", delete_after=10)

        if isinstance(channel, discord.VoiceChannel):
            permissions = channel.permissions_for(ctx.guild.me)

            if not permissions.connect:
                return await ctx.send("", delete_after=10)

            voice_channel = await channel.connect()
            await ctx.send(f"- Xfected is now connected~ **#{channel.name}**", delete_after=10)

        else:
            await ctx.send("- invalid vc id", delete_after=10)
    except discord.errors.ClientException:
        await ctx.send("- selfbot is already in a vc", delete_after=10)
    except discord.Forbidden:
        await ctx.send("- not have perms to connect", delete_after=10)
    except ValueError:
        await ctx.send("- invalid vc id", delete_after=10)
    except Exception as e:
        await ctx.send(f"- an error occured", delete_after=10)

@bot.command(aliases=['purge'], description="purges your msges")
async def clear(ctx, times: int):
    channel = ctx.channel
    
    def isxfectbotmsg(message):
        return message.author.id == ctx.bot.user.id
    
    msges = await channel.history(limit=times + 1).flatten()
    xfectbotmsg = filter(isxfectbotmsg, msges)
    
    for message in xfectbotmsg:
        await asyncio.sleep(0.75)  
        await message.delete()
    
    await ctx.send(f"- Cleared {times}x msges", delete_after=15)


bot.xfectstime = datetime.datetime.utcnow()
@bot.command(aliases=['selfbot'], description="shows yours stats")
async def stats(ctx):
    xfecttserv = len(bot.guilds)
    xfecmuse = psutil.Process().memory_full_info().rss / 1024 / 1024
    xfecusec = (datetime.datetime.utcnow() - bot.xfectstime).total_seconds()
    xfecuhrs = int(xfecusec // 3600)
    xfecumin = int((xfecusec % 3600) // 60)
    xfecusec = int(xfecusec % 60)

    xfectst = [
        f"**Servers ~** ***{xfecttserv}***",
        f"**Memory Usage ~** ***{xfecmuse:.2f}MB***",
        f"**Uptime ~** ***{xfecuhrs} hrs, {xfecumin} min, {xfecusec} sec***\n",
        "- **Dev - [@infectedxd](<https://solo.to/infected7>)**",
        "- **[Xfected Src Code](<https://github.com/infectedxd/Xfected-Selfbot>)**",
        "- **[InfectCord Premium](<https://infectcord.xyz>)**"
    ]

    await ctx.send("**# Xfected Stats**\n" + "\n".join(xfectst), delete_after=45)


@bot.command(aliases=['cltc'], description="shows real time ltc price")
async def ltcprice(ctx):
    url = 'https://api.coingecko.com/api/v3/coins/litecoin'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        price = data['market_data']['current_price']['usd']
        await ctx.send(f"The current price of Litecoin (LTC) is ${price:.2f}", delete_after=45)
    else:
        await ctx.send("Failed to fetch Litecoin price", delete_after=10)



@bot.command(aliases=['nitro'], description="gives fake nitro")
async def fakenitro(ctx):
    nitro_months = random.randint(1, 12)
    fake_link = f"discord.gift/xfected-{nitro_months}M"
    await ctx.send(f"\n{fake_link}", delete_after=45)

@bot.command(aliases=['nscan'], description="shows yours nickname of all server")
async def nickscan(ctx):
    for guild in bot.guilds:
        member = guild.get_member(bot.user.id)
        if member is not None and member.nick is not None:
            await ctx.send(f"- **Server {guild.name}** - ***{member.nick}***\n")


@bot.command(aliases=['ip'], description="shows ip info")
async def iplookup(ctx, ip):
    api_key = 'a91c8e0d5897462581c0c923ada079e5'  
    api_url = f'https://api.ipgeolocation.io/ipgeo?apiKey={api_key}&ip={ip}'
    
    resp = requests.get(api_url)
    data = resp.json()
    
    if 'country_name' in data:
        country = data['country_name']
        city = data['city']
        isp = data['isp']
        org = data['organization']
        timezone = data['time_zone']['name']
        latitude = data['latitude']
        longitude = data['longitude']
        country_flag_url = data['country_flag']
        
        xfecipinf = f"- **Xfected IP Lookup for {ip} ~**\n"
        xfecipinf += f" - **Country** ~ ***[{country}]({country_flag_url}) {data['country_emoji']}***\n"
        xfecipinf += f" - **City** ~ ***{city}***\n"
        xfecipinf += f" - **ISP** ~ ***{isp} ; {org}***\n"
        xfecipinf += f" - **Time Zone** ~ ***{timezone}***\n"
        xfecipinf += f" - **Coordinates** ~ ***{latitude}, {longitude}***\n"
        
        await ctx.send(xfecipinf, delete_after=45)
    else:
        await ctx.send("- Invalid IP or API Ratelimits", delete_after=10)

@bot.command(aliases=['bal', 'ltcbal'], description="shows ltc balance")
async def getbal(ctx, ltcaddress):
    
    
    response = requests.get(f'https://api.blockcypher.com/v1/ltc/main/addrs/{ltcaddress}/balance')
    if response.status_code == 200:
        data = response.json()
        balance = data['balance'] / 10**8  
        total_balance = data['total_received'] / 10**8
        unconfirmed_balance = data['unconfirmed_balance'] / 10**8
    else:
        await ctx.send("- Invalid LTC Addy", delete_after=10)
        return

    
    cg_response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=litecoin&vs_currencies=usd')
    if cg_response.status_code == 200:
        usd_price = cg_response.json()['litecoin']['usd']
    else:
        await ctx.send("- API Ratelimted", delete_after=10)
        return
    
    
    usd_balance = balance * usd_price
    usd_total_balance = total_balance * usd_price
    usd_unconfirmed_balance = unconfirmed_balance * usd_price
    
    message = f"- LTC Address~ **{ltcaddress}**\n"
    message += f"- Current LTC~ **${usd_balance:.2f} USD**\n"
    message += f"- Total LTC Received~ **${usd_total_balance:.2f} USD**\n"
    message += f"- Unconfirmed LTC~ **${usd_unconfirmed_balance:.2f} USD**"
    
    
    response_message = await ctx.send(message, delete_after=30)

@bot.command(description="rate anyones level of gayness")
async def gayrate(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.author

    if user.id == 1127377098647023758:
        xfecgay = 0
    else:
        xfecgay = random.randint(0, 100)
    resp = f"{user.mention} is {xfecgay}% gay"

    await ctx.reply(resp, delete_after=60)

@bot.command(description="rate anyones scammin abilities")
async def scamrate(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.author
        
    if user.id == 1127377098647023758:
        xfecscam = 0
    else:
        xfecscam = random.randint(0, 105)

    if xfecscam == 0:
        resp = f"{user.mention} is 100% trusted"
    elif xfecscam < 20:
        resp = f"{user.mention} has a low scam rate of {xfecscam}%, You can go first with em"
    elif xfecscam < 50:
        resp = f"{user.mention} has a mid scam rate of {xfecscam}%. Use any MM when dealing with them"
    elif xfecscam < 80:
        resp = f"{user.mention} has a high scam rate of {xfecscam}%. Use trusted MM only"
    else:
        resp = f"{user.mention} is a poor scammer with a scam rate of {xfecscam}%, Stay away and block this dalit"

    await ctx.reply(resp, delete_after=60)
    
roapi = "https://evilinsult.com/generate_insult.php"

@bot.command(description="roasts someone")
async def roast(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.author

    if user.id == 1127377098647023758:
        await ctx.reply("You want to roast your daddy?", delete_after=60)
        return

    params = {
        "lang": "en",
        "type": "json"
    }

    try:
        response = requests.get(roapi, params=params)
        if response.status_code == 200:
            insult_data = response.json()
            roast = insult_data["insult"]
            await ctx.reply(f"{user.mention}, {roast}", delete_after=60)
        else:
            await ctx.reply("API Ratelimit", delete_after=10)
    except Exception as e:
        print("Error:", e)
        await ctx.reply("Try again later", delete_after=10)


@bot.command(description="scrape msges")
async def scrap(ctx, limit: int = 10000):
    channel = ctx.channel

    messages = await channel.history(limit=limit).flatten()

    html_content = f"<html><head><title>Xfected Scraped Msges</title></head><body>"
    html_content += f"<h1>Server: {channel.guild.name}</h1>"
    html_content += f"<h2>Channel: {channel.name}</h2>"

    for message in messages:
        user = message.author
        user_icon = user.avatar_url
        time = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
        username = user.name

        html_content += f"<div>"
        html_content += f"<img src='{user_icon}' alt='User Icon' width='50' height='50'>"
        html_content += f"<p>{time} - {username}</p>"
        html_content += f"<p>{message.content}</p>"
        html_content += f"</div>"

    html_content += "</body></html>"

    with open("scrap.html", "w", encoding="utf-8") as file:
        file.write(html_content)

    await ctx.send(file=discord.File("scrap.html"))
    
@bot.command(description="it will grab anyones token (satire)")
async def tokengrab(ctx, member: discord.Member):
    with open("./data/tokens.json", "r") as json_f:
        data = json.load(json_f)

    msg = ctx.message
    xfecmemid = str(member.id)
    xfecmemidb64 = base64.b64encode(xfecmemid.encode()).decode()

    if xfecmemid not in data:
        timest = "".join(random.choices(
            string.ascii_letters + string.digits + "-" + "_", k=6))
        last = "".join(random.choices(
            string.ascii_letters + string.digits + "-" + "_", k=27))
        token = f"{xfecmemidb64}.{timest}.{last}"
        data[xfecmemid] = token

        with open("./data/tokens.json", "w") as out:
            json.dump(data, out, indent=4)

        await msg.edit(content=f"```yaml\n+ Xfected token grabbed for {member}\nToken~ {token}```")
    else:
        token = data[xfecmemid]
        await msg.edit(content=f"```yaml\n+ Xfected token grabbed for {member}\nToken~ {token}```")
    

def infectedxd(title):
    system = platform.system()
    if system == 'Windows':
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    elif system == 'Darwin':
        subprocess.run(['osascript', '-e', f'tell application "Terminal" to set custom title of front window to "{title}"'])
    elif system == 'Linux':
        sys.stdout.write(f"\x1b]2;{title}\x07")
        sys.stdout.flush()
try:
   infectedxd("Xfected Selfbot")
except Exception as e:
   print(f"Error while trying to change the terminal name: {e}")
   
@bot.event
async def on_ready():
    colorama.init() 
    
    def xfectascitit():
        b = Fore.LIGHTMAGENTA_EX
        y = Fore.MAGENTA
        w = Fore.WHITE
        print(f"\n\n{Style.RESET_ALL}")
        print(f"""
____  ___ _____              __             .___
\   \/  // ____\____   _____/  |_  ____   __| _/
 \     /\   __\/ __ \_/ ___\   __\/ __ \ / __ | 
 /     \ |  | \  ___/\  \___|  | \  ___// /_/ | 
/___/\  \|__|  \___  >\___  >__|  \___  >____ | 
      \_/          \/     \/          \/     \/\n""".replace('█', f'{b}█{y}'))
        print(f"""{y}-----------------------------------------------------\n{w}infectedxd {b}|{w} https://discord.gg/infection {b}|{w} https://github.com/infectedxd {b}|{w} https://solo.to/infected7 {b}|{w} https://infected.store {b}\n-----------------------------------------------------\n""")
        print(f"{y}[{b}+{y}]{w} Xfected Stats")
        print(f"{y}[{b}+{y}]{w} Version > v2")
        print(f"{y}[{b}+{y}]{w} Connected As > @{bot.user.name}")
        print(f"{y}[{b}+{y}]{w} User ID > {bot.user.id}")
        print(f"{y}[{b}+{y}]{w} Settings")
        print(f"{y}[{b}+{y}]{w} Prefix > {bot.command_prefix}")
        print(f"{y}[{b}+{y}]{w} Cached Users > {len(bot.users)}")
        print(f"{y}[{b}+{y}]{w} Cached Guilds > {len(bot.guilds)}")
        
    xfectascitit()
    
    def check_latest_version(repo_owner, repo_name):
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        response = requests.get(url)
        
        if response.status_code == 200:
            release_info = response.json()
            latest_version = release_info['tag_name']
            return latest_version
        else:
            return None

    def call_check_repo():
        global xfected_version
        repo_owner = "infectedxd"
        repo_name = "Xfected-Selfbot"
        current_version = xfected_version
        
        latest_version = check_latest_version(repo_owner, repo_name)
        if latest_version:
            if not latest_version == current_version:
                b = Fore.LIGHTMAGENTA_EX
                y = Fore.MAGENTA
                w = Fore.WHITE
                print(f"{y}[{b}+{y}]{w} You are using old version ", current_version)
                print(f"{y}[{b}+{y}]{w} Latest Version Detected: {latest_version}\nhttps://github.com/infectedxd/Xfected-Selfbot/releases/tag/{latest_version}")
                

    try:
        call_check_repo()
    except Exception as e:
        print(f"Error while trying to check the last Xfected version: {e}") 

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

infected = config('token')

if __name__ == "__main__":
    bot.load_extension("automsg")
    bot.run(infected, bot=False)
