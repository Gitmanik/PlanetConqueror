import json
import logging
import os
import sys

if sys.platform != "emscripten":
    import pymongo

import config

logger = logging.getLogger(__name__)

class SaveManager:

    @staticmethod
    def save_file(filename, content):
        if sys.platform == "emscripten":
            from platform import window
            stored = window.localStorage.getItem(config.LOCAL_STORAGE)
            try:
                files_data = json.loads(stored) if stored else {}
            except:
                files_data = {}
            files_data[filename] = content
            window.localStorage.setItem(config.LOCAL_STORAGE, json.dumps(files_data))
            logger.info(f"Saved file to localStorage under key '{config.LOCAL_STORAGE}' with filename {filename}")
        else:
            logger.info(f"Saving file to {filename}")
            with open(os.path.join(config.SAVES_FOLDER, filename), 'w') as f:
                f.write(content)

    @staticmethod
    def read_file(filename):
        if sys.platform == "emscripten":
            from platform import window
            stored = window.localStorage.getItem(config.LOCAL_STORAGE)
            try:
                files_data = json.loads(stored) if stored else {}
            except:
                files_data = {}
            if filename in files_data:
                logger.info(f"Loading file from localStorage under key '{config.LOCAL_STORAGE}' with filename {filename}")
                return files_data[filename]
            else:
                logger.error(f"File {filename} not found in localStorage")
                return None
        else:
            logger.info(f"Loading file from {filename}")
            with open(os.path.join(config.SAVES_FOLDER, filename), 'r') as f:
                return f.read()

    @staticmethod
    def list_files():
        if sys.platform == "emscripten":
            from platform import window
            stored = window.localStorage.getItem(config.LOCAL_STORAGE)
            try:
                files_data = json.loads(stored) if stored else {}
            except:
                files_data = {}
            return files_data.keys()
        else:
            files = os.listdir(config.SAVES_FOLDER)

            client = pymongo.MongoClient(config.MONGO_CONNECTION_URI, serverSelectionTimeoutMS=100)
            try:
                client.admin.command('ping')
                db = client[config.MONGO_DB]
                collection = db[config.MONGO_COLLECTION]
                data = collection.find()
                for entry in data:
                    files.append(entry["mongo_name"] + ".mongo")
                client.close()
            except:
                logger.error("MongoDB not available")

            return files