import json, tempfile, os
from bson.objectid import ObjectId
import moviepy.editor
from producer import Producer
from gridfs import GridFS

def start(message, fs_videos: GridFS, fs_mp3s: GridFS):
    message = json.loads(message)

    # empty temp file
    tf = tempfile.NamedTemporaryFile()
    # video contents
    out = fs_videos.get(ObjectId(message["video_id"]))
    # add video contents to empty file
    tf.write(out.read())
    # create audio from temp video file
    audio = moviepy.editor.VideoFileClip(tf.name).audio
    tf.close()

    # write audio to the file
    tf_path = tempfile.gettempdir() + f"/{message['video_id']}.mp3"

    if audio:
        audio.write_audiofile(tf_path)

    # save file to mongo
    f = open(tf_path, "rb")
    data = f.read()
    fid = fs_mp3s.put(data)
    f.close()
    os.remove(tf_path)


    try:
        producer = Producer("mp3_topic")
        producer.emit_event({
            "mp3_id": str(fid)
        })
    except Exception as err:
        fs_mp3s.delete(fid)
        return "failed to emit event"
