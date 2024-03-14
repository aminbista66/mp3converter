from pymongo import MongoClient
from gridfs import GridFS
from .producer import Producer
import hashlib
import os


client = MongoClient("mongodb://root:example@localhost:27017/file_db?authSource=admin")
video_db = client.get_database('video_database')
fs = GridFS(video_db)


def calculate_hash(content):
    md5 = hashlib.md5()
    md5.update(content)
    return md5.hexdigest()


def upload_file(file):
    try:
        file_id = fs.put(file.file.read(), filename=file.filename)    
    except Exception as err:
        return None, str(err)
        
    try:
        producer = Producer("video_topic")
        producer.emit_event({
            "video_id": str(file_id)
        })
    except Exception as err:
        fs.delete(file_id)
        return None, str(err)
        
    return str(file_id), None
    