import pika, json

def upload(file, fs, channel):
    try:
        fid = fs.put(file)
    except Exception as err:
        print(str(err))
        return "internal server error", 500
    
    message = {
        "video_fid": fid,
        "mp3_fid": None,
    }

    try:
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as err:
        print(err)
        fs.delete(fid)
        return "internal server error", 500