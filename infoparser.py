import asyncio

import aiohttp

# from yandex_music import ClientAsync


class MusicInfoParser:
    async def getInfoAboutNow_spotify(self, stastfm_username: str):
        headers = {"User-Agent": "Mozilla/5.0 (compatible; Musixinfobot/1.0)"}
        user_url = f"https://api.stats.fm/api/v1/users/{stastfm_username}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(user_url, headers=headers) as usresp:
                    if usresp.status != 200:
                        return usresp.status

                    usdata = await usresp.json()

                if "item" in usdata:
                    user_id = usdata["item"]["id"]
                else:
                    user_id = usdata.get("id")

                if not user_id:
                    return 404

                stream_url = (
                    f"https://api.stats.fm/api/v1/users/{user_id}/streams/current"
                )

                async with session.get(stream_url, headers=headers) as stream_resp:
                    if stream_resp.status == 200:
                        full_data = await stream_resp.json()
                        track_data = full_data.get("item")

                        ### print(f"TRACK_DATA {track_data}")
                        if track_data and track_data.get("isPlaying"):
                            ### print(track_data)
                            track_info = track_data["track"]
                            track_name = track_info["name"]

                            track_artists = []
                            for artist in track_info["artists"]:
                                track_artists.append(artist["name"])

                            try:
                                track_thumb = track_info["albums"][0]["image"]
                            except (KeyError, IndexError):
                                track_thumb = None

                            track_externalId = track_info["externalIds"]["spotify"][0]
                            track_url = (
                                f"https://open.spotify.com/track/{track_externalId}"
                            )

                            try:
                                odesli_apiurl = f"https://api.song.link/v1-alpha.1/links?url={track_url}"

                                async with session.get(odesli_apiurl) as res:
                                    if res.status == 200:
                                        data = await res.json()
                                        all_url = data.get("pageUrl")
                                    else:
                                        all_url = None
                            except Exception as e:
                                all_url = None
                                print("Odesly error: " + str(e))

                            return {
                                "title": track_name,
                                "artists": track_artists,
                                "thumb": track_thumb,
                                "url": track_url,
                                "all_url": all_url,
                            }
                        else:
                            return 200
                    else:
                        return 100

        except Exception as e:
            print(f"Error in parser spotify: {e}")
            return 500

    async def getInfoAboutNow_YM(self, token):
        url = "https://track.mipoh.ru/get_current_track_beta"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "ya-token": token,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        res = await resp.json()
                        track = res["track"]
                        track_name = track["title"]
                        track_artists = track["artist"].split(", ")
                        track_thumb = track["img"]
                        track_url = "https://music.yandex.ru/track/" + str(
                            track["track_id"]
                        )
                        try:
                            odesli_apiurl = f"https://api.song.link/v1-alpha.1/links?url={track_url}"

                            async with session.get(odesli_apiurl) as res:
                                if res.status == 200:
                                    data = await res.json()
                                    all_url = data.get("pageUrl")
                                else:
                                    all_url = None
                        except Exception as e:
                            all_url = None
                            print("Odesly error: " + str(e))

                        return {
                            "title": track_name,
                            "artists": track_artists,
                            "thumb": track_thumb,
                            "url": track_url,
                            "all_url": all_url,
                        }
                    else:
                        return 200
        except Exception as e:
            print(f"error in parser YM: {e}")
            return 500
