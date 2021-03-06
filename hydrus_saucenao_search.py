#!/usr/bin/env python -u

#Let me just preface this by saying "I don't know Python."
#The only actual languages I've worked with previously are C++ and Pascal, and both were very limited experiences.
#I've only made anything even remotely complex from scratch with Windows CMD scripts and jQuery userscripts.
#When I do this, I don't know what I'm doing, so the core of this is copied from identify_images_v1.1.py, an example script from SauceNAO.
#Just about everything else in this script is thanks to search engines and online tutorials.

#Necessary Hydrus permissions: Import URLs, Search Files
# Add Tags is also required if tagging is enabled

#This script requires Python 3+, Requests, and Hydrus-API: 'pip install requests' and 'pip install hydrus-api'

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. 

import sys
import os
import io
import unicodedata
import requests
import hydrus
import hydrus.utils
from saucenao_api import SauceNao, errors
import codecs
import time
import configparser
from collections import OrderedDict
sys.stdout = codecs.getwriter('utf8')(sys.stdout.detach())
sys.stderr = codecs.getwriter('utf8')(sys.stderr.detach())

config = configparser.ConfigParser()
try:
	config.read_file(open("config_default.ini"))
except FileNotFoundError:
	print("config_default.ini not found!\nGenerating default configuration...")
	config["General"] = {"hash_file": "hashes.txt"}
	config["Hydrus"] = {"api_key": "", "api_url": "http://127.0.0.1:45869/", "results_Page_Name": "HydrausNao"}
	config["Hydrus_Meta_Tags"] = {"enable": "1", "namespace": "hydrausnao", "hit": "hit", "miss": "miss", "no_result": "no_result"}
	config["SauceNao"] = {"api_key": "", "minsim": "80!"}
	config["SauceNao_Indexes"] = {"hmags": "0",
		"imdb": "0",
		"hcg": "0",
		"ddbobjects": "0",
		"ddbsamples": "0",
		"pixiv": "1",
		"pixivhistorical": "0",
		"seigaillust": "0",
		"danbooru": "1",
		"drawr": "0",
		"nijie": "1",
		"yandere": "1",
		"animeop": "0",
		"shutterstock": "0",
		"fakku": "0",
		"nhentai": "0",
		"2dmarket": "0",
		"medibang": "0",
		"anime": "0",
		"hanime": "0",
		"movies": "0",
		"shows": "0",
		"gelbooru": "1",
		"konachan": "1",
		"sankaku": "1",
		"animepictures": "0",
		"e621": "1",
		"idolcomplex": "0",
		"bcyillust": "0",
		"bcycosplay": "0",
		"portalgraphics": "0",
		"da": "0",
		"pawoo": "0",
		"madokami": "0",
		"mangadex": "0",
		"ehentai": "0",
		"artstation": "0",
		"furaffinity": "0",
		"twitter": "1",
		"furrynetwork": "0"}
	with open("config_default.ini", "w") as defconfigfile:
		config.write(defconfigfile)
	#print("Please edit config.ini before running this script again.")
