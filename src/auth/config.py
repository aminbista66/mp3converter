from dotenv import load_dotenv, find_dotenv

def load_env(env_filename: str = '.env'):
    load_dotenv(find_dotenv(env_filename))
    return