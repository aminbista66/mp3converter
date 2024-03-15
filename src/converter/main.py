from dotenv import load_dotenv, find_dotenv
from consumer import VideoConsumer
from pymongo import MongoClient
from gridfs import GridFS
import os

if __name__ == "__main__":
    load_dotenv(find_dotenv())
    print("Connecting to db...")
    client = MongoClient(os.environ.get("MONGO_URI"))
    video_db = client.get_database("video_database")
    mp3_db = client.get_database("mp3_db")
    fs_videos = GridFS(video_db)
    fs_mp3s = GridFS(mp3_db)
    print("Db connected !!")


    consumer = VideoConsumer()
    consumer.run(fs_videos, fs_mp3s)