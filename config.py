# Config file for loading environment variables
from dotenv import load_dotenv
import os


def get_bot_token():
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN not set in .env file")
    return token


def get_weather_api_key():
    load_dotenv()
    key = os.getenv("WEATHER_API_KEY")
    if not key:
        raise ValueError("WEATHER_API_KEY not set in .env file")
    return key


def get_gsheets_credentials_path():
    load_dotenv()
    path = os.getenv("GSHEETS_CREDENTIALS_PATH")
    if not path:
        raise ValueError("GSHEETS_CREDENTIALS_PATH not set")
    return path


# def get_gsheets_token_path():
#     load_dotenv()
#     path = os.getenv("GSHEETS_TOKEN_PATH")
#     if not path:
#         raise ValueError("GSHEETS_TOKEN_PATH not set")
#     return path


def get_serpapi_key():
    load_dotenv()
    key = os.getenv("SERPAPI_KEY")
    if not key:
        raise ValueError("SERPAPI_KEY not set in .env file")
    return key
