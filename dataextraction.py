import requests
import json
from datetime import datetime

#filter timespan
start_time = datetime(year=2005, month=1, day=1).strftime('%Y-%m-%dT%H:%M:%SZ')
end_time = datetime(year=2008, month=1, day=1).strftime('%Y-%m-%dT%H:%M:%SZ')

api_key = "AIzaSyBTJ-3GnxHQStbUBxI8cPdxMjGRDnV6iAY"
search_api = "https://www.googleapis.com/youtube/v3/search"
video_api = "https://www.googleapis.com/youtube/v3/videos"
categories_api = "https://www.googleapis.com/youtube/v3/videoCategories"


category_args = {
    "part": "snippet",
    "regionCode": "AT",
    "key": api_key
}

def get_category_list():
    #only initially needed to create the json dump of all video categories
    response = requests.get(categories_api, category_args).json()["items"]
    category_list = [{"id": item["id"], "name": item["snippet"]["title"]} for item in response ]
    return json.dump(category_list, open("category_list", "w"), indent=6)

categories = json.load(open("category_list.json"))

def get_video_statistics_by_video_list(video_list):
    #function receives the prepared video list from search filter
    #will add further video details and statistics to the list which are not to be found in
    # the search queue
    for item in video_list["video_results"]:
        for entry in item:
            video_args = {
                "part": "snippet,contentDetails,statistics",
                "id": entry["videoId"],
                "key": api_key
            }
            video_response = requests.get(video_api, video_args).json()
            for category in categories:
                if category["id"] == video_response["items"][0]["snippet"]["categoryId"]:
                    entry["category"] = category["name"]
            entry["tags"] = video_response["items"][0]["snippet"]["tags"]
            entry["contentDetails"] = video_response["items"][0]["contentDetails"]
            entry["statistics"] = video_response["items"][0]["statistics"]

def get_video_list_by_search_filter(search_string, region, start_date, end_date):
    search_args = {
        "part": "snippet",
        "q": search_string,
        "type": "video",
        "regionCode": region,
        "publishedAfter": start_date,
        "publishedBefore": end_date,
        "maxResults": 5,
        "key": api_key,
        "pageToken": None
    }

    counter = 1
    filtered_search_list = {
        "region": region,
        "video_results": []
    }
    while counter < 3:
        search_list = requests.get(search_api, search_args).json()
        if search_args["pageToken"] == search_list["nextPageToken"]:
            break
        search_args["pageToken"] = search_list["nextPageToken"]
        filtered_search_list["video_results"].append([item for item in [
            {"videoId": entry["id"]["videoId"], "videoTitle": entry["snippet"]["title"],
             "description": entry["snippet"]["description"],
             "channelTitle": entry["snippet"]["channelTitle"],
             "channelId": entry["snippet"]["channelId"],
             "publishedAt": entry["snippet"]["publishedAt"],
             "liveBroadcast": entry["snippet"][
                 "liveBroadcastContent"]} for entry in search_list["items"]]])
        counter += 1

    get_video_statistics_by_video_list(filtered_search_list)
    return json.dump(filtered_search_list, open(f"video_list_{search_string}", "w"), indent=6)



get_video_list_by_search_filter("food blog", "US", start_time, end_time)