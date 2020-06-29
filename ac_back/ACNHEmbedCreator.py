import discord

class ACNHEmbedCreator():

	def create_fish_embed(fish_data):
		#Discord Embed
		embed = discord.Embed()
		#Fish name in 4 languages
		name_en = fish_data['name']['name-USen'].capitalize()
		name_es = fish_data['name']['name-EUes'].capitalize()
		name_cn = fish_data['name']['name-CNzh']
		name_kr = fish_data['name']['name-KRko']
		embed.title = f'{name_en}/{name_es}/{name_cn}/{name_kr}'
		#Color of embed
		embed.colour = 0x00C8FF
		#Embed thumbnail with picture of fish
		embed.set_thumbnail(url=fish_data['image_uri'])
		#Availability text
		month_avail_out = fish_data['availability']['month-northern'] if fish_data['availability']['isAllYear'] == False else 'All Year'
		time = fish_data['availability']['time'] if fish_data['availability']['isAllDay'] == False else 'All Day'
		location = fish_data['availability']['location']
		rarity = fish_data['availability']['rarity']
		avail_value = f'Months: {month_avail_out}\n Time: {time}\n Location: {location}\n Rarity: {rarity}'
		embed.add_field(name='Availablity', value=avail_value)
		#Shadow
		embed.add_field(name='Shadow', value=fish_data['shadow'].split(' ')[0])
		#Price
		price = f'Regular: {fish_data["price"]} \n CJ: {fish_data["price-cj"]}'
		embed.add_field(name='Price', value=price, inline=False)
		return embed

	def create_bug_embed(bug_data):
		#Discord Embed
		embed = discord.Embed()
		#Bug name in 4 languages
		name_en = bug_data['name']['name-USen'].capitalize()
		name_es = bug_data['name']['name-EUes'].capitalize()
		name_cn = bug_data['name']['name-CNzh']
		name_kr = bug_data['name']['name-KRko']
		embed.title = f'{name_en}/{name_es}/{name_cn}/{name_kr}'
		#Color of embed
		embed.colour = 0x00D13B
		#Embed thumbnail with picture of bug
		embed.set_thumbnail(url=bug_data['image_uri'])
		#Availability text
		month_avail_out = bug_data['availability']['month-northern'] if bug_data['availability']['isAllYear'] == False else 'All Year'
		time = bug_data['availability']['time'] if bug_data['availability']['isAllDay'] == False else 'All Day'
		location = bug_data['availability']['location']
		rarity = bug_data['availability']['rarity']
		avail_value = f'Months: {month_avail_out}\n Time: {time}\n Location: {location}\n Rarity: {rarity}'
		embed.add_field(name='Availablity', value=avail_value)
		#Price
		price = f'Regular: {bug_data["price"]} \n Flick: {bug_data["price-flick"]}'
		embed.add_field(name='Price', value=price)
		return embed

	def create_fossil_embed(fossil_data):
		#Discord Embed
		embed = discord.Embed()
		#Fossil name in 4 languages
		name_en = fossil_data['name']['name-USen'].capitalize()
		name_es = fossil_data['name']['name-EUes'].capitalize()
		name_cn = fossil_data['name']['name-CNzh']
		name_kr = fossil_data['name']['name-KRko']
		embed.title = f'{name_en}/{name_es}/{name_cn}/{name_kr}'
		#Color of embed
		embed.colour = 0xB06100
		#Embed thumbnail with picture of Fossil
		embed.set_thumbnail(url=fossil_data['image_uri'])
		#Price
		price = f'Regular: {fossil_data["price"]}'
		embed.add_field(name='Price', value=price)
		return embed