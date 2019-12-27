import discord
from discord.ext import commands
import os

import Credentials

client = commands.Bot(command_prefix = "!")

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
async def snake(ctx, user):
	await ctx.reply(ctx.message.user)

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