from app.config import getDbConnection

def getDiscordStatsFunc():
    conn = getDbConnection()
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