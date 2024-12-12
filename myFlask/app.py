from flask import Flask, render_template
import json
import pymysql
from datetime import datetime
from collections import defaultdict

# Load secrets from secrets.json
with open("../secrets.json") as f:
    secrets = json.load(f)

# Initialize Flask app
app = Flask(__name__)

# Connect to MariaDB database
def get_db_connection():
    return pymysql.connect(
        user=secrets["user"],
        password=secrets["password"],
        host=secrets["host"],
        port=secrets.get("port", 3306),
        database=secrets["database"]
    )

def fetch_message_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT username, COUNT(*) as total_msgs, MIN(time), MAX(time) FROM messages GROUP BY username"
    cursor.execute(query)

    person_data = {}
    for username, total_msgs, first_time, last_time in cursor.fetchall():
        if first_time and last_time:
            days_active = (last_time - first_time).days + 1
            months_active = days_active / 30
            average_day = total_msgs / days_active
            average_month = total_msgs / months_active
        else:
            average_day = average_month = 0

        person_data[username] = (total_msgs, average_month, average_day)

    conn.close()
    return sorted(person_data.items(), key=lambda item: item[1][0], reverse=True)


# Route for the homepage
@app.route("/")
def index():
    person_data = fetch_message_data()
    return render_template("index.html", person_data=person_data)

if __name__ == "__main__":
    app.run(debug=True)
