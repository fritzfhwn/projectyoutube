import requests
import json
from datetime import datetime
import pandas as pd
from api import YoutubeAPIHandler

search_strings = pd.read_excel("./data/Suchbegriffe.xlsx")
search_strings.columns = ["Category"]
api_data = json.load(open("./data/api.json"))
categories = json.load(open("./data/category_list.json"))

def get_category_list():
    # only initially needed to create the json dump of all video categories
    response = YoutubeAPIHandler.make_api_request(api_data["api"]["category"], api_data["args"]["category"])["items"]
    category_list = [{"id": item["id"], "name": item["snippet"]["title"]} for item in response]
    return json.dump(category_list, open("category_list", "w"), indent=6)


def get_channel_details_by_video_list(video_list):
    if "items" in video_list.keys():
        for item in video_list["items"]:
            api_data["args"]["channel"]["id"] = item["snippet"]["channelId"]
            channel_response = YoutubeAPIHandler.make_api_request(api_data["api"]["channel"], api_data["args"]["channel"])
            if "items" in channel_response.keys():
                item["channel_details"] = channel_response["items"]


def get_video_statistics_by_video_list(video_list):
    # function receives the prepared video list from search filter
    # will add further video details and statistics to the list which are not to be found in
    # the search queue
    if "items" in video_list.keys():
        for item in video_list["items"]:
            # fileDetails, processingDetails, suggestions - only for content owner
            api_data["args"]["video"]["id"] = item["id"]["videoId"]
            video_response = YoutubeAPIHandler.make_api_request(api_data["api"]["video"], api_data["args"]["video"])
            if "items" in video_response.keys():
                for category in categories:
                    if category["id"] == video_response["items"][0]["snippet"]["categoryId"]:
                        video_response["items"][0]["snippet"]["categoryId"] = category["name"]
            item["video_details"] = video_response


def get_video_list_by_search_filter():
    data_list = []
    counter = 1
    for i in search_strings.index:
        api_data["args"]["search"]["q"] = search_strings.loc[i, "Category"]
        search_list = YoutubeAPIHandler.make_api_request(api_data["api"]["search"], api_data["args"]["search"])
        search_list["kind"] = search_strings.loc[i, "Category"]
        get_video_statistics_by_video_list(search_list)
        get_channel_details_by_video_list(search_list)
        data_list.append(search_list)
        print(counter, search_strings.loc[i, "Category"])
        counter += 1
    json.dump(data_list, open(f"list_test", "w"), indent=6)


get_video_list_by_search_filter()
