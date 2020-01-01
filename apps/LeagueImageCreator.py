from PIL import Image, ImageDraw, ImageFont
import requests

class LeagueImageCreator():

	perk_host = 'http://ddragon.leagueoflegends.com/cdn/img/perk-images/'
	summoner_spell_host = 'http://ddragon.leagueoflegends.com/cdn/9.24.2/img/spell/'

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
		