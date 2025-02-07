import sqlite3
import win32evtlog
from datetime import datetime, timedelta
from enableEV import enable_failed_login_auditing
import pandas as pd
import json
# Function to check if the timestamp is within custom business hours
def is_business_hours(timestamp, business_start_hour=9, business_end_hour=18):
    # Set the custom business start and end times
    business_start = timestamp.replace(hour=business_start_hour, minute=0, second=0, microsecond=0)
    business_end = timestamp.replace(hour=business_end_hour, minute=0, second=0, microsecond=0)
    return business_start <= timestamp <= business_end

def extract_login_data(log_type="Security", days_back=0, business_start_hour=9, business_end_hour=18):
    server = "localhost"  # Local machine
    log_handle = win32evtlog.OpenEventLog(server, log_type)

    events = []
    total = win32evtlog.GetNumberOfEventLogRecords(log_handle)

    chunk_size = 10
    end_date = datetime.now()  # Current date
    start_date = end_date - timedelta(days=days_back)  # Calculate the start date

    while True:
        events_chunk = win32evtlog.ReadEventLog(
            log_handle,
            win32evtlog.EVENTLOG_SEQUENTIAL_READ | win32evtlog.EVENTLOG_FORWARDS_READ,
            0
        )
        if not events_chunk:
            break

        for event in events_chunk:
            event_id = event.EventID
            timestamp = event.TimeGenerated
            timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')

            # Only include events that occurred within the specified date range
            if timestamp < start_date:
                continue  # Skip this event if it's outside the date range

            event_data = {
                "timestamp": timestamp_str,
                "event_id": event_id,
                "message": event.StringInserts if event.StringInserts else []
            }

            # Determine if the event occurred during custom business hours
            business_hours = 1 if is_business_hours(timestamp, business_start_hour, business_end_hour) else 0

            # Filtering for logon events (4624 = Successful logon, 4625 = Failed logon, 4634 = Logoff)
            if event_id == 4624:  # Successful logon
                logon_type = event_data["message"][8] if len(event_data["message"]) > 8 else None
                user = event_data["message"][5] if len(event_data["message"]) > 5 else None
                status = "Success"
                event_data.update({
                    "logon_type": logon_type,
                    "user": user,
                    "status": status,
                    "business_hours": business_hours
                })
                events.append(event_data)

            elif event_id == 4625:  # Failed logon
                user = event_data["message"][5] if len(event_data["message"]) > 5 else None
                status = "Failed"
                event_data.update({
                    "user": user,
                    "status": status,
                    "business_hours": business_hours
                })
                events.append(event_data)

            elif event_id == 4634:  # Logoff
                user = event_data["message"][5] if len(event_data["message"]) > 5 else None
                status = "Logoff"
                event_data.update({
                    "user": user,
                    "status": status,
                    "business_hours": business_hours
                })
                events.append(event_data)

    return events

def save_to_csv_from_db(filename="login_data.csv"):
    conn = sqlite3.connect("logguard.db")
    cursor = conn.cursor()

    # Query to fetch the data
    cursor.execute("SELECT status,is_rapid_logon,is_business_hours,risk_score FROM login_events")
    rows = cursor.fetchall()

    # Create a pandas DataFrame from the fetched rows
    df = pd.DataFrame(rows, columns=["status", "is_rapid_logon", "is_business_hours", "risk_score",])

    # Replace business_hours with 1 or 0 (1 for business hours, 0 otherwise)
    df['is_business_hours'] = df['is_business_hours'].apply(lambda x: 1 if x == 1 else 0)

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Open the CSV file and save the DataFrame directly to the CSV
    df.to_csv(filename, index=False)  # No header, as it's already handled by pandas

    conn.close()

