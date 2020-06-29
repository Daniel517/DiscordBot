import discord
from discord.ext import commands
from discord import User
import os

import Credentials

client = commands.Bot(command_prefix = "!")
client.remove_command('help')

# Riot notice line (insert to custom help when created)
#'SecretBot isn’t endorsed by Riot Games and doesn’t reflect the views \nor opinions of Riot Games or anyone officially involved in producing or \nmanaging League of Legends. League of Legends and Riot Games are \ntrademarks or registered trademarks of Riot Games, Inc. League of \nLegends © Riot Games, Inc.'

@client.event
async def on_ready():
	print('Bot is ready!')

@client.command()
async def sbothelp(ctx):
	"""Returns list of possible commands"""
	embed = discord.Embed(description='Below Are All The Commands For SecretBot')
	embed.set_author(name='SecretBot Help Center')
	embed.add_field(name='***`!ping`***', value='Returns the bot latency', inline=False)
	embed.add_field(name='***`!clear`***', value='Deletes the given amount of messages(default 10) \n***i.e. !clear 20***', inline=False)
	embed.add_field(name='***`!live`***', value='Shows an image with data from a live League of Legends game \n***i.e. !live NA Test Summoner Name***', inline=False)
	embed.add_field(name='***`!league`***', value='Shows an image with data of a summoner \nFor multiple summoners, split by commas \n***i.e. !league NA Test_Summoner_Name***', inline=False)
	embed.add_field(name='***`!ac`***', value='Shows data on bugs, fossils, or fish\n***i.e. !ac fish horse mackerel***', inline=False)
	embed.set_footer(text='SecretBot isn’t endorsed by Riot Games and doesn’t reflect the views or opinions of Riot Games or anyone officially involved in producing or managing League of Legends. League of Legends and Riot Games are trademarks or registered trademarks of Riot Games, Inc. League of Legends © Riot Games, Inc.')
	await ctx.send(embed=embed)

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