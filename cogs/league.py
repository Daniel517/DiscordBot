import discord
from discord.ext import commands
import Credentials
from apps.LeagueAPI import LeagueAPI
from apps.LeagueImageCreator import LeagueImageCreator
import requests
import os
import asyncio

#LeagueCog which handles all league related commands
class League(commands.Cog):

	#Initializer
	def __init__(self, client):
		self.client = client

	#Returns image containing summoner data
	@commands.command()
	async def league(self, ctx, *summoner_names):
		summoner_names_str = " ".join(summoner_names)
		summoner_names_list = summoner_names_str.split(',')
		await ctx.send(summoner_names_list)

	# PASS IMG PASS INSTEAD OF GAME ID? PATH DECLARE BEFORE SECOND ERROR AND CHECKED IN ELIF OR USED IN SENDING BACK IMG
	#Returns image containing data of live game if summoner is in one
	@commands.command()
	async def live(self, ctx, *summoner_name):
		summoner_name_str = " ".join(summoner_name)
		# Sends a loading gif for users to know command is being processed
		await ctx.message.channel.send(file = discord.File('./staticdata/load01.gif', 'load.gif'))
		summoner_account_data = LeagueAPI.get_summoner_account_info(summoner_name_str)
		try:
			#Checks if there was an error getting summoner account data
			if 'error' in summoner_account_data:
				#Removes loading gif and then returns an error message
				await ctx.channel.purge(limit=1)
				await ctx.send(summoner_account_data['error'])
				return
			elif summoner_account_data:
				summoner_id = summoner_account_data['id']
				live_match_data = LeagueAPI.get_live_match_data(summoner_id)
				#Checks if there was an error getting live match data
				if 'error' in live_match_data:
					#Removes loading gif and then returns an error message
					await ctx.channel.purge(limit=1)
					await ctx.send(live_match_data['error'])
					return
				#If no error, checks if image already stored in imgs folder(used to remove unnecessary reprocessing of images for same game)
				elif os.path.exists(f'./imgs/{live_match_data["game_id"]}.png'):
					#Removes loading gif and then returns the already stored imge
					await ctx.channel.purge(limit=1)
					img_path = f'./imgs/{live_match_data["game_id"]}.png'
					await ctx.message.channel.send(file = discord.File(img_path, 'match.png'))
					return
				#If no error and image not already in imgs folder
				elif live_match_data:
					game_id = live_match_data['game_id']
					summoners = live_match_data['summoners']
					banned_champs = live_match_data['banned_champs']
					image_path = LeagueImageCreator.get_match_image(game_id, summoners, banned_champs)
					#Removes loading gif and then returns the image created
					await ctx.channel.purge(limit=1)
					await ctx.message.channel.send(file = discord.File(image_path, 'match.png'))
					#Waits 60 seconds to delete img in case command called for same match
					#CHANGE TO WHILE LOOP AND CHECK EVERY 3 MIN IF GAME STILL GOING ON, IF NOT DELETE IMG
					await asyncio.sleep(60)
					os.remove(image_path)
		except:
			await ctx.channel.purge(limit=1)
			await ctx.send('An error occured getting live match.')


def setup(client):
	client.add_cog(League(client))