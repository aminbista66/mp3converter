from pymongo import MongoClient
from gridfs import GridFS
from dotenv import load_dotenv, find_dotenv
import os
from bson.objectid import ObjectId

load_dotenv(find_dotenv())

client = MongoClient(os.environ.get("MONGO_URI"))
mp3_db = client.get_database('mp3_db')
fs_mp3s = GridFS(mp3_db)

# Stream the file data back to the client
def stream_file(file_id):
    try:
        with fs_mp3s.get(ObjectId(file_id)) as file_stream:
            for chunk in file_stream:
                yield chunk
    except Exception as err:
        raise Exception(str(err))