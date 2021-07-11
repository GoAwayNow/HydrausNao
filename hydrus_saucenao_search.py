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
import subprocess
import shutil
import requests
import hydrus
import hydrus.utils
from saucenao_api import SauceNao, errors as SauceNaoErrors
#import codecs
import time
import configparser
#sys.stdout = codecs.getwriter('utf8')(sys.stdout.detach())
#sys.stderr = codecs.getwriter('utf8')(sys.stderr.detach())

results = None

config = configparser.ConfigParser()
try:
    config.read_file(open("config_default.ini"))
except FileNotFoundError:
    print("config_default.ini not found!\nGenerating default configuration...")
    config["DEFAULT"] = {"blacklist_file": ""}
    config["General"] = {"hash_file": "hashes.txt", "test_results": "1"}
    config["Hydrus"] = {"api_key": "", "api_url": "http://127.0.0.1:45869/", "results_Page_Name": "HydrausNao"}
    config["Hydrus_Meta_Tags"] = {"enable": "1", "namespace": "hydrausnao", "hit": "hit", "miss": "miss", "miss_over_minsim": "miss over minsim", "no_result": "no_result"}
    config["SauceNao"] = {"api_key": "", "minsim": "80!", "numres": "2"}
    config["SauceNao_Indexes"] = {"hmags": "0",
        "hcg": "0",
        "pixiv": "1",
        "pixivhistorical": "0",
        "seigaillust": "0",
        "danbooru": "1",
        "drawr": "0",
        "nijie": "1",
        "yandere": "1",
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
        "sankaku": "0",
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
        "twitter": "0",
        "furrynetwork": "0"}
    with open("config_default.ini", "w") as defconfigfile:
        config.write(defconfigfile)
        defconfigfile.close()
    #print("Please edit config.ini before running this script again.")
finally:
    config.read('config.ini')
    #general
    hash_file = config['General']['hash_file']
    verbose_output = config['General'].getboolean('verbose', False)
    gen_test_res = config['General'].getboolean('test_results')
    #hydrus
    hydrus_api_key = config['Hydrus']['api_key']
    hydrus_api_url = config['Hydrus']['api_url']
    hydrus_page_name = config['Hydrus']['results_page_name']
    #hydrus_meta_tags
    meta_enable_tags = config['Hydrus_Meta_Tags'].getboolean('enable')
    meta_tag_namespace = config['Hydrus_Meta_Tags']['namespace']
    meta_tag_hit = config['Hydrus_Meta_Tags']['hit']
    meta_tag_miss = config['Hydrus_Meta_Tags']['miss']
    meta_tag_mom = config['Hydrus_Meta_Tags']['miss_over_minsim']
    meta_tag_noresult = config['Hydrus_Meta_Tags']['no_result']
    meta_tag_service = config['Hydrus_Meta_Tags'].get('service', 'my tags')
    #saucenao
    saucenao_api_key = config['SauceNao']['api_key']
    minsim = config['SauceNao']['minsim']
    sauce_numres = config['SauceNao'].getint('numres')
    #saucenao_indexes
    saucenao_indexes = config['SauceNao_Indexes']

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
        if meta_tag_mom:
            missovermin_tag = meta_tag_namespace+':'+meta_tag_mom
        if meta_tag_noresult:
            noresult_tag = meta_tag_namespace+':'+meta_tag_noresult
    else:
        if meta_tag_hit:
            hit_tag = meta_tag_hit
        if meta_tag_miss:
            miss_tag = meta_tag_miss
        if meta_tag_mom:
            missovermin_tag = meta_tag_mom
        if meta_tag_noresult:
            noresult_tag = meta_tag_noresult

#list indexes match server indexes
#this is why reserved is included despite not being part of dbmask calcs
sauce_index_list = ['hmags',
                    'hanime',
                    'hcg',
                    'ddbobjects',
                    'ddbsamples',
                    'pixiv',
                    'pixivhistorical',
                    'anime',
                    'seigaillust',
                    'danbooru',
                    'drawr',
                    'nijie',
                    'yandere',
                    'animeop',
                    'imdb',
                    'shutterstock',
                    'fakku',
                    'reserved',
                    'nhentai',
                    '2dmarket',
                    'medibang',
                    'anime',
                    'hanime',
                    'movies',
                    'shows',
                    'gelbooru',
                    'konachan',
                    'sankaku',
                    'animepictures',
                    'e621',
                    'idolcomplex',
                    'bcyillust',
                    'bcycosplay',
                    'portalgraphics',
                    'da',
                    'pawoo',
                    'madokami',
                    'mangadex',
                    'ehentai',
                    'artstation',
                    'furaffinity',
                    'twitter',
                    'furrynetwork']

#generate appropriate bitmask & empty index config sections
def bis(boolin):
    return str(int(boolin))
db_bitmask_bin = ''
for i in reversed(sauce_index_list):
    if i == 'reserved':
        continue
    if not i in config.keys():
        config[i] = {}
    if saucenao_indexes.getboolean(i, False):
        db_bitmask_bin = db_bitmask_bin+'1'
    else:
        db_bitmask_bin = db_bitmask_bin+'0'
        
db_bitmask = int(db_bitmask_bin, 2)
if verbose_output:
    print("dbmask="+str(db_bitmask))
#encoded print - handle random crap
def printe(line):
    print(str(line).encode(sys.getdefaultencoding(), 'replace')) #ignore or replace
    
sauce = SauceNao(api_key=saucenao_api_key,
                dbmask=db_bitmask,
                numres=sauce_numres,
)
    
client = hydrus.Client(hydrus_api_key, hydrus_api_url)

