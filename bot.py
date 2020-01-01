import discord
from discord.ext import commands
from discord import User
import os

import Credentials

client = commands.Bot(command_prefix = "!")

# Riot notice line (insert to custom help when created)
#'SecretBot isn’t endorsed by Riot Games and doesn’t reflect the views \nor opinions of Riot Games or anyone officially involved in producing or \nmanaging League of Legends. League of Legends and Riot Games are \ntrademarks or registered trademarks of Riot Games, Inc. League of \nLegends © Riot Games, Inc.'

@client.event
async def on_ready():
	print('Bot is ready!')

@client.command()
async def ping(ctx):
	"""Returns bot latency"""
	await ctx.send(f'Bot latency: {round(client.latency * 1000)}ms')

@client.command()
async def clear(ctx, amount=10):
	""""Clears given amount of messages, default value is 5. Command call is also deleted."""
	await ctx.channel.purge(limit=amount + 1)

@client.command()
async def load(ctx, extension):
	"""Loads cog"""
	client.load_extension(f'cogs.{extension}')

@client.command()
async def unload(ctx, extension):
	"""Unloads cog"""
	client.unload_extension(f'cogs.{extension}')

@client.command()
async def reload(ctx, extension):
	"""Reloads cog"""
	client.unload_extension(f'cogs.{extension}')
	client.load_extension(f'cogs.{extension}')

for filename in os.listdir('cogs'):
	if filename.endswith('.py'):
		client.load_extension(f'cogs.{filename[:-3]}')

client.run(Credentials.discord_token)