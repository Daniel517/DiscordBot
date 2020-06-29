import discord
from discord.ext import commands
from ac_back.ACNHAPI import *
from ac_back.ACNHEmbedCreator import *
import asyncio

class ACNH(commands.Cog):
	
	#Initializer
	def __init__(self, client):
		self.client = client

	#Returns information on fish name entered 
	@commands.command()
	async def ac(self, ctx, search, *name):
		#Connects the rest of input into a single string
		full_name = "_".join(name)
		#Sends a loading gif while fetching data
		await ctx.message.channel.send(file = discord.File('./staticdata/load01.gif', 'load.gif'))
		if search.lower() == 'fish':
			fish_response = ACNHAPI.get_fish_info(fish_name=full_name)
			if 'error' not in fish_response:
				fish_embed = ACNHEmbedCreator.create_fish_embed(fish_response)
				await ctx.channel.purge(limit=1)
				await ctx.send(embed=fish_embed)
				return
			else:
				await ctx.channel.purge(limit=1)
				await ctx.send(fish_response['error'])
				return
		elif search.lower() == 'bug':
			bug_response = ACNHAPI.get_bug_info(bug_name=full_name)
			if 'error' not in bug_response:
				bug_embed = ACNHEmbedCreator.create_bug_embed(bug_response)
				await ctx.channel.purge(limit=1)
				await ctx.send(embed=bug_embed)
				return
			else:
				await ctx.channel.purge(limit=1)
				await ctx.send(bug_response['error'])
				return
		elif search.lower() == 'fossil':
			fossil_response = ACNHAPI.get_fossil_info(fossil_name=full_name)
			if 'error' not in fossil_response:
				fossil_embed = ACNHEmbedCreator.create_fossil_embed(fossil_response)
				await ctx.channel.purge(limit=1)
				await ctx.send(embed=fossil_embed)
				return
			else:
				await ctx.channel.purge(limit=1)
				await ctx.send(fossil_response['error'])
				return
		else:
			await ctx.channel.purge(limit=1)
			await ctx.send("Not a valid sub command. Enter bug/fish/fossil.")
			return

def setup(client):
	client.add_cog(ACNH(client))