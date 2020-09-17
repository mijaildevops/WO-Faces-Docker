# DB
import pymysql

# DB Settings
StringDB = [
    #"128.199.15.192", # Server
    "192.168.100.50", # Server
    "WO.Test", # User
    "DB.Learing", # Pass
    "WO-Faces", # DB
]

# Connect to the database
connection = pymysql.connect(host=StringDB[0],
                    user=StringDB[1],
                    password=StringDB[2],
                    db=StringDB[3],
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor)

# Server
server = '192.168.100.3'

# Cognitive-Services
SUBSCRIPTION_KEY = 'ad421b0ac53b4d7e9d38cc94f9877fd9'
BASE_URL = 'https://eastus.api.cognitive.microsoft.com/face/v1.0/'