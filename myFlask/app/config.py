import json
import pymysql

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