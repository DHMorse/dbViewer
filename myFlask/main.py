from flask import Flask, render_template
import paramiko
from scp import SCPClient
import os

from app.getiMessageStats import getiMessageStatsFunc
from app.getDiscordStats import getDiscordStatsFunc

from app.getDiscordLongestStreak import getLongestDiscordStreakFunc
from app.getiMessageLongestStreak import getiMessageLongestStreakFunc

from app.getiMessageCurrentStreak import getiMessageCurrentStreakFunc

from app.config import REMOTE_HOST, REMOTE_USER, REMOTE_PASSWORD, REMOTE_FILE_PATH, DB_PATH

# Initialize Flask app
app = Flask(__name__)

def downloadDB(remote_host=REMOTE_HOST, remote_user=REMOTE_USER, remote_password=REMOTE_PASSWORD, remote_file_path=REMOTE_FILE_PATH, local_file_path=DB_PATH):
    try:
        if os.path.exists(local_file_path):
            print(f"Removing existing file: {local_file_path}")
            os.remove(local_file_path)

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=remote_host, username=remote_user, password=remote_password)

        with SCPClient(ssh.get_transport()) as scp:
            scp.get(remote_file_path, local_file_path)

        print(f"File {remote_file_path} copied to {local_file_path}")

    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        ssh.close()

# Route for the homepage
@app.route("/")
def index():
    discordMessageStats = getDiscordStatsFunc()
    discordLongestStreak = getLongestDiscordStreakFunc()

    downloadDB()
    iMessagePersonData = getiMessageStatsFunc(DB_PATH)
    iMessageLongestStreak = getiMessageLongestStreakFunc(DB_PATH)
    iMessageCurrentStreak = getiMessageCurrentStreakFunc(DB_PATH)

    return render_template("index.html", 
                            discordMessageStats=discordMessageStats, 
                            discordLongestStreak=discordLongestStreak, 
                            iMessagePersonData=iMessagePersonData, 
                            iMessageLongestStreak=iMessageLongestStreak, 
                            iMessageCurrentStreak=iMessageCurrentStreak
                        )

if __name__ == "__main__":
    app.run(debug=True)