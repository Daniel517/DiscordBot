import discord
from discord.ext import commands
import Credentials
from apps.LeagueAPI import LeagueAPI as lapi
import requests

class League(commands.Cog):

	def __init__(self, client):
		self.client = client

	@commands.command()
	async def league(self, ctx, username):
		"""Returns data on a summoner. Given a summoner name, returns level, rank, top 5 champs played, top 2 roles played."""
		embed = discord.Embed(colour=0x0064ff)
		summoner_info = lapi.get_summoner_info(username)
		if 'error' in summoner_info:
			await ctx.send(summoner_info['error'])
			return
		elif summoner_info:
			embed.set_author(name=f'{username} #{summoner_info["summonerLevel"]}', icon_url=f'http://ddragon.leagueoflegends.com/cdn/9.24.2/img/profileicon/{summoner_info["profileIconId"]}.png')
		summoner_rank = lapi.get_summoner_rank(summoner_info['id'])
		if 'error' in summoner_rank:
			await ctx.send(summoner_rank['error'])
			return
		elif summoner_rank:
			for queue_data in summoner_rank:
				embed.add_field(name=queue_data['queue'], value=f'{queue_data["rank"]}\n{queue_data["games_played"]} ({queue_data["win_rate"]}%)', inline=True)
		summoner_match_data = lapi.get_summoner_data(summoner_info['accountId'])
		if 'error' in summoner_match_data:
			await ctx.send(summoner_match_data['error'])
			return
		elif summoner_match_data:
			top_five_champs = dict(list(summoner_match_data[0].items())[0:5])
			top_two_roles = dict(list(summoner_match_data[1].items())[0:2])
			str_for_champ_embed = ''
			for champ in top_five_champs:
				str_for_champ_embed += f'{lapi.get_champ_from_id(str(champ))} ({top_five_champs[champ]}%)\n' 
			embed.add_field(name='Top 5 Champs Played:', value=str_for_champ_embed, inline=False)
			str_for_role_embed = ''
			for role in top_two_roles:
				str_for_role_embed += f'{role} ({top_two_roles[role]}%)\n'
			embed.add_field(name='Top 2 Roles Played:', value=str_for_role_embed, inline=True)
		embed.set_footer(text="SecretBot isn’t endorsed by Riot Games and doesn’t reflect the views \nor opinions of Riot Games or anyone officially involved in producing or \nmanaging League of Legends. League of Legends and Riot Games are \ntrademarks or registered trademarks of Riot Games, Inc. League of \nLegends © Riot Games, Inc.")
		await ctx.message.channel.send(embed = embed)

	@commands.command()
	async def live(self, ctx, username):
		"""Returns data of live game if summoner is in one"""
		embed = discord.Embed(colour=0x0fff00)
		summoner_info = lapi.get_summoner_info(username)
		if 'error' in summoner_info:
			await ctx.send(summoner_info['error'])
			return
		elif summoner_info:
			embed.set_author(name=f'{username} #{summoner_info["summonerLevel"]}', icon_url=f'http://ddragon.leagueoflegends.com/cdn/9.24.2/img/profileicon/{summoner_info["profileIconId"]}.png')
		summoner_live_data = lapi.get_live_match(summoner_info['id'])
		if 'error' in summoner_live_data:
			await ctx.send(summoner_live_data['error'])
			return
		elif summoner_live_data:
			embed.description = summoner_live_data['game_type']
			blue_team_names = ''
			red_team_names = ''
			blue_team_champs = ''
			red_team_champs = ''
			for summoner in summoner_live_data['summoners']:
				if summoner['team'] == 100:
					blue_team_names += f'{summoner["name"]}\n'
					blue_team_champs += f'{summoner["champ"]}\n'
				else:
					red_team_names += f'{summoner["name"]}\n'
					red_team_champs += f'{summoner["champ"]}\n'
			blue_team_bans = ''
			red_team_bans = ''
			if summoner_live_data['banned']:
				for ban in summoner_live_data['banned']:
					if ban['team'] == 100:
						blue_team_bans += f'{ban["champ"]}\n'
					else:
						red_team_bans += f'{ban["champ"]}\n'
			else:
				blue_team_bans = 'Not\nAvailable'
				red_team_bans = 'Not\nAvailable'
			embed.add_field(name='Blue Team', value=blue_team_names, inline=True)
			embed.add_field(name='Champ', value=blue_team_champs, inline=True)
			embed.add_field(name='Bans', value=blue_team_bans, inline=True)
			embed.add_field(name='Red Team', value=red_team_names, inline=True)
			embed.add_field(name='Champ', value=red_team_champs, inline=True)
			embed.add_field(name='Bans', value=red_team_bans, inline=True)
		embed.set_footer(text="SecretBot isn’t endorsed by Riot Games and doesn’t reflect the views or opinions of Riot Games or anyone officially involved in producing or managing League of Legends. League of Legends and Riot Games are trademarks or registered trademarks of Riot Games, Inc. League of Legends © Riot Games, Inc.")
		await ctx.message.channel.send(embed=embed)


def setup(client):
	client.add_cog(League(client))