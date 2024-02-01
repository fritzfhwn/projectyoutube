import json
import pickle


class DataHandler:

    @staticmethod
    def load_data(file_path, format):
        """
        Loads data from a specified file path according to the given format.
        This method supports loading data in either JSON or pickle format.

        :param file_path: The path to the file from which data is to be loaded.
        :param format: The format of the file and expected data. Supported values are 'json' and 'pickle'.
        :return: The data deserialized from the file.

        """
        if format == 'json':
            with open(file_path, 'r') as file:
                return json.load(file)
        elif format == 'pickle':
            with open(file_path, 'rb') as file:
                return pickle.load(file)

    @staticmethod
    def save_data(data, file_path, format):
        """
        Saves data from a specified file path according to the given format.
        This method supports saving data in either JSON or pickle format.

        :param data: The data to be saved. Can be any data structure supported by the specified format.
        :param file_path: The path to the file from which data is to be saved.
        :param format: The format of the file. Supported values are 'json' and 'pickle'.

        """
        if format == 'json':
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)
        elif format == 'pickle':
            with open(file_path, 'wb') as file:
                pickle.dump(data, file)
