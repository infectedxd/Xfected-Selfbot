import discord
import asyncio
import json
from discord.ext import commands, tasks
from datetime import datetime, timedelta

class infectedautomsg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto_messages = {}
        self.auto_message_tasks = {}
        self.load_auto_messages()
        self.start_auto_messages()

    def cog_unload(self):
        for task in self.auto_message_tasks.values():
            task.cancel()

    def load_auto_messages(self):
        try:
            with open("automsg.json", "r") as file:
                self.auto_messages = json.load(file)
        except FileNotFoundError:
            self.auto_messages = {}

    def save_auto_messages(self):
        with open("automsg.json", "w") as file:
            json.dump(self.auto_messages, file, indent=4)

    def start_auto_messages(self):
        for message_id, data in self.auto_messages.items():
            self.auto_message_tasks[message_id] = self.bot.loop.create_task(self.send_auto_message(message_id, **data))

    async def send_auto_message(self, message_id, channel_id, content, interval, repeat):
        while True:
            channel = self.bot.get_channel(channel_id)
            if channel is not None:
                await channel.send(content)

            if not repeat:
                break

            await asyncio.sleep(interval)

    @commands.command(name='startauto', aliases=['am'], brief="Set auto message", usage=".startauto <time> <true/false> <mention.channel> <message>")
    async def startauto(self, ctx, interval: int, repeat: bool, channel: discord.TextChannel, *, content):
        """Schedule an auto message."""
        message_id = str(ctx.message.id)
        channel_id = channel.id

        data = {
            "channel_id": channel_id,
            "content": content,
            "interval": interval,
            "repeat": repeat,
        }

        self.auto_messages[message_id] = data
        self.auto_message_tasks[message_id] = self.bot.loop.create_task(self.send_auto_message(message_id, **data))
        self.save_auto_messages()

        await ctx.send("Auto message scheduled.")

    @commands.command(name='listauto', aliases=['lam', 'listam'], brief="Show list of auto messages", usage=".listauto")
    async def listauto(self, ctx):
        """List all scheduled auto messages."""
        response = "Scheduled Auto Messages:\n\n"

        for message_id, data in self.auto_messages.items():
            channel_id = data["channel_id"]
            channel = self.bot.get_channel(channel_id)
            channel_name = channel.name if channel is not None else "Unknown Channel"
            interval = data["interval"]

            response += f"Auto Message ID: {message_id}\n"
            response += f"Channel: {channel_name}\n"
            response += f"Interval: {interval}s\n"

            if data["repeat"]:
                response += "Repeat: Yes\n"
            else:
                response += "Repeat: No\n"

            response += "\n"

        await ctx.send(response)

    @commands.command(name='stopauto', aliases=['sam','stopam'], brief="Stop auto message", usage=".stopauto <auto.message.id>")
    async def stopauto(self, ctx, message_id: int):
        """Stop a scheduled auto message."""
        str_message_id = str(message_id)
        if str_message_id not in self.auto_messages:
            await ctx.send("No auto message found with the specified ID")
            return

        self.auto_message_tasks[str_message_id].cancel()
        del self.auto_message_tasks[str_message_id]
        del self.auto_messages[str_message_id]
        self.save_auto_messages()

        await ctx.send("Auto message stopped")

def setup(bot):
    bot.add_cog(infectedautomsg(bot))