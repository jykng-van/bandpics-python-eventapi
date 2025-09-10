import os
from dotenv import load_dotenv
import requests

#get concert data from a variety of external APIs
class ExternalInfo:

    def __init__(self):
        load_dotenv() # load environment variable from .env

    def get_info(self, source):
        print('retrieving from:', source)