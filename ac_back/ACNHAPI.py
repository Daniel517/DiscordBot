import requests

class ACNHAPI():

	#Host directory
	host = 'http://acnhapi.com'

	def get_fish_info(fish_name):
		#Fish api url path
		fish_url = f'/v1/fish/{fish_name}'
		#Response from fish api
		fish_response = requests.get(ACNHAPI.host + fish_url)
		if fish_response.status_code == 200:
			return fish_response.json()
		elif fish_response.status_code == 404:
			return {'error' : f'Fish "{fish_name}" not found!'}
		else:
			return {'error' : f'An error occurred getting data on "{fish_name}"!'}
	
	def get_bug_info(bug_name):
		#Bug api url path
		bug_url = f'/v1/bugs/{bug_name}'
		#Response from bug api
		bug_response = requests.get(ACNHAPI.host + bug_url)
		if bug_response.status_code == 200:
			return bug_response.json()
		elif bug_response.status_code == 404:
			return {'error' : f'Bug "{bug_name}" not found!'}
		else:
			return {'error' : f'An error occurred getting data on "{bug_name}"!'}
	
	def get_fossil_info(fossil_name):
		#Fossil api url path
		fossil_url = f'/v1/fossils/{fossil_name}'
		#Response from fossil api
		fossil_response = requests.get(ACNHAPI.host + fossil_url)
		if fossil_response.status_code == 200:
			return fossil_response.json()
		elif fossil_response.status_code == 404:
			return {'error' : f'Fossil "{fossil_name}" not found!'}
		else:
			return {'error' : f'An error occurred getting data on "{fossil_name}"!'}