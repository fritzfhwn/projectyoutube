import json
import pickle


class DataHandler:

    @staticmethod
    def load_data(file_path, format):
        if format == 'json':
            with open(file_path, 'r') as file:
                return json.load(file)
        elif format == 'pickle':
            with open(file_path, 'rb') as file:
                return pickle.load(file)

    @staticmethod
    def save_data(data, file_path, format):
        if format == 'json':
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)
        elif format == 'pickle':
            with open(file_path, 'wb') as file:
                pickle.dump(data, file)
