from flask import Flask, render_template
import json
import pymysql
from datetime import datetime, timedelta
from collections import defaultdict
from pytz import timezone
import paramiko
from scp import SCPClient
import sqlite3
import math

def downloadDB(remote_host='raspberrypi', remote_user='danielpi', remote_password='password', remote_file_path='/home/danielpi/Documents/httpServer/iMessagelog.db', local_file_path='/home/daniel/Documents/myCode/dbViewer/myFlask/iMessagelog.db'):
    try:
        # Create an SSH client
        ssh = paramiko.SSHClient()

        # Automatically add host key if not in known_hosts
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the remote host
        ssh.connect(hostname=remote_host, username=remote_user, password=remote_password)

        # Use SCPClient to copy the file
        with SCPClient(ssh.get_transport()) as scp:
            scp.get(remote_file_path, local_file_path)

        print(f"File {remote_file_path} copied to {local_file_path}")

    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        # Close the SSH connection
        ssh.close()

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

def get_contact_message_stats(db_path='/home/daniel/Documents/myCode/dbViewer/myFlask/iMessagelog.db'):
    """
    Analyze iMessage statistics from the provided database.
    
    Args:
        db_path (str): Path to the SQLite database file
    
    Returns:
        List of tuples with contact name and message statistics, 
        sorted from greatest total messages to least
    """
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query to get message statistics per contact, pre-sorted by total messages
    query = """
    SELECT 
        contactName, 
        COUNT(*) as total_messages,
        MIN(secondsSinceEpoch) as earliest_timestamp,
        MAX(secondsSinceEpoch) as latest_timestamp
    FROM imessages
    GROUP BY contactName
    ORDER BY total_messages DESC
    """
    
    # Execute the query
    cursor.execute(query)
    contacts = cursor.fetchall()
    
    # Process and calculate statistics
    contact_stats = []
    for contact, total_msgs, earliest_ts, latest_ts in contacts:
        # Calculate total messages
        total_messages = str(total_msgs)
        
        # Calculate total days and months
        if earliest_ts and latest_ts:
            # Convert timestamps to days
            start_date = datetime.fromtimestamp(earliest_ts)
            end_date = datetime.fromtimestamp(latest_ts)
            total_days = max(1, (end_date - start_date).days + 1)
            total_months = max(1, math.ceil(total_days / 30))
            
            # Calculate averages
            avg_msgs_per_month = "{:.2f}".format(total_msgs / total_months)
            avg_msgs_per_day = "{:.2f}".format(total_msgs / total_days)
        else:
            # Fallback if timestamp data is incomplete
            avg_msgs_per_month = "0.00"
            avg_msgs_per_day = "0.00"
        
        # Create the tuple for this contact
        contact_stat = (
            contact, 
            (
                total_messages, 
                avg_msgs_per_month, 
                avg_msgs_per_day
            )
        )
        contact_stats.append(contact_stat)
    
    # Close the database connection
    conn.close()
    
    return contact_stats

def fetch_message_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT username, COUNT(*) as total_msgs, MIN(time), MAX(time) FROM messages GROUP BY username"
    cursor.execute(query)
    person_data = {}
    
    for username, total_msgs, first_time, last_time in cursor.fetchall():
        if first_time and last_time:
            # Calculate actual months active
            days_active = (last_time - first_time).days + 1
            months_active = max(days_active / 30, 1)  # Ensure at least 1 month
            
            # More precise monthly average calculation
            average_month = total_msgs / months_active
            average_day = total_msgs / days_active
        else:
            average_day = average_month = 0
        
        # Store data with formatted numbers
        person_data[username] = (
            f"{total_msgs:,}",  # Total messages with commas
            f"{average_month:.2f}",  # Monthly average with 2 decimal places
            f"{average_day:.2f}"  # Daily average with 2 decimal places
        )
    
    conn.close()
    return sorted(person_data.items(), key=lambda item: int(item[1][0].replace(',', '')), reverse=True)

def find_longest_streak():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get unique usernames
    cursor.execute("SELECT DISTINCT username FROM messages")
    usernames = [row[0] for row in cursor.fetchall()]
    
    # Track and find streaks
    streak_data = []
    today = datetime.now(timezone('US/Central')).date()  # Today's date in CST
    
    for username in usernames:
        # Query to get sorted unique dates for the user
        query = """
        SELECT DISTINCT DATE(time) as message_date 
        FROM messages 
        WHERE username = %s 
        ORDER BY message_date
        """
        cursor.execute(query, (username,))
        
        date_list = [row[0] for row in cursor.fetchall()]
        
        if not date_list:
            streak_data.append((username, 0, None, None, False))
            continue
        
        # Streak calculation logic
        longest_streak = 1
        current_streak = 1
        streak_start = date_list[0]
        longest_start = longest_end = streak_start

        for i in range(1, len(date_list)):
            if date_list[i] - date_list[i-1] == timedelta(days=1):
                current_streak += 1
            else:
                if current_streak > longest_streak:
                    longest_streak = current_streak
                    longest_start = streak_start
                    longest_end = date_list[i-1]
                current_streak = 1
                streak_start = date_list[i]
        
        # Final streak check
        if current_streak > longest_streak:
            longest_streak = current_streak
            longest_start = streak_start
            longest_end = date_list[-1]
        else:
            longest_end = longest_end  # Retain the end of the longest streak

        # Check if the longest streak is current
        is_current_streak = longest_end == today

        streak_data.append((username, longest_streak, longest_start, longest_end, is_current_streak))
    
    conn.close()
    return sorted(streak_data, key=lambda x: x[1], reverse=True)



# Route for the homepage
@app.route("/")
def index():
    person_data = fetch_message_data()
    streak_data = find_longest_streak()
    iMessagePersonData = get_contact_message_stats()
    print(iMessagePersonData)
    return render_template("index.html", person_data=person_data, streak_data=streak_data, iMessagePersonData=iMessagePersonData)

if __name__ == "__main__":
    app.run(debug=True)