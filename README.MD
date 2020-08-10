# HydrausNao
A script to automatically search SauceNao for images and send results to Hydrus Network.

**Disclaimer:** I know basic coding, but have no prior experience with Python. Don't expect anything amazing.

## Requirements
* Python 3+
* Requests (`pip install requests`)
* Hydrus-API (`pip install hydrus-api`)

## Use
1. In your Hydrus Client, the Client API must be enabled, and a key with the permissions "Add URLs" and "Search Files" must be created
2. On SauceNAO, create or login to a user account and navigate to the [search api page](https://saucenao.com/user.php?page=search-api)
3. Edit hydrus_saucenao_search.py, replacing placeholders in the CONFIG section with the relevant API keys, and making other changes as necessary
4. Create a new text document in the same folder as hydrus_saucenao_search.py called 'hashes.txt' (or any name you may have changed 'hash_file' to in the CONFIG section) and paste in sha256 hashes for any files you with to search
5. Run the script

The script will inform you of the status of its searches as well as your remaining SauceNao API use limits. Any URLs found will automatically be added to Hydrus for download, in a new page called "HydrausNao" (unless changed in the CONFIG section)

### Credits

This script is based directly upon [Identify and Rename Images 1.1](https://saucenao.com/tools/examples/api/identify_images_v1.1.py), the API example script provided by SauceNao.