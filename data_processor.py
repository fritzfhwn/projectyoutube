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
        """
        Retrieves channel details for a list of videos by making API requests to fetch channel information based on channelId found in each video's details.

        :param video_list: A dictionary containing video items, each with a 'snippet' that includes the 'channelId'.
        :return: None. The function modifies the input video_list in-place, adding 'channel_details' to each item if channel information is successfully retrieved.

        This method iterates over the 'items' in the video_list, uses the 'channelId' to make API requests for channel details,
        and appends the channel details to the corresponding video item if found.
        """
        if "items" in video_list.keys():
            for item in video_list["items"]:
                DataProcessor.api_data["args"]["channel"]["id"] = item["snippet"]["channelId"]
                channel_response = YoutubeAPIHandler.make_api_request(DataProcessor.api_data["api"]["channel"], DataProcessor.api_data["args"]["channel"])
                if "items" in channel_response.keys():
                    item["channel_details"] = channel_response["items"]

    @staticmethod
    def get_video_statistics_by_video_list(video_list):
        """
        Enhances a list of videos with additional video details and statistics not available in the initial search query results.

        :param video_list: A dictionary representing a list of videos.
        :return: None. The function updates the input video_list in-place, appending detailed video statistics and information to each video item.

        Iterates through the 'items' in video_list, making API requests for each video's detailed statistics and information using the video's ID.
        Transforms category IDs into readable names using the predefined category list, updating each video's details accordingly.
        """
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
        """
        Fetches the list of all video categories available on YouTube and saves them as a JSON file.

        :return: None. The function makes an API request to retrieve video categories and saves the result as 'video_categories.json'.

        This method is primarily used for initial setup to create a JSON dump of all video categories, associating category IDs with their respective titles.
        """
        response = YoutubeAPIHandler.make_api_request(DataProcessor.api_data["api"]["category"], DataProcessor.api_data["args"]["category"])["items"]
        category_list = [{"id": item["id"], "name": item["snippet"]["title"]} for item in response]
        DataHandler.save_data(category_list, "video_categories.json", "json")

    @staticmethod
    def get_video_list_by_search_filter():
        """
        Compiles a comprehensive list of videos based on specified search filters, enriching each video with detailed statistics and channel information.

        :return: None. The function saves the compiled and enriched video list as a JSON file in the './data' directory.

        For each search string from a predefined list, this method makes API requests to fetch videos, their statistics, and channel details.
        Each search result is then enhanced with additional video and channel details before being saved collectively as 'full_video_list.json'.
        """
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
        """
        Creates a DataFrame from a list of search argument entries, each containing video and channel details, and saves it as a pickle file.

        :param search_args_list: A list of dictionaries, each representing search results with video items and their associated details.
        :return: None. Constructs a DataFrame with detailed video and channel statistics and saves it as './data/df_video_stats.pkl'.

        This method aggregates video and channel information from the input list, creating a comprehensive DataFrame that includes various metrics
        and details for each video, such as view counts, like counts, and channel subscriber counts. The resulting DataFrame is saved for further analysis.
        """
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
        """
        Processes a DataFrame by converting date strings to datetime objects and adding derived columns for analysis.

        :param dataframe: A pandas DataFrame containing video and channel metrics, including publication dates and durations.
        :return: A pandas DataFrame with additional columns for days online, publication month, publication year, and video duration in seconds.

        Enhances the input DataFrame by converting publication dates to datetime, calculating the number of days each video has been online,
        extracting month and year of publication, and converting video duration into seconds. This processed DataFrame is returned for further analysis.
        """
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
        """
        Converts categorical variables within a DataFrame into dummy/indicator variables and performs cleaning to prepare for regression.

        :param dataframe: A DataFrame with video and channel metrics, including categorical fields like category and country.
        :return: A pandas DataFrame with dummy variables for categories, country, caption availability, licensed content, and privacy status.

        This method generates dummy variables for several categorical columns, drops unnecessary or redundant columns, and ensures all boolean columns are converted to integers.
        The cleaned and transformed DataFrame is returned, ready for regression analysis.
        """
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


