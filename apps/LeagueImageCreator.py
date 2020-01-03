from PIL import Image, ImageDraw, ImageFont
import requests

class LeagueImageCreator():

	perk_host = 'http://ddragon.leagueoflegends.com/cdn/img/perk-images/'
	summoner_spell_host = 'http://ddragon.leagueoflegends.com/cdn/9.24.2/img/spell/'
	ranked_crest_host = 'http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/content/src/leagueclient/rankedcrests/'

	def get_summoner_card(summoner_card_data):
		img = Image.new('RGBA', (576, 1024), (255, 255, 0, 0))
		#Check if font folder is available
		try: 
			font_summoner_name = ImageFont.truetype('staticdata/open-sans/OpenSans-Regular.ttf', 32)
			font_summoner_data_headings = ImageFont.truetype('staticdata/open-sans/OpenSans-Bold.ttf', 26)
			font_summoner_data_rank = ImageFont.truetype('staticdata/open-sans/OpenSans-Bold.ttf', 24)
			font_summoner_data_subtext = ImageFont.truetype('staticdata/open-sans/OpenSans-Bold.ttf', 20)
		except:
			font_summoner_name = ImageFont.load_default()
			font_summoner_data_headings = ImageFont.load_default()
			font_summoner_data_rank = ImageFont.load_default()
			font_summoner_data_subtext = ImageFont.load_default()
		#Adds background banner to img
		banner_img_response = requests.get('http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/regalia/banners/backgrounds/solidbanner_still.png', stream=True)
		if banner_img_response.status_code == 200:
			banner_img = Image.open(banner_img_response.raw)
			banner_img = banner_img.resize((576, 1923))
			banner_img = banner_img.crop((0, 899, 576, 1923))
			img.paste(banner_img, (0, 0))
		#Adds banner trim to img
		if summoner_card_data['rank_data']:
			summoner_rank_data = summoner_card_data['rank_data']
			rank_to_use_for_border = LeagueImageCreator.get_rank_with_prio_to_solo_queue(summoner_rank_data)
			rank_and_div = rank_to_use_for_border['rank']
			rank_and_div_list = rank_and_div.split(' ')
			rank = rank_and_div_list[0].lower() if rank_and_div_list[0] != 'PLATINUM' else 'plat'
			trim_url = f'http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/regalia/banners/trims/trim_{rank}.png'
			trim_response = requests.get(trim_url, stream=True)
			if trim_response.status_code == 200:
				trim_img = Image.open(trim_response.raw)
				trim_img = trim_img.resize((576, 288))
				img.paste(trim_img, (0, 736), trim_img.convert('RGBA'))
		#Adds icon with crest and profile icon of summoner
		summoner_icon_img = LeagueImageCreator.get_summoner_icon_with_crest(summoner_card_data)
		img.paste(summoner_icon_img, (140, 0), summoner_icon_img.convert('RGBA'))
		#Adds summoner name to img
		summoner_name = summoner_card_data['summoner_name']
		summoner_name_font_place = (img.size[0] / 2) - (font_summoner_name.getsize(summoner_name)[0] / 2)
		name_text = ImageDraw.Draw(img)
		name_text.text((summoner_name_font_place, 284), summoner_name, fill='#ffe553', align='center', font=font_summoner_name)
		#Add ranked data text
		solo_center_coords = 172
		flex_center_coords = 404
		solo_labels = ['Ranked Solo/Duo', 'N/A', 'N/A']
		solo_label_coord = solo_center_coords - (font_summoner_data_headings.getsize(solo_labels[0])[0] / 2)
		solo_label_text = ImageDraw.Draw(img)
		solo_label_text.text((solo_label_coord, 362), solo_labels[0], fill='#d3d3d3', align='center', font=font_summoner_data_headings)
		flex_labels = ['Ranked Flex', 'N/A', 'N/A']
		flex_label_coord = flex_center_coords - (font_summoner_data_headings.getsize(flex_labels[0])[0] / 2)
		flex_label_text = ImageDraw.Draw(img)
		flex_label_text.text((flex_label_coord, 362), flex_labels[0], fill='#d3d3d3', align='center', font=font_summoner_data_headings)
		for rank in summoner_card_data['rank_data']:
			if rank['queue'] == 'Ranked Solo/Duo':
				solo_labels[1] = rank['rank']
				solo_labels[2] = f'{rank["games_played"]} ({rank["win_rate"]}%)'
			elif rank['queue'] == 'Ranked Flex':
				flex_labels[1] = rank['rank']
				flex_labels[2] = f'{rank["games_played"]} ({rank["win_rate"]}%)'
		solo_rank_coord = solo_center_coords - (font_summoner_data_headings.getsize(solo_labels[1])[0] / 2)
		solo_rank_text = ImageDraw.Draw(img)
		solo_rank_text.text((solo_rank_coord, 405), solo_labels[1], fill='#15EBFF', align='center', font=font_summoner_data_rank)
		solo_win_rate_coord = solo_center_coords - (font_summoner_data_headings.getsize(solo_labels[2])[0] / 2)
		solo_win_rate_text = ImageDraw.Draw(img)
		solo_win_rate_text.text((solo_win_rate_coord, 442), solo_labels[2], fill='#15EBFF', align='center', font=font_summoner_data_rank)
		flex_rank_coord = flex_center_coords - (font_summoner_data_headings.getsize(flex_labels[1])[0] / 2)
		flex_rank_text = ImageDraw.Draw(img)
		flex_rank_text.text((flex_rank_coord, 405), flex_labels[1], fill='#15EBFF', align='center', font=font_summoner_data_rank)
		flex_win_rate_coord = flex_center_coords - (font_summoner_data_headings.getsize(flex_labels[2])[0] / 2)
		flex_win_rate_text = ImageDraw.Draw(img)
		flex_win_rate_text.text((flex_win_rate_coord, 442), flex_labels[2], fill='#15EBFF', align='center', font=font_summoner_data_rank)
		#Add 'Top Champions:' text
		top_champs_label = 'Top Champions(Pick Rate):'
		top_champs_font_place = (img.size[0] / 2) - (font_summoner_data_headings.getsize(top_champs_label)[0] / 2)
		top_champs_text = ImageDraw.Draw(img)
		top_champs_text.text((top_champs_font_place, 499), top_champs_label, fill='#D3D3D3', align='center', font=font_summoner_data_headings)
		#Add top champs played
		champs_played_coords = 48
		for champ, pick_rate in summoner_card_data['most_played_champs'].items():
			#Adds champion image to banner image
			champ_response = requests.get(f'http://ddragon.leagueoflegends.com/cdn/9.24.2/img/champion/{champ}.png', stream=True)
			if champ_response.status_code == 200:
				champ_img = Image.open(champ_response.raw)
				champ_img = champ_img.resize((64, 64))
				img.paste(champ_img, (champs_played_coords, 556))
				pick_rate_label = f'{pick_rate}%'
				pick_rate_font_place = champs_played_coords + ((champ_img.size[0] / 2) - (font_summoner_data_subtext.getsize(pick_rate_label)[0] / 2))
				pick_rate_text = ImageDraw.Draw(img)
				pick_rate_text.text((pick_rate_font_place, 628), pick_rate_label, fill='#D3D3D3', align='center', font=font_summoner_data_subtext)
				champs_played_coords += 105
		#Add 'Top Roles:' text
		top_roles_label = 'Top Roles(Pick Rate):'
		top_roles_font_place = (img.size[0] / 2) - (font_summoner_data_headings.getsize(top_roles_label)[0] / 2)
		top_roles_text = ImageDraw.Draw(img)
		top_roles_text.text((top_roles_font_place, 664), top_roles_label, fill='#D3D3D3', align='center', font=font_summoner_data_headings)
		#Add top roles played
		role_played_x_coords = 89
		role_played_y_coords = 724
		for role, pick_rate in summoner_card_data['most_played_roles'].items():
			role_str = LeagueImageCreator.get_role_str(role)
			role_url = f'http://raw.communitydragon.org/latest/plugins/rcp-fe-lol-career-stats/global/default/position_{role_str}.png'
			role_response = requests.get(role_url, stream=True)
			if role_response.status_code == 200:
				role_img = Image.open(role_response.raw)
				role_img = role_img.resize((62, 62))
				img.paste(role_img, (role_played_x_coords, role_played_y_coords), role_img.convert('RGBA'))
				role_played_x_coords += 84
				pick_rate_label = f'{pick_rate}%'
				pick_rate_y_font_place = role_played_y_coords + ((role_img.size[1] / 2) - (font_summoner_data_subtext.getsize(pick_rate_label)[1] / 2))
				pick_rate_text = ImageDraw.Draw(img)
				pick_rate_text.text((role_played_x_coords, pick_rate_y_font_place), pick_rate_label, fill='#D3D3D3', align='center', font=font_summoner_data_subtext)
				role_played_x_coords += 187
		img.save(f'./imgs/{summoner_card_data["summoner_name"]}.png')
		return f'./imgs/{summoner_card_data["summoner_name"]}.png'

	def get_summoner_icon_with_crest(summoner_card_data):
		summoner_crest_icon_img = Image.new('RGBA', (296,338), (255, 255, 0, 0))
		summoner_icon = summoner_card_data['summoner_icon']
		summoner_icon_response = requests.get(f'http://ddragon.leagueoflegends.com/cdn/9.24.2/img/profileicon/{summoner_icon}.png', stream=True)
		if summoner_icon_response.status_code == 200:
			icon_img = Image.open(summoner_icon_response.raw)
			icon_img = icon_img.resize((152, 152))
			#Circular mask
			round_icon = Image.new('RGBA', (152, 152), (255, 255, 0, 0))
			draw = ImageDraw.Draw(round_icon)
			draw.ellipse((0,0) + (152, 152), fill=(255,255,255,255))
			round_icon.paste(icon_img, (0,0), round_icon)
			summoner_crest_icon_img.paste(round_icon, (72, 93))
			#If rank data exists, add ranked crest to icon
			if summoner_card_data['rank_data']:
				summoner_rank_data = summoner_card_data['rank_data']
				rank_to_use_for_border = LeagueImageCreator.get_rank_with_prio_to_solo_queue(summoner_rank_data)
				rank_and_div = rank_to_use_for_border['rank']
				rank_and_div_list = rank_and_div.split(' ')
				rank = rank_and_div_list[0].lower()
				rank_num = LeagueImageCreator.get_matching_num_for_rank(rank_and_div_list[0])
				#Base Crest image
				base_crest_url = f'{LeagueImageCreator.ranked_crest_host}{rank_num}_{rank}/images/{rank}_base.png'
				base_crest_response = requests.get(base_crest_url, stream=True)
				if base_crest_response.status_code == 200:
					base_crest_img = Image.open(base_crest_response.raw)
					base_crest_img = base_crest_img.resize((296, 338))
					summoner_crest_icon_img.paste(base_crest_img, (0, 0), base_crest_img.convert('RGBA'))
				#Crown image
				division = LeagueImageCreator.get_arabic_from_roman_num(rank_and_div_list[1])
				division_path = f'_d{division}' if int(rank_num) < 7 else ''
				crown_crest_url = f'{LeagueImageCreator.ranked_crest_host}{rank_num}_{rank}/images/{rank}_crown{division_path}.png'
				crown_crest_response = requests.get(crown_crest_url, stream=True)
				if crown_crest_response.status_code == 200:
					crown_crest_img = Image.open(crown_crest_response.raw)
					crown_crest_img = crown_crest_img.resize((296, 338))
					summoner_crest_icon_img.paste(crown_crest_img, (0, 0), crown_crest_img.convert('RGBA'))
				summoner_crest_icon_img = summoner_crest_icon_img.crop(((0, 35, summoner_crest_icon_img.size[0], summoner_crest_icon_img.size[1])))
		return summoner_crest_icon_img

	def get_rank_with_prio_to_solo_queue(rank_data):
		for queue_rank in rank_data:
			if queue_rank['queue'] == 'Ranked Solo/Duo':
				return queue_rank
		return rank_data[0]

	def get_matching_num_for_rank(rank):
		switcher = {
			'IRON': '01',
			'BRONZE' : '02',
			'SILVER': '03',
			'GOLD': '04',
			'PLATINUM': '05',
			'DIAMOND': '06',
			'MASTER': '07',
			'GRANDMASTER': '08',
			'CHALLENGER': '09'
		}
		return switcher.get(rank)

	def get_arabic_from_roman_num(roman_num):
		switcher = {
			'I': '1',
			'II': '2',
			'III': '3',
			'IV': '4'
		}
		return switcher.get(roman_num)

	def get_role_str(role):
		switcher = {
			'TOP': 'top',
			'JUNGLE' : 'jungle',
			'MID': 'mid',
			'DUO_CARRY': 'bottom',
			'DUO_SUPPORT': 'support'
		}
		return switcher.get(role)

	def get_match_image(game_id, summoners, bans):
		#Check if response of background image is valid
		back_img_response = requests.get('http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/content/src/leagueclient/gamemodeassets/classic_sru/img/champ-select-planning-intro.jpg', stream=True)
		if back_img_response.status_code == 200:
			img = Image.open(back_img_response.raw)
			img = img.resize((1920, 1080))
			blue_img_coords = 140
			red_img_coords = 140
			#Iterates through each summoner in dictionary, calls for creation of banner image for each summoner, and adds banner image to match image
			for summoner in summoners:
				summoner_img = LeagueImageCreator.get_summoner_image_for_live_game(summoner)
				if summoner['team'] == 100:
					img.paste(summoner_img, (blue_img_coords, 0), summoner_img.convert('RGBA'))
					blue_img_coords += 348
				else:
					img.paste(summoner_img, (red_img_coords, 575), summoner_img.convert('RGBA'))
					red_img_coords += 348
			img.save(f'./imgs/{game_id}.png')
		return f'./imgs/{game_id}.png'

	#Create a banner image of summoner data for live game image
	def get_summoner_image_for_live_game(summoner):
		summoner_name = summoner['name']
		champ = summoner['champ_name']
		mastery = summoner['mastery_points']
		rank_data = summoner['rank_data']
		color = '#00c4ff' if summoner['team'] == 100 else '#ff0000'
		img = Image.new('RGBA', (248, 505), (255, 255, 0, 0))
		#Check if font folder is available
		try: 
			font_summoner_name = ImageFont.truetype('staticdata/open-sans/OpenSans-Regular.ttf', 28)
			font_summoner_data = ImageFont.truetype('staticdata/open-sans/OpenSans-Bold.ttf', 18)
		except:
			font_summoner_name = ImageFont.load_default()
			font_summoner_data = ImageFont.load_default()
		#Check if response of background banner is valid
		banner_img_response = requests.get('http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/regalia/banners/backgrounds/solidbanner_still.png', stream=True)
		if banner_img_response.status_code == 200:
			banner_img = Image.open(banner_img_response.raw)
			banner_img = banner_img.resize((248, 828))
			banner_img = banner_img.crop((0, 323, banner_img.size[0], 828))
			img.paste(banner_img, (0, 0))
		#Check if response of trim for summoner's rank is valid
		if summoner['rank_data']:
			summoner_rank = summoner['rank_data']['rank'] if summoner['rank_data']['rank'] != 'platinum' else 'plat'
			trim_response = requests.get(f'http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/regalia/banners/trims/trim_{summoner_rank}.png', stream=True)
			if trim_response.status_code == 200:
				trim_img = Image.open(trim_response.raw)
				trim_img = trim_img.resize((248, 124))
				img.paste(trim_img, (0, 381), trim_img.convert('RGBA'))
		#Adds summoner name to banner image
		summoner_font_place = (img.size[0] / 2) - (font_summoner_name.getsize(summoner_name)[0] / 2)
		text = ImageDraw.Draw(img)
		text.text((summoner_font_place, 10), summoner_name, fill=color, align='center', font=font_summoner_name)
		#Adds champion image to banner image
		champ_response = requests.get(f'http://ddragon.leagueoflegends.com/cdn/9.24.2/img/champion/{champ}.png', stream=True)
		if champ_response.status_code == 200:
			champ_img = Image.open(champ_response.raw)
			champ_img = champ_img.resize((127, 127))
			img.paste(champ_img, (61, 54))
		#Adds Mastery Points label and data to image
		mastery_title_text = ImageDraw.Draw(img)
		mastery_title_text.text((32, 200), 'Mastery:', fill='#FFE553', align='center', font=font_summoner_data)
		mastery_data_text = ImageDraw.Draw(img)
		mastery_font_place = 185 - (font_summoner_data.getsize(f'{mastery}')[0] / 2)
		mastery_data_text.text((mastery_font_place, 200), f'{mastery}', fill='#D3D3D3', align='center', font=font_summoner_data)
		#Adds Winrate label and data to image
		win_rate = f'{summoner["rank_data"]["win_rate"]}%' if summoner["rank_data"] else 'N/A'
		win_rate_title_text = ImageDraw.Draw(img)
		win_rate_title_text.text((32, 239), 'Winrate:', fill='#FFE553', align='center', font=font_summoner_data)
		win_rate_data_text = ImageDraw.Draw(img)
		win_rate_font_place = 185 - (font_summoner_data.getsize(win_rate)[0] / 2)
		win_rate_data_text.text((win_rate_font_place, 239), win_rate, fill='#D3D3D3', align='center', font=font_summoner_data)
		perks = summoner['perks']
		#Adds main tree perks into banner image
		first_row_perks_coords = 26
		for x in range(4):
			perk_url = perks[x]['perk_icon_url']
			perk_response = requests.get(f'{LeagueImageCreator.perk_host}{perk_url}', stream=True)
			if perk_response.status_code == 200:
				perk_img = Image.open(perk_response.raw)
				perk_img = perk_img.resize((37, 37))
				img.paste(perk_img, (first_row_perks_coords, 284), perk_img.convert('RGBA'))
				first_row_perks_coords += 53
		#Adds two subtree perks into banner image
		second_row_perks_coords = 26
		for x in range(4, 6):
			perk_url = perks[x]['perk_icon_url']
			perk_response = requests.get(f'{LeagueImageCreator.perk_host}{perk_url}', stream=True)
			if perk_response.status_code == 200:
				perk_img = Image.open(perk_response.raw)
				perk_img = perk_img.resize((37, 37))
				img.paste(perk_img, (second_row_perks_coords, 326), perk_img.convert('RGBA'))
				second_row_perks_coords += 53
		#Adds three stat perks into banner image
		second_row_rune_coords = 130
		for x in range(6, 9):
			perk_url = perks[x]['perk_icon_url']
			perk_response = requests.get(f'{LeagueImageCreator.perk_host}{perk_url}', stream=True)
			if perk_response.status_code == 200:
				perk_img = Image.open(perk_response.raw)
				perk_img = perk_img.resize((24, 24))
				img.paste(perk_img, (second_row_rune_coords, 333), perk_img.convert('RGBA'))
				second_row_rune_coords += 33
		#Adds first summoner spell image to banner image
		summoner_spell_1_response = requests.get(f'{LeagueImageCreator.summoner_spell_host}{summoner["spell_1"]}.png', stream=True)
		if summoner_spell_1_response.status_code == 200:
			summoner_spell_img = Image.open(summoner_spell_1_response.raw)
			summoner_spell_img = summoner_spell_img.resize((37, 37))
			img.paste(summoner_spell_img, (79, 369), summoner_spell_img.convert('RGBA'))
		#Adds second summoner spell image to banner image
		summoner_spell_2_response = requests.get(f'{LeagueImageCreator.summoner_spell_host}{summoner["spell_2"]}.png', stream=True)
		if summoner_spell_2_response.status_code == 200:
			summoner_spell_img = Image.open(summoner_spell_2_response.raw)
			summoner_spell_img = summoner_spell_img.resize((37, 37))
			img.paste(summoner_spell_img, (132, 369), summoner_spell_img.convert('RGBA'))
		return img
		