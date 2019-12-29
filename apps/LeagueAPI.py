import requests
import Credentials

class LeagueAPI():
	
	headers = {'X-Riot-Token' : Credentials.riot_token}
	host = 'https://na1.api.riotgames.com'

	response_queues = requests.get('http://static.developer.riotgames.com/docs/lol/queues.json')
	response_game_modes = requests.get('http://static.developer.riotgames.com/docs/lol/gameModes.json')
	response_champs = requests.get('http://ddragon.leagueoflegends.com/cdn/9.24.2/data/en_US/champion.json')

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
		if summoner_data.status_code == 200:
			matches = summoner_data.json()['matches']
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
		if LeagueAPI.response_champs.status_code == 200:
			champs = LeagueAPI.response_champs.json()['data']
			for champ_name, value in champs.items():
				for key, val2 in value.items(): 
					if key == 'key' and val2 == champ_id:
						return champ_name
			return "None"


	def get_live_match(summoner_id):
		summoner_live_data = requests.get(f'{LeagueAPI.host}/lol/spectator/v4/active-games/by-summoner/{summoner_id}', headers = LeagueAPI.headers)
		summoners = []
		banned_champs = []
		if summoner_live_data.status_code == 200:
			for summoner_data in summoner_live_data.json()['participants']:
				player_info = {'name' : summoner_data['summonerName'], 'champ' : LeagueAPI.get_champ_from_id(str(summoner_data['championId'])), 'team' : summoner_data['teamId']}
				summoners.append(player_info)
			for  banned_champ_data in summoner_live_data.json()['bannedChampions']:
				banned_champ = {'champ' : LeagueAPI.get_champ_from_id(str(banned_champ_data['championId'])), 'team' : banned_champ_data['teamId'], 'turn_banned' : banned_champ_data['pickTurn']}
				banned_champs.append(banned_champ)
			return {'game_type': LeagueAPI.get_mode_from_data(summoner_live_data.json()), 'summoners': summoners, 'banned' : banned_champs}
		elif summoner_live_data.status_code == 404:
			print(f'Error getting summoner match data, code: {summoner_live_data.status_code}')
			return {'error' : 'No live match found!'}
		else:
			print(f'Error getting summoner match data, code: {summoner_live_data.status_code}')
			return {'error' : 'An error occurred!'}

	def get_mode_from_data(match_data):
		if match_data['gameMode'] == 'CLASSIC':
			return LeagueAPI.get_mode_from_queue_id(match_data['gameQueueConfigId'])
		else:
			return LeagueAPI.get_description_from_mode(match_data['gameMode'])

	def get_mode_from_queue_id(queue_id):
		if LeagueAPI.response_queues.status_code == 200:
			queues = LeagueAPI.response_queues.json()
			for queue in queues:
				if queue['queueId'] == queue_id:
					return queue['description'][:-6]
		else:
			print(f'Error getting summoner match data, code: {summoner_live_data.status_code}')
			return 'Error occurred getting mode from queueId'

	def get_description_from_mode(game_mode_in):
		if LeagueAPI.response_game_modes.status_code == 200:
			for game_mode in LeagueAPI.response_game_modes.json():
				if game_mode['gameMode'] == game_mode_in:
					return game_mode['description'][:-6]
		else:
			print(f'Error getting summoner match data, code: {summoner_live_data.status_code}')
			return 'Error occurred getting description from game mode'
















