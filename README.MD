# HydrausNao
A script to automatically search SauceNao for images and send results to Hydrus Network.

**Disclaimer:** I know basic coding, but have no prior experience with Python. Don't expect anything amazing.

## Requirements
* Python 3.9+
* Requests `pip install -U requests`
* SauceNao-API `pip install -U saucenao_api`
* Hydrus-API `pip install -U hydrus-api`

## Use
1. In your Hydrus Client, the Client API must be enabled, and a key with the permissions "Add URLs", "Search Files" and "Add Tags" must be created. "Add Tags" is not necessary if tagging is disabled in config.ini.
2. On SauceNAO, create or login to a user account and navigate to the [search api page](https://saucenao.com/user.php?page=search-api)
3. Run the script once to generate a default config.ini
4. Edit config.ini, adding  your relevant API keys to the Hydrus and SauceNao sections, and making other changes as necessary
5. Create a new text document in the same folder as hydrus_saucenao_search.py called 'hashes.txt' (or any name you may have changed 'hash_file' to in the General section or config.ini) and paste in sha256 hashes for any files you with to search
6. Run the script

The script will inform you of the status of its searches as well as your remaining SauceNao API use limits. Any URLs found will automatically be added to Hydrus for download, in a new page called "HydrausNao" (unless changed in config.ini)

## About config.ini
By default, the API key options will be the only options in a generated config.ini. Any key found in config_default.ini can be copied into config.ini in order to override the default values.

If your config_default.ini becomes somehow damaged, you can delete it and run the script in order to generate a new, clean copy.

Index-specific options are have defaults defined under the `[DEFAULT]` section, and are overridden by any options defined in sections named after the respective index. Currently, the index-specific option is `blacklist_file`.

## About blacklists
HydrausNao now supports username blacklists. These blacklists are simple text files with one username per line.

By default, a small DeviantArt blacklist with several users known for uploading other's work is included as an example, but not enabled.

To enable it, add this block to your config.ini:
```
[da]
blacklist_file = blacklist-deviantart.txt
```
If adding to this blacklist, it's recommended you copy the file and update your configuration to point to that instead. Any changes to the included text file may be removed upon updates to the script.

### Credits

This script is based heavily upon [Identify and Rename Images 1.1](https://saucenao.com/tools/examples/api/identify_images_v1.1.py), the API example script provided by SauceNao.
