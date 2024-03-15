from pymongo import MongoClient
from gridfs import GridFS
from .producer import Producer
import hashlib
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

client = MongoClient(os.environ.get("MONGO_URI"))
video_db = client.get_database('video_database')
fs_videos = GridFS(video_db)


def calculate_hash(content):
    md5 = hashlib.md5()
    md5.update(content)
    return md5.hexdigest()


def upload_file(file, user):
    try:
        file_id = fs_videos.put(file.file.read(), filename=file.filename)    
    except Exception as err:
        return None, str(err)
            
    try:
        producer = Producer("video_topic")
        producer.emit_event({
            "video_id": str(file_id),
            "user": user
        })
    except Exception as err:
        fs_videos.delete(file_id)
        return None, str(err)
        
    return str(file_id), None
    