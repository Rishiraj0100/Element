import discord
import sys
import os
import traceback
import json
import asyncio
from discord.ext import commands, tasks
from itertools import cycle
from dotenv import load_dotenv
from keep_alive import keep_alive

def get_prefix(bot, message):
  if not message.guild:
    return commands.when_mentioned_or("--")(bot, message)

  with open("prefixes.json", "r") as f:
    prefixes = json.load(f)

  if str(message.guild.id) not in prefixes:
    return commands.when_mentioned_or("--")(bot, message)

  prefix = prefixes[str(message.guild.id)]
  return commands.when_mentioned_or(prefix)(bot, message)

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=get_prefix, intents=intents)
bot.remove_command('help')
status = cycle(["--help", "Discord Server, RSGameTech's Official"])

@bot.event
async def on_ready():
  change_status.start()
  print("Bot is online")

@tasks.loop(seconds=5)
async def change_status():
  await bot.change_presence(activity=discord.Game(next(status)))

#Reloads

@bot.command()
async def reload(ctx, cog=None):
  if not cog:
    #No cogs means Reload all the extension
    async with ctx.typing:
      embed = discord.Embed(
        title = "Reloading all Cogs!",
      )
      for ext in os.listdir("./cogs/"):
        if ext.endswith(".py") and not ext.startswith("_"):
          try:
            bot.unload_extension(f"cogs.{ext[:-3]}")
            bot.load_extension(f"cogs.{ext[:-3]}")
            embed.add_field(name="Reloaded:- `{ext}`!",value="\uFEFF",inline=False)
          except Exception as e:
            embed.add_field(name="Failed to reload:- `{ext}`",value=e)
          await asyncio.sleep(0.5)
      await ctx.send(embed=embed)
  else:
    #Reloads a specific extension
    async with ctx.typing:
      embed = discord.Embed(
        title = "Reloading Cogs!",
      )
      ext=f"{cog.lower()}.py"
      if not os.path.exists(f"./cogs/{ext}"):
          # if the file does not exist
          embed.add_field(name=f"Failed to reload:- `{ext}`",value="This cog does not exist.",inline=False)
      elif ext.endswith(".py") and not ext.startswith("_"):
          try:
              bot.unload_extension(f"cogs.{ext[:-3]}")
              bot.load_extension(f"cogs.{ext[:-3]}")
              embed.add_field(name=f"Reloaded: `{ext}`",value='\uFEFF',inline=False)
          except Exception:
              desired_trace = traceback.format_exc()
              embed.add_field(name=f"Failed to reload: `{ext}`",value=desired_trace,inline=False)
      await ctx.send(embed=embed)

extensions = ['cogs.moderation',
              'cogs.fun',
							'Server Event.join_leave',
							'Utility.avatar',
							'Utility.help',
							'Utility.prefix',
							'Utility.info',
							'Utility.ping',
              'Utility.ascii',
              'Extras.Chat',
              'Extras.source'
]
if __name__ == '__main__':
  for extension in extensions:
    try:
      bot.load_extension(extension)
    except Exception as e:
      print(f"Error loading {extension}", file=sys.stderr)
      traceback.print_exc()

keep_alive()
bot.run(os.getenv('TOKEN'))
