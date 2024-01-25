import requests
import json
from datetime import datetime, timezone
import pandas as pd
from api import YoutubeAPIHandler
import pickle
from data_handler import DataHandler

class DataProcessor:

    search_strings = pd.read_excel("./data/Suchbegriffe_random.xlsx")
    search_strings.columns = ["Category"]

    api_data = DataHandler.load_data("./data/api.json", "json")
    categories = DataHandler.load_data("./data/category_list.json", "json")

    @staticmethod
    def get_channel_details_by_video_list(video_list):
        if "items" in video_list.keys():
            for item in video_list["items"]:
                DataProcessor.api_data["args"]["channel"]["id"] = item["snippet"]["channelId"]
                channel_response = YoutubeAPIHandler.make_api_request(DataProcessor.api_data["api"]["channel"], DataProcessor.api_data["args"]["channel"])
                if "items" in channel_response.keys():
                    item["channel_details"] = channel_response["items"]

    @staticmethod
    def get_video_statistics_by_video_list(video_list):
        # function receives the prepared video list from search filter
        # will add further video details and statistics to the list which are not to be found in
        # the search queue
        if "items" in video_list.keys():
            for item in video_list["items"]:
                # fileDetails, processingDetails, suggestions - only for content owner
                DataProcessor.api_data["args"]["video"]["id"] = item["id"]["videoId"]
                video_response = YoutubeAPIHandler.make_api_request(DataProcessor.api_data["api"]["video"], DataProcessor.api_data["args"]["video"])
                if "items" in video_response.keys():
                    for category in DataProcessor.categories:
                        if category["id"] == video_response["items"][0]["snippet"]["categoryId"]:
                            video_response["items"][0]["snippet"]["categoryId"] = category["name"]
                item["video_details"] = video_response

    @staticmethod
    def get_category_list():
        # only initially needed to create the json dump of all video categories
        response = YoutubeAPIHandler.make_api_request(DataProcessor.api_data["api"]["category"], DataProcessor.api_data["args"]["category"])["items"]
        category_list = [{"id": item["id"], "name": item["snippet"]["title"]} for item in response]
        DataHandler.save_data(category_list, "video_categories.json", "json")

    @staticmethod
    def get_video_list_by_search_filter():
        data_list = []
        for i in DataProcessor.search_strings.index:
            DataProcessor.api_data["args"]["search"]["q"] = DataProcessor.search_strings.loc[i, "Category"]
            search_list = YoutubeAPIHandler.make_api_request(DataProcessor.api_data["api"]["search"], DataProcessor.api_data["args"]["search"])
            search_list["kind"] = DataProcessor.search_strings.loc[i, "Category"]
            DataProcessor.get_video_statistics_by_video_list(search_list)
            DataProcessor.get_channel_details_by_video_list(search_list)
            data_list.append(search_list)

        DataHandler.save_data(data_list, "./data/full_video_list.json", "json")


    @staticmethod
    def create_dataframe(search_args_list):
        df = {"video_id": [], "published_at": [], "channel_id": [], "length_title": [], "length_description": [], "liveBroadcastContent": [], "length_tags": [], "category": [], "duration": [], "dimension": [], "definition": [], "caption": [], "licensedContent": [], "privacyStatus": [], "view_count": [], "like_count": [], "favorite_count": [], "comment_count": [], "channel_view_count": [], "channel_sub_count": [], "channel_video_count": [], "channel_country": []}

        for search_entry in search_args_list:
            if "items" in search_entry:
                for video in search_entry:
                    if video == "items":
                        for dict_entry in search_entry[video]:
                            if all(key in dict_entry for key in ["id", "snippet", "video_details", "channel_details"]):
                                if "items" in dict_entry["video_details"]:
                                    if all(key in dict_entry["video_details"]["items"][0]["statistics"] for key in ["likeCount", "commentCount"]):
                                        df["video_id"].append(dict_entry["id"]["videoId"])
                                        df["published_at"].append(dict_entry["snippet"]["publishedAt"])
                                        df["channel_id"].append(dict_entry["snippet"]["channelId"])
                                        df["length_title"].append(len(dict_entry["video_details"]["items"][0]["snippet"]["title"]))
                                        df["length_description"].append(len(dict_entry["video_details"]["items"][0]["snippet"]["description"]))
                                        df["category"].append(dict_entry["video_details"]["items"][0]["snippet"]["categoryId"])
                                        df["liveBroadcastContent"].append(dict_entry["video_details"]["items"][0]["snippet"]["liveBroadcastContent"])
                                        df["duration"].append(dict_entry["video_details"]["items"][0]["contentDetails"]["duration"])
                                        df["dimension"].append(dict_entry["video_details"]["items"][0]["contentDetails"]["dimension"])
                                        df["definition"].append(dict_entry["video_details"]["items"][0]["contentDetails"]["definition"])
                                        df["caption"].append(dict_entry["video_details"]["items"][0]["contentDetails"]["caption"])
                                        df["licensedContent"].append(dict_entry["video_details"]["items"][0]["contentDetails"]["licensedContent"])
                                        df["privacyStatus"].append(dict_entry["video_details"]["items"][0]["status"]["privacyStatus"])
                                        df["view_count"].append(dict_entry["video_details"]["items"][0]["statistics"]["viewCount"])
                                        df["like_count"].append(dict_entry["video_details"]["items"][0]["statistics"]["likeCount"])
                                        df["favorite_count"].append(dict_entry["video_details"]["items"][0]["statistics"]["favoriteCount"])
                                        df["comment_count"].append(dict_entry["video_details"]["items"][0]["statistics"]["commentCount"])
                                        if "tags" in dict_entry["video_details"]["items"][0]["snippet"]:
                                            df["length_tags"].append(len(dict_entry["video_details"]["items"][0]["snippet"]["tags"]))
                                        else:
                                            df["length_tags"].append(None)
                                        df["channel_view_count"].append(dict_entry["channel_details"][0]["statistics"]["viewCount"])
                                        df["channel_sub_count"].append(dict_entry["channel_details"][0]["statistics"]["subscriberCount"])
                                        df["channel_video_count"].append(dict_entry["channel_details"][0]["statistics"]["videoCount"])
                                        if "country" in dict_entry["channel_details"][0]["snippet"]:
                                            df["channel_country"].append(dict_entry["channel_details"][0]["snippet"]["country"])
                                        else:
                                            df["channel_country"].append(None)
        df = pd.DataFrame(df)
        DataHandler.save_data(df, "./data/df_video_stats.pkl", "pickle")

    @staticmethod
    def process_dataframe(dataframe):
        df = dataframe

        df['published_at'] = pd.to_datetime(df['published_at'], utc=True)
        df['days_online'] = (datetime.now(timezone.utc) - df['published_at']).dt.days
        df['published_month'] = df['published_at'].dt.month
        df['published_year'] = df['published_at'].dt.year
        df['duration_sec'] = pd.to_timedelta(df['duration']).dt.total_seconds()
        df['duration_sec'] = df['duration_sec'].astype(int)

        return df

    @staticmethod
    def generate_dummies_from_dataframe(dataframe):
        df = dataframe

        df = pd.get_dummies(df, columns=['category'], prefix="cat")
        df = pd.get_dummies(df, columns=['channel_country'], prefix="country")
        df = pd.get_dummies(df, columns=['caption'], prefix="caption")
        df = pd.get_dummies(df, columns=['licensedContent'], prefix="licensed")
        df = pd.get_dummies(df, columns=['privacyStatus'], prefix="privacy")

        df = df.drop(columns=['published_at', 'video_id', "channel_id", "favorite_count",
                              "dimension", "definition", "length_tags", "liveBroadcastContent",
                              "caption_false", "licensed_False", "duration", 'published_year'],
                     axis=1)

        df = df.dropna()

        for col in df.columns:
            if df[col].dtype == 'bool':
                df[col] = df[col].astype(int)

        return df


