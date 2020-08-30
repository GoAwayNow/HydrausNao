#!/usr/bin/env python -u
#Let me just preface this by saying "I don't know Python."
#For instance, WTF is that line above this? Is it important? It's commented, but is it an actual comment? Fuck.
#And just what is going on with stdout and stderr below? I read about what all that does, but I can't figure out why.
#The only actual languages I've worked with previously are C++ and Pascal, and both were very limited experiences.
#I've only made anything even remotely complex from scratch with Windows CMD scripts and jQuery userscripts.
#When I do this, I don't know what the hell I'm doing, so the core of this is copied from identify_images_v1.1.py, an example script from SauceNAO.
#Just about everything else in this script is thanks to search engines and online tutorials.

#Necessary Hydrus permissions: Import URLs, Search Files

#This script requires Python 3+, Requests, and Hydrus-API: 'pip install requests' and 'pip install hydrus-api'

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. 
#################CONFIG##################
#In the future, this config should hopefully be external.

saucenao_api_key="!!!REPLACE THIS WITH YOUR API KEY!!!"
hydrus_api_key="!!!REPLACE THIS WITH YOUR API KEY!!!"
hydrus_api_url="http://127.0.0.1:45869/" #This is the default API URL. Adjust as needed.
hydrus_page_name="HydrausNao"
EnableRename=False
minsim='80!'#forcing minsim to 80 is generally safe for complex images, but may miss some edge cases. If images being checked are primarily low detail, such as simple sketches on white paper, increase this to cut down on false positives.
hash_file="hashes.txt"

##############END CONFIG#################
import sys
import os
import io
import unicodedata
import requests
import hydrus
import hydrus.utils
import json
import codecs
import time
from collections import OrderedDict
sys.stdout = codecs.getwriter('utf8')(sys.stdout.detach())
sys.stderr = codecs.getwriter('utf8')(sys.stderr.detach())

hash_input = open(hash_file)

hydrus_permissions = [hydrus.Permission.SearchFiles, hydrus.Permission.ImportURLs]

#enable or disable indexes
index_hmags='0'
index_reserved='0'
index_hcg='0'
index_ddbobjects='0'
index_ddbsamples='0'
index_pixiv='1'
index_pixivhistorical='1'
index_reserved='0'
index_seigaillust='0'
index_danbooru='1'
index_drawr='1'
index_nijie='1'
index_yandere='0'
index_animeop='0'
index_reserved='0'
index_shutterstock='0'
index_fakku='0'
index_hmisc='0'
index_2dmarket='0'
index_medibang='0'
index_anime='0'
index_hanime='0'
index_movies='0'
index_shows='0'
index_gelbooru='1'
index_konachan='1'
index_sankaku='1'
index_animepictures='0'
index_e621='1'
index_idolcomplex='0'
index_bcyillust='0'
index_bcycosplay='0'
index_portalgraphics='0'
index_da='1'
index_pawoo='0'
index_madokami='0'
index_mangadex='0'

#generate appropriate bitmask
db_bitmask = int(index_mangadex+index_madokami+index_pawoo+index_da+index_portalgraphics+index_bcycosplay+index_bcyillust+index_idolcomplex+index_e621+index_animepictures+index_sankaku+index_konachan+index_gelbooru+index_shows+index_movies+index_hanime+index_anime+index_medibang+index_2dmarket+index_hmisc+index_fakku+index_shutterstock+index_reserved+index_animeop+index_yandere+index_nijie+index_drawr+index_danbooru+index_seigaillust+index_anime+index_pixivhistorical+index_pixiv+index_ddbsamples+index_ddbobjects+index_hcg+index_hanime+index_hmags,2)
print("dbmask="+str(db_bitmask))
#encoded print - handle random crap
def printe(line):
    print(str(line).encode(sys.getdefaultencoding(), 'replace')) #ignore or replace
	
client = hydrus.Client(hydrus_api_key, hydrus_api_url)
	
if not hydrus.utils.verify_permissions(client, hydrus_permissions):
	print("The Hydrus API key does not grant all required permissions:", hydrus_permissions)
	sys.exit(1)

	
for line in hash_input:
	thumbnail = client.get_thumbnail(hash_=line)
	#file = open("fileout", "wb")
	#file.write(thumbnail.content)
	url = 'http://saucenao.com/search.php?output_type=2&numres=1&minsim='+minsim+'&dbmask='+str(db_bitmask)+'&api_key='+saucenao_api_key
	thumb_data = {'file': thumbnail.content}
	print("Processing hash: "+str(line).rstrip(), flush=True)
	
	processResults = True
	while True:
		r = requests.post(url, files=thumb_data)
		if r.status_code != 200:
			if r.status_code == 403:
				print('Incorrect or Invalid API Key! Please Edit Script to Configure...')
				sys.exit(2)
			else:
				#generally non 200 statuses are due to either overloaded servers or the user is out of searches
				print("status code: "+str(r.status_code))
				time.sleep(10)
		else:
			results = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(r.text)
			if int(results['header']['user_id'])>0:
				#api responded
				print('Remaining Searches 30s|24h: '+str(results['header']['short_remaining'])+'|'+str(results['header']['long_remaining']), flush=True)
				if int(results['header']['status'])==0:
					#search succeeded for all indexes, results usable
					break
				else:
					if int(results['header']['status'])>0:
						#One or more indexes are having an issue.
						#This search is considered partially successful, even if all indexes failed, so is still counted against your limit.
						#The error may be transient, but because we don't want to waste searches, allow time for recovery.
						print('API Error. Retrying in 600 seconds...', flush=True)
						time.sleep(600)
					else:
						#Problem with search as submitted, bad image, or impossible request.
						#Issue is unclear, so don't flood requests.
						print('Bad image or other request error. Skipping in 10 seconds...', flush=True)
						processResults = False
						time.sleep(10)
						break
			else:
				#General issue, api did not respond. Normal site took over for this error state.
				#Issue is unclear, so don't flood requests.
				print('Bad image, or API failure. Skipping in 10 seconds...', flush=True)
				processResults = False
				time.sleep(10)
				break
	
	if processResults:
		#print(results)
		
		if int(results['header']['results_returned']) > 0:
			#one or more results were returned
			if float(results['results'][0]['header']['similarity']) > float(results['header']['minimum_similarity']):
				print('hit! '+str(results['results'][0]['header']['similarity']), flush=True)
				file_url=results['results'][0]['data']['ext_urls'][0]
				
				client.add_url(url=file_url, page_name=hydrus_page_name)
				
			else:
				print('miss... '+str(results['results'][0]['header']['similarity']), flush=True)
				
		else:
			print('no results... ;_;')

		if int(results['header']['long_remaining'])<1: #could potentially be negative
			print('Out of searches for today. Sleeping for 6 hours...', flush=True)
			time.sleep(6*60*60)
		if int(results['header']['short_remaining'])<1:
			print('Out of searches for this 30 second period. Sleeping for 25 seconds...', flush=True)
			time.sleep(25)			
		print("")
	
print('All Done!')
