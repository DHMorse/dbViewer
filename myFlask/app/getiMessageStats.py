import sqlite3
import math
from datetime import datetime

def getiMessageStatsFunc(db_path):
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