finally:
	config.read('config.ini')
	#general
	hash_file = config['General']['hash_file']
	#hydrus
	hydrus_api_key = config['Hydrus']['api_key']
	hydrus_api_url = config['Hydrus']['api_url']
	hydrus_page_name = config['Hydrus']['results_page_name']
	#hydrus_meta_tags
	meta_enable_tags = config['Hydrus_Meta_Tags'].getboolean('enable')
	meta_tag_namespace = config['Hydrus_Meta_Tags']['namespace']
	meta_tag_hit = config['Hydrus_Meta_Tags']['hit']
	meta_tag_miss = config['Hydrus_Meta_Tags']['miss']
	meta_tag_noresult = config['Hydrus_Meta_Tags']['no_result']
	meta_tag_service = config['Hydrus_Meta_Tags'].get('service', 'my tags')
	#saucenao
	saucenao_api_key = config['SauceNao']['api_key']
	minsim = config['SauceNao']['minsim']
	#saucenao_indexes
	index_hmags = config['SauceNao_Indexes']['hmags']
	index_imdb = config['SauceNao_Indexes']['imdb']
	index_hcg = config['SauceNao_Indexes']['hcg']
	index_ddbobjects = config['SauceNao_Indexes']['ddbobjects']
	index_ddbsamples = config['SauceNao_Indexes']['ddbsamples']
	index_pixiv = config['SauceNao_Indexes']['pixiv']
	index_pixivhistorical = config['SauceNao_Indexes']['pixivhistorical']
	index_seigaillust = config['SauceNao_Indexes']['seigaillust']
	index_danbooru = config['SauceNao_Indexes']['danbooru']
	index_drawr = config['SauceNao_Indexes']['drawr']
	index_nijie = config['SauceNao_Indexes']['nijie']
	index_yandere = config['SauceNao_Indexes']['yandere']
	index_animeop = config['SauceNao_Indexes']['animeop']
	index_shutterstock = config['SauceNao_Indexes']['shutterstock']
	index_fakku = config['SauceNao_Indexes']['fakku']
	index_hmisc = config['SauceNao_Indexes']['nhentai']
	index_2dmarket = config['SauceNao_Indexes']['2dmarket']
	index_medibang = config['SauceNao_Indexes']['medibang']
	index_anime = config['SauceNao_Indexes']['anime']
	index_hanime = config['SauceNao_Indexes']['hanime']
	index_movies = config['SauceNao_Indexes']['movies']
	index_shows = config['SauceNao_Indexes']['shows']
	index_gelbooru = config['SauceNao_Indexes']['gelbooru']
	index_konachan = config['SauceNao_Indexes']['konachan']
	index_sankaku = config['SauceNao_Indexes']['sankaku']
	index_animepictures = config['SauceNao_Indexes']['animepictures']
	index_e621 = config['SauceNao_Indexes']['e621']
	index_idolcomplex = config['SauceNao_Indexes']['idolcomplex']
	index_bcyillust = config['SauceNao_Indexes']['bcyillust']
	index_bcycosplay = config['SauceNao_Indexes']['bcycosplay']
	index_portalgraphics = config['SauceNao_Indexes']['portalgraphics']
	index_da = config['SauceNao_Indexes']['da']
	index_pawoo = config['SauceNao_Indexes']['pawoo']
	index_madokami = config['SauceNao_Indexes']['madokami']
	index_mangadex = config['SauceNao_Indexes']['mangadex']
	index_ehentai = config['SauceNao_Indexes']['ehentai']
	index_artstation = config['SauceNao_Indexes']['artstation']
	index_fa = config['SauceNao_Indexes']['furaffinity']
	index_twitter = config['SauceNao_Indexes']['twitter']
	index_furnet = config['SauceNao_Indexes']['furrynetwork']

try:
	hash_input = open(hash_file)
except FileNotFoundError:
	print("Hash file not found!\n", hash_file, "\nTerminating...")
	sys.exit(4)
	
if not hydrus_api_key  or not saucenao_api_key:
	print("One or more API keys missing.")
	try:
		configfile = open("config.ini")
	except FileNotFoundError:
		print("Additionally, config.ini was not found.")
		config.remove_section("General")
		config.remove_section("SauceNao_Indexes")
		config["Hydrus"] = {"api_key": ""}
		config["SauceNao"] = {"api_key": ""}
		with open("config.ini", "w") as configfile:
			config.write(configfile)
		print("A default config.ini has been created.")
	print("Please update config.ini before continuing.")
	sys.exit(5)

hydrus_permissions = [hydrus.Permission.SearchFiles, hydrus.Permission.ImportURLs]
if meta_enable_tags:
	hydrus_permissions.append(hydrus.Permission.AddTags)
	
	if meta_tag_namespace:
		if meta_tag_hit:
			hit_tag = meta_tag_namespace+':'+meta_tag_hit
		if meta_tag_miss:
			miss_tag = meta_tag_namespace+':'+meta_tag_miss
		if meta_tag_noresult:
			noresult_tag = meta_tag_namespace+':'+meta_tag_noresult
	else:
		if meta_tag_hit:
			hit_tag = meta_tag_hit
		if meta_tag_miss:
			miss_tag = meta_tag_miss
		if meta_tag_noresult:
			noresult_tag = meta_tag_noresult


