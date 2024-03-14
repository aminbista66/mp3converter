from pymongo import MongoClient
from gridfs import GridFS
from .producer import Producer
import hashlib
import os


client = MongoClient(os.environ.get("MONGO_URI"))
video_db = client.get_database('video_database')
fs = GridFS(video_db)


def calculate_hash(content):
    md5 = hashlib.md5()
    md5.update(content)
    return md5.hexdigest()


def upload_file(file):
    try:
        file_id = fs.put(file, filename=file.filename)    
    except Exception as err:
        return None, err
    
    try:
        producer = Producer("video_topic")
        producer.emit_event({
            "video_id": file_id
        })
    except Exception as err:
        fs.delete(file_id)
        return None, err
    
    return file_id, None
    