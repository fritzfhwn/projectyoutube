# YouTube Video Analysis Project

This project is an analysis project focused on YouTube videos, utilizing the YouTube API for data collection. It offers
the capability to query search results, video details, and channel information. Examples of these queries are provided
in the files `example_search_fitness`, `example_video`, `example_channel` for individual results and 
`complete_list_fitness` for a combination of all results, respectively.

## Project Overview

The project includes a `video_list.json` file containing the entire JSON output from combined search
queries, associated video details, and channel details. This output was generated through API requests made from a list
of search queries representing the video categories from YouTube8M. Due to the limited number of API requests available,
the list was randomized, and 66 search terms were used, with 25 videos considered for each term. Therefore, the analysis
is based on this random sample.

The core data queries are performed in the notebooks `visualization.ipynb` and `regressionsanalyse.ipynb`. Other files
serve as accessory files for processing, requesting, loading, or saving data. The `data_processor.ipynb` notebook primarily handles
the processing of the `video_list.json`, which comprises a complete output of search queries, video details, and channel
information, to save the filtered data as a CSV file. This filtered file is then loaded and further processed
in `Auswertung_Daten.ipynb` to remove unnecessary metrics of the api queries.

The same functionality is also present in `data_processor.py`, which first saves the data from `video_list.json` as a filtered dataframe. This
dataframe `df_video_stats.pkl` is then loaded and processed in `visualization.ipynb` for exploratory data analysis. Contrary, the
notebook `regressionsanalyse.ipynb` uses the cleaned CSV for both data exploration and regression analyses.

The `api.json` file contains the API filter criteria as a dictionary. The `category_list.json` file includes the list of
YouTube categories, which is used to convert category IDs into strings when saving the JSON.


