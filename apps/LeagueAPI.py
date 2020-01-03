import requests
import Credentials
from apps.LeagueImageCreator import LeagueImageCreator

class LeagueAPI():

	#Static variable for use in requests
	host = 'https://na1.api.riotgames.com'
	headers = {'X-Riot-Token' : Credentials.riot_token}

	#Responses of requests containing json data(stored and then reused instead of calling every time needed)
	#FASTER? SLOWER? IF CALLED EVERY TIME
	response_queues = requests.get('http://static.developer.riotgames.com/docs/lol/queues.json')
	response_game_modes = requests.get('http://static.developer.riotgames.com/docs/lol/gameModes.json')
	response_champs = requests.get('http://ddragon.leagueoflegends.com/cdn/9.24.2/data/en_US/champion.json')
	response_perks = requests.get('http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/perks.json')
	response_summoner_spells = requests.get('http://ddragon.leagueoflegends.com/cdn/9.24.2/data/en_US/summoner.json')

	#Gets top level account data on a given summoner such as summoner id and summoner level
	def get_summoner_account_info(summoner_name):
		summoner_account_data = requests.get(f'{LeagueAPI.host}/lol/summoner/v4/summoners/by-name/{summoner_name}', headers = LeagueAPI.headers)
		#Checks if request was successful
		if summoner_account_data.status_code == 200:
			#Returns json of summoner account data
			return summoner_account_data.json()
		#Returns custom error message if summoner name was not found
		elif summoner_account_data.status_code == 404:
			return {'error' : f'Summoner "{summoner_name}" not found!'}
		else:
			return {'error' : 'An error occurred!'}

	#Gets data for summoner card such as rank and most played champs
	def get_summoner_card_data(summoner_account_data, begin_index=0, end_index=100):
		summoner_name = summoner_account_data['name']
		summoner_icon = summoner_account_data['profileIconId']
		summoner_id = summoner_account_data['id']
		summoner_rank_data = LeagueAPI.get_summoner_ranked_solo_flex_data(summoner_id)
		if 'error' in summoner_rank_data:
			return summoner_rank_data
		account_id = summoner_account_data['accountId']
		most_played_champs_roles = LeagueAPI.get_summoner_most_played_champs_and_roles(account_id, begin_index, end_index)
		if 'error' in most_played_champs_roles:
			return most_played_champs_roles
		return {'summoner_name': summoner_name, 'summoner_icon' : summoner_icon, 'rank_data' : summoner_rank_data, 'most_played_champs' : most_played_champs_roles[0], 'most_played_roles' : most_played_champs_roles[1]}

	#Gets data on a live match given a summoner id such as summoners in match
	def get_live_match_data(summoner_id):
		#Request url for live match data
		live_match_data_url = f'{LeagueAPI.host}/lol/spectator/v4/active-games/by-summoner/{summoner_id}'
		summoner_live_data_response = requests.get(live_match_data_url, headers = LeagueAPI.headers)
		#Checks if requests for live match data was successful
		if summoner_live_data_response.status_code == 200:
			summoner_live_data = summoner_live_data_response.json()
			game_type = LeagueAPI.get_game_type_from_match_data(summoner_live_data)
			game_id = summoner_live_data['gameId']
			#Iterates through all summoners in match and stores data into summoners list
			summoners = []
			for summoner_data in summoner_live_data['participants']:
				summoner_name = summoner_data['summonerName']
				ranked_data = LeagueAPI.get_summoner_rank_from_queue_id(summoner_data['summonerId'], summoner_live_data['gameQueueConfigId'])
				champ_name = LeagueAPI.get_champ_name_from_id(str(summoner_data['championId']))
				mastery_points = LeagueAPI.get_summoner_mastery_points_for_champion(summoner_data['summonerId'], summoner_data['championId'])
				perks_data = []
				#Iterates through all perks of a summoner and gets information on each perk such as perk name
				for perk_id in summoner_data['perks']['perkIds']:
					perks_data.append(LeagueAPI.get_perk_info_from_id(str(perk_id)))
				spell_1_name = LeagueAPI.get_summoner_spell_name_from_id(summoner_data['spell1Id'])
				spell_2_name = LeagueAPI.get_summoner_spell_name_from_id(summoner_data['spell2Id'])
				team = summoner_data['teamId']
				#Creates a dictionary with data of the summoner
				player_info = {'name' : summoner_name, 'rank_data' : ranked_data, 'champ_name' : champ_name, 'mastery_points' : mastery_points, 'perks' : perks_data, 'spell_1' : spell_1_name, 'spell_2' : spell_2_name, 'team' : team}
				summoners.append(player_info)
			#Iterates through all champions banned in match and stores data into banned champs list
			banned_champs = []
			for banned_champ_data in summoner_live_data['bannedChampions']:
				champ_name = LeagueAPI.get_champ_name_from_id(str(banned_champ_data['championId']))
				team_banned = banned_champ_data['teamId']
				turn_banned = banned_champ_data['pickTurn']
				#Creates a dictionary with data of the champions banned in the match
				banned_champ = {'champ' : champ_name, 'team' : team_banned, 'turn_banned' : turn_banned}
				banned_champs.append(banned_champ)
			return {'game_type': game_type, 'game_id' : game_id,'summoners': summoners, 'banned_champs' : banned_champs}
		#Returns custom error message if live match was not found
		elif summoner_live_data_response.status_code == 404:
			return {'error' : 'No live match found!'}
		else:
			return {'error' : 'An error occurred getting live match information!'}

	# Gets summoner's top 5 most played champs and top 2 roles in the desired 
	# amount of past game(default is set to past 100 games), error if getting data
	def get_summoner_most_played_champs_and_roles(account_id, begin_index, end_index):
		#Request url for match history
		request_url = f'{LeagueAPI.host}/lol/match/v4/matchlists/by-account/{account_id}?endIndex={end_index}&beginIndex={begin_index}'
		summoner_data = requests.get(request_url, headers = LeagueAPI.headers)
		#Checks if request was successful
		if summoner_data.status_code == 200:
			matches = summoner_data.json()['matches']
			roles_played = {}
			champs_played = {}
			#Iterates through all of the matches
			for match in matches:
				champ = match['champion']
				#Increments champ counter by one if already in dictionary, else it adds champ to dictionary of champs played
				if champ in champs_played:
					champs_played[champ] += 1
				else:
					champs_played.update({champ : 1})
				match_role = match['lane']
				#Increments role counter by one if already in dictionary
				if match_role in roles_played:
					roles_played[match_role] += 1
				#If lane is bot, checks role to see if summoner is either adc or support
				elif match_role == 'NONE' or match_role == 'BOTTOM':
					match_bot_role = match['role']
					#Increments role counter by one if already in dictionary, else it adds role to dictionary of roles played
					if match_bot_role in roles_played:
						roles_played[match_bot_role] += 1
					else:
						roles_played.update({match_bot_role : 1})
				#Adds role to dictionary of roles played
				else:
					roles_played.update({match_role : 1})
			#Sorts champ and roles dictionaries in order of number of times played
			sorted_champs = {k: v for k, v in sorted(champs_played.items(), key=lambda item: item[1], reverse=True)}
			sorted_roles = {k: v for k, v in sorted(roles_played.items(), key=lambda item: item[1], reverse=True)}
			top_five_champs = dict(list(sorted_champs.items())[0:5])
			top_two_roles = dict(list(sorted_roles.items())[0:2])
			#Replaces champ ids with champ names
			top_five_champs_with_names = {}
			for champ_id, times_played in top_five_champs.items():
				top_five_champs_with_names.update({LeagueAPI.get_champ_name_from_id(str(champ_id)) : times_played})
			return [top_five_champs_with_names, top_two_roles]
		#
		else:
			return {'error' : f'An error occurred getting summoner match history! {summoner_data.status_code}'}

	#Gets ranked solo/duo and flex data given a summoner id
	def get_summoner_ranked_solo_flex_data(summoner_id):
		summoner_ranked_data_url = f'{LeagueAPI.host}/lol/league/v4/entries/by-summoner/{summoner_id}'
		summoner_ranked_data = requests.get(summoner_ranked_data_url, headers = LeagueAPI.headers)
		#Checks if requests for ranked data was successful
		if summoner_ranked_data.status_code == 200:
			ranked_data = []
			#Iterates through each queue of ranked
			for queue in summoner_ranked_data.json():
				queue_data = {}
				#Checks whether the queue is solo/duo or flex and assigns the name and rank to to queue data dictionary
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
			return {'error' : 'An error occurred getting ranked solo/duo and flex data!'}

	def get_summoner_rank_from_queue_id(summoner_id, queue_id):
		summoner_rank = requests.get(f'{LeagueAPI.host}/lol/league/v4/entries/by-summoner/{summoner_id}', headers = LeagueAPI.headers)
		queue_type = ''
		if queue_id == 440:
			queue_type = 'RANKED_FLEX_SR'
		else:
			queue_type = 'RANKED_SOLO_5x5'
		if summoner_rank.status_code == 200:
			for queue in summoner_rank.json():
				if queue['queueType'] == queue_type:
					win_rate = round((queue['wins'] / (queue['wins'] + queue['losses'])) * 100)
					return {'rank' : queue['tier'].lower(), 'win_rate' : win_rate}
		else:
			return {'error' : 'Error getting ranked data'}

	def get_champ_name_from_id(champ_id: str):
		if LeagueAPI.response_champs.status_code == 200:
			champs = LeagueAPI.response_champs.json()['data']
			for champ_name, value in champs.items():
				for key, val2 in value.items(): 
					if key == 'key' and val2 == champ_id:
						return champ_name
			return "None"

	def get_game_type_from_match_data(match_data):
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
			#print(f'Error getting summoner match data, code: {summoner_live_data.status_code}')
			return 'Error occurred getting mode from queueId'

	def get_description_from_mode(game_mode_in):
		if LeagueAPI.response_game_modes.status_code == 200:
			for game_mode in LeagueAPI.response_game_modes.json():
				if game_mode['gameMode'] == game_mode_in:
					return game_mode['description'][:-6]
		else:
			#print(f'Error getting summoner match data, code: {summoner_live_data.status_code}')
			return 'Error occurred getting description from game mode'

	def get_summoner_mastery_points_for_champion(summoner_id, champ_id):
		mastery_points_response = requests.get(f'{LeagueAPI.host}/lol/champion-mastery/v4/champion-masteries/by-summoner/{summoner_id}/by-champion/{champ_id}', headers = LeagueAPI.headers)
		if mastery_points_response.status_code == 200:
			return mastery_points_response.json()['championPoints']
		else:
			return 0

	#Returns dictionary containing id, name, and icon url route for a given perk id
	def get_perk_info_from_id(perk_id):
		if LeagueAPI.response_perks.status_code == 200:
			for perk in LeagueAPI.response_perks.json():
				if int(perk['id']) == int(perk_id):
					perk_path = perk['iconPath'].split('perk-images/')[1]
					return {'perk_id' : perk_id, 'perk_name' : perk['name'], 'perk_icon_url' : perk_path}
		else:
			return {'error' : 'Error getting perk info'}

	def get_summoner_spell_name_from_id(spell_id):
		if LeagueAPI.response_summoner_spells.status_code == 200:
			spells = LeagueAPI.response_summoner_spells.json()
			for spell_name, spell_data_dict in spells['data'].items():
				if spell_data_dict['key'] == str(spell_id):
					return spell_data_dict['id']
					