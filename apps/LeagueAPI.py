import requests
import Credentials

class LeagueAPI():
	
	headers = {'X-Riot-Token' : Credentials.riot_token}
	host = 'https://na1.api.riotgames.com'

	@staticmethod
	def get_summoner_info(username):
		summoner_data = requests.get(f'{LeagueAPI.host}/lol/summoner/v4/summoners/by-name/{username}', headers = LeagueAPI.headers)
		if summoner_data.status_code == 200:
			return summoner_data.json()
		elif summoner_data.status_code == 404:
			print(f'Error getting summoner data, code: {summoner_data.status_code}')
			return {'error' : f'Summoner "{username}" not found!'}
		else:
			print(f'Error getting summoner data, code: {summoner_data.status_code}')
			return {'error' : 'An error occurred!'}

	def get_summoner_rank(summoner_id):
		summoner_rank = requests.get(f'{LeagueAPI.host}/lol/league/v4/entries/by-summoner/{summoner_id}', headers = LeagueAPI.headers)
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

	def get_summoner_data(account_id):
		summoner_data = requests.get(f'{LeagueAPI.host}/lol/match/v4/matchlists/by-account/{account_id}', headers = LeagueAPI.headers)
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

	def get_champ_from_id(champ_id: str):
		response = requests.get(f'http://ddragon.leagueoflegends.com/cdn/9.24.2/data/en_US/champion.json')
		champs = response.json()['data']
		for champ_name, value in champs.items():
			for key, val2 in value.items(): 
				if key == 'key' and val2 == champ_id:
					return champ_name