def create_login_table():
    conn = sqlite3.connect("logguard.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event_type TEXT,
            user TEXT,
            domain TEXT,
            user_sid TEXT,
            logon_type TEXT,
            status TEXT,
            failure_reason TEXT,
            logon_id TEXT,
            session_duration INTEGER,
            source_ip TEXT,
            workstation_name TEXT,
            is_business_hours INTEGER,
            is_rapid_logon INTEGER,
            day_of_week INTEGER,
            hour_of_day INTEGER,
            risk_score REAL,
            event_id INTEGER,
            event_task_category TEXT
        )
    """)

    conn.commit()
    conn.close()


def insert_login_data(login_data):
    conn = sqlite3.connect("logguard.db")
    cursor = conn.cursor()

    for log in login_data:
        cursor.execute("""
            INSERT INTO login_events (
                timestamp, event_type, user, domain, user_sid, logon_type, status, 
                failure_reason, logon_id, session_duration, source_ip, workstation_name, 
                is_business_hours, is_rapid_logon, day_of_week, hour_of_day, 
                risk_score, event_id, event_task_category
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            log["timestamp"], log.get("event_type", "N/A"), log.get("user", "N/A"),
            log.get("domain", "N/A"), log.get("user_sid", "N/A"), log.get("logon_type", "N/A"),
            log["status"], log.get("failure_reason", "N/A"), log.get("logon_id", "N/A"),
            log.get("session_duration", 0), log.get("source_ip", "N/A"), log.get("workstation_name", "N/A"),
            log.get("is_business_hours", 0), log.get("is_rapid_logon", 0),
            log.get("day_of_week", 0), log.get("hour_of_day", 0),
            log.get("risk_score", 0.0), log["event_id"], log.get("event_task_category", "N/A")
        ))

    conn.commit()
    conn.close()


from datetime import datetime, timedelta
from collections import deque


def is_rapid_logon(logs, user, timestamp, threshold_minutes=10):
    """
    Determines if a user logs in multiple times within a short period (e.g., 10 minutes).
    Returns 1 if the login is considered rapid, otherwise 0.
    """
    # Ensure timestamp is a datetime object
    if isinstance(timestamp, str):
        timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

    threshold_time = timedelta(minutes=threshold_minutes)
    user_logins = deque(maxlen=2)  # Store only the last 2 logins for efficiency

    for log in logs:
        if log["user"] == user:
            prev_timestamp = datetime.strptime(log["timestamp"], '%Y-%m-%d %H:%M:%S')
            user_logins.append(prev_timestamp)

            # If there are at least two logins, check the time difference
            if len(user_logins) == 2 and (timestamp - user_logins[0]) <= threshold_time:
                return 1  # Rapid logon detected

    return 0


def calculate_risk_score(log):
    """
    Calculates a risk score based on multiple factors:
    - Failed login attempts increase risk
    - Rapid logins increase risk
    - Unusual logon type may increase risk
    - Unfamiliar source IP increases risk
    """
    risk_score = 0.0

    # Assign weights to risk factors
    if log["status"] == "Failed":
        risk_score += 0.4  # Failed login attempts are riskier

    if log["is_rapid_logon"]:
        risk_score += 0.3  # Frequent logins within a short period are suspicious

    if log["logon_type"] not in ["2", "3", "10"]:
        risk_score += 0.2  # Uncommon logon types increase risk

    if log["source_ip"] not in ["192.168.1.1", "127.0.0.1"]:
        risk_score += 0.1  # Unrecognized IP addresses increase risk

    return min(risk_score, 1.0)  # Ensure the score is between 0 and 1

# Main function to run the process
def main():
    with open('config.json', 'r') as file:
        data = json.load(file)

    # Accessing working hours
    working_hours = data["working_hours"]
    business_start_hour = int(working_hours["start_hour"])
    business_end_hour = int(working_hours["end_hour"])

    enable_failed_login_auditing()  # Enable failed login auditing
    login_data = extract_login_data(days_back=1, business_start_hour=business_start_hour, business_end_hour=business_end_hour)  # Get the login data for 4 days back
    # for i in login_data:
    #     print(i)
    create_login_table()

    insert_login_data(login_data)  # Insert the data into the database
    save_to_csv_from_db()  # Save the data to a CSV file
    # make data in proper format
    # new function that passes the csv file data to ml model and give back response
if __name__ == "__main__":
    main()