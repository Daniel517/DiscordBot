from PIL import Image, ImageDraw, ImageFont
import requests

class LeagueImageCreator():

	def get_match_image(game_id, summoners, bans):
		blue_img_coords = 140
		red_img_coords = 140
		#Check if response of background image is valid
		back_img_response = requests.get('http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/content/src/leagueclient/gamemodeassets/classic_sru/img/champ-select-planning-intro.jpg', stream=True)
		if back_img_response.status_code == 200:
			img = Image.open(back_img_response.raw)
			img = img.resize((1920, 1080))
			for summoner in summoners:
				summoner_img = LeagueImageCreator.get_summoner_image_for_live_game(summoner)
				if summoner['team'] == 100:
					img.paste(summoner_img, (blue_img_coords, 0), summoner_img.convert('RGBA'))
					blue_img_coords += 348
				else:
					img.paste(summoner_img, (red_img_coords, 575), summoner_img.convert('RGBA'))
					red_img_coords += 348
			img.save(f'./{game_id}.png')
		return f'./{game_id}.png'

	def get_summoner_image_for_live_game(summoner):
		summoner_name = summoner['name']
		champ = summoner['champ_name']
		mastery = summoner['mastery_points']
		color = '#00c4ff' if summoner['team'] == 100 else '#ff0000'
		img = Image.new('RGBA', (248, 505), (255, 255, 0, 0))
		#Check if font folder is available
		try: 
			font_summoner_name = ImageFont.truetype('open-sans/OpenSans-Regular.ttf', 28)
			font_summoner_data = ImageFont.truetype('open-sans/OpenSans-Regular.ttf', 18)
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
		trim_response = requests.get(f'http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/regalia/banners/trims/trim_{summoner["rank"]}.png', stream=True)
		if trim_response.status_code == 200:
			trim_img = Image.open(trim_response.raw)
			trim_img = trim_img.resize((248, 124))
			img.paste(trim_img, (0, 381), trim_img.convert('RGBA'))
		#Adds summoner name to image
		summoner_font_place = (img.size[0] / 2) - (font_summoner_name.getsize(summoner_name)[0] / 2)
		text = ImageDraw.Draw(img)
		text.text((summoner_font_place, 10), summoner_name, fill=color, align='center', font=font_summoner_name)
		#Get square tile image of champion
		champ_response = requests.get(f'http://ddragon.leagueoflegends.com/cdn/9.24.2/img/champion/{champ}.png', stream=True)
		if champ_response.status_code == 200:
			champ_img = Image.open(champ_response.raw)
			champ_img = champ_img.resize((228, 228))
			img.paste(champ_img, (10, 57))
		#Adds Mastery Points label and data to image
		title_text = ImageDraw.Draw(img)
		title_text.text((30, 293), 'Mastery:', fill='#FFE553', align='center', font=font_summoner_data)
		data_text = ImageDraw.Draw(img)
		data_text.text((150, 293), f'{mastery}', fill='#D3D3D3', align='center', font=font_summoner_data)
		return img