if shutil.which('git') and os.path.exists('.git'):
    hn_revision = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
else:
    hn_revision = 'Git'

r_head = requests.utils.default_headers()

r_head.update(
    {
        'User-Agent': 'HydrausNao/'+hn_revision+' by GanBat',
    }
)

if verbose_output:
    print('User-Agent:'+str(r_head['User-Agent']))

try:
    p = hydrus.utils.verify_permissions(client, hydrus_permissions)
except:
    print("Hydrus-API encountered a server error.\nHydrus API key may be malformed.")
    sys.exit(6)
else:
    if not hydrus.utils.verify_permissions(client, hydrus_permissions):
        print("The Hydrus API key does not grant all required permissions:", hydrus_permissions)
        sys.exit(1)
        
def tag_file(status):
    if not meta_enable_tags:
        return
    
    if status == "hit" and meta_tag_hit:
        final_tag = hit_tag
    elif status == "miss" and meta_tag_miss:
        final_tag = miss_tag
    elif status == "miss_over_min":
        if meta_tag_mom:
            final_tag = missovermin_tag
        elif meta_tag_miss:
            final_tag = miss_tag
    elif status == "noresult" and meta_tag_noresult:
        final_tag = noresult_tag
    else:
        return
    
    try:
        client.add_tags(hashes=line.splitlines(), service_to_tags={meta_tag_service: [final_tag]})
    except hydrus.MissingParameter as e:
        print(str(e))
        print("A different tag service can be set in config.ini.\n"
            "Add a key called service to the Hydrus_Meta_Tags section and\nset it to the name of your tag service.\n\n"
            "Example:\n[Hydrus_Meta_Tags]\nservice = my tag service")
        sys.exit(e)
    else:
        return
    
def test_blacklist(result_author, blacklist):
    if verbose_output:
        print('Blacklist file: '+blacklist)
    f = open(blacklist, 'r')
    if result_author in f.read():
        print('miss... blacklisted author: '+result_author)
        tag_file("miss")
        f.close()
        return True
    else:
        return False
      
#this can be done better, elimate redundancy and stuff
def handle_results(results):
    if not gen_test_res:
        f_blacklist = config[sauce_index_list[results[0].index_id]]['blacklist_file']
        if f_blacklist:
            if test_blacklist(results[0].author, f_blacklist):
                return
        if results[0].similarity > float(minsim.strip('!')):
            print('hit! '+str(results[0].similarity), flush=True)
            tag_file("hit")
            client.add_url(url=results[0].urls[0], page_name=hydrus_page_name)
        else:
            tag_file("miss")
        return
    if verbose_output:
        resultnum = 0
    for i in results:
        if verbose_output:
            resultnum += 1
            print('Trying result #'+str(resultnum)+'\nSimilarity:'+str(i.similarity))
        if i.similarity > float(minsim.strip('!')):
            f_blacklist = config[sauce_index_list[i.index_id]]['blacklist_file']
            if f_blacklist:
                if test_blacklist(i.author, f_blacklist):
                    continue
            for k in i.urls:
                if verbose_output:
                    print('Processing URL:'+k, flush=True)
                r = requests.get(k, headers=r_head)
                if verbose_output:
                    print('Response code:'+str(r.status_code), flush=True)
                if r.status_code == 200:
                    print('hit! '+str(i.similarity), flush=True)
                    tag_file("hit")
                    client.add_url(url=k, page_name=hydrus_page_name)
                    return
    else:
        print('miss... '+str(results[0].similarity), flush=True)
        if results[0].similarity > float(minsim.strip('!')):
            tag_file("miss_over_min")
        else:
            tag_file("miss")
        return

short_pause = False

for line in hash_input:
    if short_pause:
        print('Out of searches for this 30 second period. Sleeping for 30 seconds...', flush=True)
        if results:
            print(str(results.long_remaining)+' searches remaining today.', flush=True)
        time.sleep(30)
        print("")
    short_pause = False
    thumbnail = client.get_thumbnail(hash_=line)
    print("Processing hash: "+str(line).rstrip(), flush=True)
    
    retries = 0
    while True:
        try:
            results = sauce.from_file(thumbnail.content)
        except SauceNaoErrors.ShortLimitReachedError as e:
            print(str(e)+". Retrying in 2 minutes...", flush=True)
            time.sleep(2*60)
            continue
        except SauceNaoErrors.LongLimitReachedError as e:
            print(str(e)+". Retrying in 24 hours...", flush=True)
            time.sleep(24*60*60)
            continue
        except SauceNaoErrors.UnknownClientError as e:
            sys.exit(str(e))
        except SauceNaoErrors.UnknownServerError as e:
            if str(e) == 'Unknown API error, status > 0':
                if retries < 4:
                    print(str(e)+". Retrying in 10 minutes...", flush=True)
                    retries += 1
                    time.sleep(600)
                    continue
                else:
                    sys.exit(str(e)+". Maximum reties reached.")
            else:
                sys.exit(str(e))
        except SauceNaoErrors.UnknownApiError as e:
            if retries < 4:
                print(str(e)+". Retrying in 10 minutes...", flush=True)
                retries += 1
                time.sleep(600)
                continue
            else:
                sys.exit(str(e)+". Maximum reties reached.")
        except SauceNaoErrors.BadFileSizeError as e:
            print(str(e)+". This should be impossible.\nTry regenerating the thumbnail for this file. Skipping...", flush=True)
            time.sleep(10)
            break
        else:
            if results:
                handle_results(results)
            else:
                print('no results... ;_;', flush=True)
                tag_file("noresult")
            if results.short_remaining < 1:
                short_pause = True
            print("")
            break
    
print('All Done!')
