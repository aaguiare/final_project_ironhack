import openrouteservice
from openrouteservice import convert
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('token')

client = openrouteservice.Client(key=api_key)

