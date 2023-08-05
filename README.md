# jellyfin-transubtitle

This is a Python script that performs automatic translation of subtitles in the ASS format for media items
in a Jellyfin media server. It uses the Baidu Text Translation API for translation purposes.

## How To Use

1. Install Docker (Compose)
2. Edit the ```.env``` file. (Copy from .env.example)
3. Execute ```docker-compose up``` (If as daemon, Add the ```-d``` option.)

## Parameter Description

The following are the parameters that can be defined and their purposes:

- `USER_NAME`: The username of the Jellyfin user for whom the subtitles will be translated.
- `BASE_URI`: The base URL of the Jellyfin server.
- `API_TOKEN`: The API token for accessing the Jellyfin server.
- `JELLYFIN_TARGET_LANG`: The [target language](doc/language.md) for the translated subtitles.
- `SCAN_INTERVAL`: The interval (in seconds) at which the script scans for new media items.

Ensure that the environment variables are correctly set before running the script.

### Baidu Text Translation API

The script utilizes the Baidu Text Translation API. That requires the following Baidu API credentials to be set as
environment variables:

- `BAIDU_APP_ID`: The App ID for the Baidu Text Translation API.
- `BAIDU_APP_KEY`: The App Key for the Baidu Text Translation API.
- `BAIDU_TARGET_LANG`: The [target language](http://api.fanyi.baidu.com/doc/21) for translation using the Baidu Text Translation API.

## Other Notes

The script performs the following tasks:

1. Loads the user information from the Jellyfin server using the `jellyfin('Users')` function and extracts the user ID
   based on the provided username.
2. Defines a `scan` function that recursively scans the media library of the user and calls a provided callback function
   for each media item.
3. Defines a `translate_ass` function that translates the content of an ASS subtitle file using the Baidu Text
   Translation API.
4. Defines a `translate_subtitle` function that checks if a media item has ASS format subtitles and translates them if
   the target language is not already available.
5. Enters a loop that continuously scans for new media items and translates their subtitles using the `scan`
   and `translate_subtitle` functions.
6. The loop is interrupted by a keyboard interrupt (Ctrl+C) to gracefully stop the script.
