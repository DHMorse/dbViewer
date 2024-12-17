import json
import pymysql

REMOTE_HOST = 'raspberrypi'
REMOTE_USER = 'danielpi'
REMOTE_PASSWORD = 'password'
REMOTE_FILE_PATH = '/home/danielpi/Documents/httpServer/iMessagelog.db'

DB_PATH = '/home/daniel/Documents/myCode/dbViewer/myFlask/iMessagelog.db'

# Connect to MariaDB database
def getDbConnection():
    with open("../secrets.json") as f:
        secrets = json.load(f)
        return pymysql.connect(
            user=secrets["user"],
            password=secrets["password"],
            host=secrets["host"],
            port=secrets.get("port", 3306),
            database=secrets["database"]
        )