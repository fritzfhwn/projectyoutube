import requests
import json
from datetime import datetime

#filter timespan
start_time = datetime(year=2005, month=1, day=1).strftime('%Y-%m-%dT%H:%M:%SZ')
end_time = datetime(year=2008, month=1, day=1).strftime('%Y-%m-%dT%H:%M:%SZ')

api_key = "AIzaSyBTJ-3GnxHQStbUBxI8cPdxMjGRDnV6iAY"
search_api = "https://www.googleapis.com/youtube/v3/search"
video_api = "https://www.googleapis.com/youtube/v3/videos"
channel_api = "https://www.googleapis.com/youtube/v3/channels"
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


def get_channel_details_by_video_list(video_list):
    for item in video_list["items"]:
        channel_args = {
            "part": "snippet,contentDetails,statistics,brandingSettings,contentOwnerDetails,"
                    "localizations,status,topicDetails",
            "id": item["snippet"]["channelId"],
            "key": api_key
        }
        channel_response = requests.get(channel_api, channel_args).json()
        item["channel_details"] = channel_response["items"]
def get_video_statistics_by_video_list(video_list):
    #function receives the prepared video list from search filter
    #will add further video details and statistics to the list which are not to be found in
    # the search queue
    for item in video_list["items"]:
        # fileDetails, processingDetails, suggestions - only for content owner
        video_args = {
            "part": "snippet,contentDetails,statistics,liveStreamingDetails,"
                    "localizations,player,recordingDetails,status,"
                    "topicDetails",
            "id": item["id"]["videoId"],
            "key": api_key
            }
        video_response = requests.get(video_api, video_args).json()
        for category in categories:
            if category["id"] == video_response["items"][0]["snippet"]["categoryId"]:
                video_response["items"][0]["snippet"]["categoryId"] = category["name"]
        item["video_details"] = video_response

def get_video_list_by_search_filter(search_string):
    search_args = {
        "part": "snippet",
        "q": search_string,
        "type": "video",
        "maxResults": 10,
        "key": api_key,
        "pageToken": None
    }

    counter = 1
    filtered_search_list = {
        "header": [],
        "items": []}
    while counter < 5:
        search_list = requests.get(search_api, search_args).json()
        filtered_search_list["header"] = [{item: search_list[item]} for item in search_list.keys() if item != "items"]
        if search_args["pageToken"] == search_list["nextPageToken"]:
            break
        search_args["pageToken"] = search_list["nextPageToken"]
        for item in search_list["items"]:
            filtered_search_list["items"].append(item)
        counter += 1
    get_video_statistics_by_video_list(filtered_search_list)
    get_channel_details_by_video_list(filtered_search_list)
    json.dump(filtered_search_list, open(f"complete_list_{search_string}", "w"), indent=6)


get_video_list_by_search_filter("fitness")