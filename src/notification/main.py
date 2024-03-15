from consumer import MP3Consumer
from dotenv import find_dotenv, load_dotenv


if __name__ == "__main__":
    load_dotenv(find_dotenv())
    consumer = MP3Consumer()
    consumer.run()