#generate appropriate bitmask
db_bitmask = int(index_furnet+index_twitter+index_fa+index_artstation+index_ehentai+index_mangadex+index_madokami+index_pawoo+index_da+index_portalgraphics+index_bcycosplay+index_bcyillust+index_idolcomplex+index_e621+index_animepictures+index_sankaku+index_konachan+index_gelbooru+index_shows+index_movies+index_hanime+index_anime+index_medibang+index_2dmarket+index_hmisc+index_fakku+index_shutterstock+index_imdb+index_animeop+index_yandere+index_nijie+index_drawr+index_danbooru+index_seigaillust+index_anime+index_pixivhistorical+index_pixiv+index_ddbsamples+index_ddbobjects+index_hcg+index_hanime+index_hmags,2)
print("dbmask="+str(db_bitmask))
#encoded print - handle random crap
def printe(line):
    print(str(line).encode(sys.getdefaultencoding(), 'replace')) #ignore or replace
	
sauce = SauceNao(api_key=saucenao_api_key,
				dbmask=db_bitmask,
				numres=1,
)
	
client = hydrus.Client(hydrus_api_key, hydrus_api_url)

try:
	p = hydrus.utils.verify_permissions(client, hydrus_permissions)
except:
	print("Hydrus-API encountered a server error.\nHydrus API key may be malformed.")
	sys.exit(6)
else:
	if not hydrus.utils.verify_permissions(client, hydrus_permissions):
		print("The Hydrus API key does not grant all required permissions:", hydrus_permissions)
		sys.exit(1)

short_pause = False

for line in hash_input:
	if short_pause:
		print('Out of searches for this 30 second period. Sleeping for 30 seconds...', flush=True)
		time.sleep(30)
	short_pause = False
	thumbnail = client.get_thumbnail(hash_=line)
	print("Processing hash: "+str(line).rstrip(), flush=True)
	
	retries = 0
	while True:
		try:
			results = sauce.from_file(thumbnail.content)
		except errors.ShortLimitReachedError as e:
			print(str(e)+". Retrying in 2 minutes...", flush=True)
			time.sleep(2*60)
			continue
		except errors.LongLimitReachedError as e:
			print(str(e)+". Retrying in 24 hours...", flush=True)
			time.sleep(24*60*60)
			continue
		except errors.UnknownClientError as e:
			sys.exit(str(e))
		except errors.UnknownServerError as e:
			sys.exit(str(e))
		except errors.UnknownApiError as e:
			if retries < 4:
				print(str(e)+". Retrying in 10 minutes...", flush=True)
				retries += 1
				time.sleep(600)
				continue
			else:
				sys.exit(str(e)+". Maximum reties reached.")
		except errors.BadFileSizeError as e:
			print(str(e)+". This should be impossible. Skipping...", flush=True)
			time.sleep(10)
			break
		else:
			if results:
				if results[0].similarity > float(minsim.strip('!')):
					print('hit! '+str(results[0].similarity), flush=True)
					if meta_enable_tags and meta_tag_hit:
						client.add_tags(hashes=line.splitlines(), service_to_tags={meta_tag_service: [hit_tag]})
					client.add_url(url=results[0].urls[0], page_name=hydrus_page_name)
				else:
					print('miss... '+str(results[0].similarity), flush=True)
					if meta_enable_tags and meta_tag_miss:
						client.add_tags(hashes=line.splitlines(), service_to_tags={meta_tag_service: [miss_tag]})
			else:
				print('no results... ;_;', flush=True)
				if meta_enable_tags and meta_tag_noresult:
					client.add_tags(hashes=line.splitlines(), service_to_tags={meta_tag_service: [noresult_tag]})
			if results.short_remaining < 1:
				short_pause = True
			print("")
			break
	
print('All Done!')
