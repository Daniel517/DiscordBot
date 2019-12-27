import discord
from discord.ext import commands
import Credentials
import requests

class League(commands.Cog):

	def __init__(self, client):
		self.client = client
		self.headers = {'X-Riot-Token' : Credentials.riot_token}
		self.host = 'https://na1.api.riotgames.com'

	@commands.command()
	async def league(self, ctx, username):
		embed = discord.Embed()
		summoner_info = self.get_summoner_info(username)
		if 'error' in summoner_info:
			await ctx.send(summoner_info['error'])
			return
		elif summoner_info:
			embed.set_author(name=f'{username} #{summoner_info["summonerLevel"]}', icon_url=f'http://ddragon.leagueoflegends.com/cdn/9.24.2/img/profileicon/{summoner_info["profileIconId"]}.png')
		summoner_rank = self.get_summoner_rank(summoner_info['id'])
		if 'error' in summoner_rank:
			await ctx.send(summoner_rank['error'])
			return
		elif summoner_rank:
			for queue_data in summoner_rank:
				embed.add_field(name=queue_data['queue'], value=f'{queue_data["rank"]}\n{queue_data["games_played"]} ({queue_data["win_rate"]}%)', inline=True)
		summoner_match_data = self.get_summoner_data(summoner_info['accountId'])
		if 'error' in summoner_match_data:
			await ctx.send(summoner_match_data['error'])
			return
		elif summoner_match_data:
			top_five_champs = dict(list(summoner_match_data[0].items())[0:5])
			top_two_roles = dict(list(summoner_match_data[1].items())[0:2])
			str_for_champ_embed = ''
			for champ in top_five_champs:
				str_for_champ_embed += f'{self.get_champ_from_id(str(champ))} ({top_five_champs[champ]}%)\n' 
			embed.add_field(name='Top 5 Champs Played:', value=str_for_champ_embed, inline=False)
			str_for_role_embed = ''
			for role in top_two_roles:
				str_for_role_embed += f'{role} ({top_two_roles[role]}%)\n'
			embed.add_field(name='Top 2 Roles Played:', value=str_for_role_embed, inline=True)
		await ctx.message.channel.send(embed = embed)

	def get_summoner_info(self, username):
		summoner_data = requests.get(f'{self.host}/lol/summoner/v4/summoners/by-name/{username}', headers = self.headers)
		if summoner_data.status_code == 200:
			return summoner_data.json()
		elif summoner_data.status_code == 404:
			print(f'Error getting summoner data, code: {summoner_data.status_code}')
			return {'error' : f'Summoner "{username}" not found!'}
		else:
			print(f'Error getting summoner data, code: {summoner_data.status_code}')
			return {'error' : 'An error occurred!'}

	def get_summoner_rank(self, summoner_id):
		summoner_rank = requests.get(f'{self.host}/lol/league/v4/entries/by-summoner/{summoner_id}', headers = self.headers)
		if summoner_rank.status_code == 200:
			ranked_data = []
			for queue in summoner_rank.json():
				queue_data = {}
				if queue['queueType'] == 'RANKED_SOLO_5x5':
					queue_data = {'queue' : 'Ranked Solo/Duo', 'rank' : queue['tier'] + ' ' + queue['rank']}
				if queue['queueType'] == 'RANKED_FLEX_SR':
					queue_data = {'queue' : 'Ranked Flex', 'rank' : queue['tier'] + ' ' + queue['rank']}
				games_played = int(queue['wins']) + int(queue['losses'])
				win_rate = int(queue['wins']) / games_played
				queue_data.update({'games_played' : str(games_played), 'win_rate' : str(round(win_rate * 100))})
				ranked_data.append(queue_data)
			return ranked_data
		else:
			print(f'Error getting summoner rank data, code: {summoner_rank.status_code}')
			return {'error' : 'An error occurred!'}

	def get_summoner_data(self, account_id):
		summoner_data = requests.get(f'{self.host}/lol/match/v4/matchlists/by-account/{account_id}', headers = self.headers)
		matches = summoner_data.json()['matches']
		if summoner_data.status_code == 200:
			roles_played = {}
			champs_played = {}
			for match in matches:
				match_champ = match['champion']
				if match_champ in champs_played:
					champs_played[match_champ] += 1
				else:
					champs_played.update({match_champ : 1})
				match_role = match['lane']
				if match_role in roles_played:
					roles_played[match_role] += 1
				elif match_role == 'NONE' or match_role == 'BOTTOM':
					match_bot_role = match['role']
					if match_bot_role in roles_played:
						roles_played[match_bot_role] += 1
					else:
						roles_played.update({match_bot_role : 1})
				else:
					roles_played.update({match_role : 1})
			sorted_champs = {k: v for k, v in sorted(champs_played.items(), key=lambda item: item[1], reverse=True)}
			sorted_roles = {k: v for k, v in sorted(roles_played.items(), key=lambda item: item[1], reverse=True)}
			return [sorted_champs, sorted_roles]
		else:
			print(f'Error getting summoner match data, code: {summoner_rank.status_code}')
			return {'error' : 'An error occurred!'}

	def get_champ_from_id(self, champ_id: str):
		response = requests.get(f'http://ddragon.leagueoflegends.com/cdn/9.24.2/data/en_US/champion.json')
		champs = response.json()['data']
		for champ_name, value in champs.items():
			for key, val2 in value.items(): 
				if key == 'key' and val2 == champ_id:
					return champ_name

def setup(client):
	client.add_cog(League(client))