from PIL import Image, ImageDraw, ImageFont
import requests

class LeagueImageCreator():

	def get_match_image(summoners, bans):
		print(f'{summoners} {bans}')
		img = Image.new('RGBA', (1920, 1080), 'white')
		img.save('./save.png')
		return './save.png'