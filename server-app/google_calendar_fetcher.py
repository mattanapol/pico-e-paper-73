import datetime  
import os  
import pickle  
import time
from google.oauth2.credentials import Credentials  
from google_auth_oauthlib.flow import InstalledAppFlow  
from google.auth.transport.requests import Request  
from googleapiclient.discovery import build  
  
# If modifying these SCOPES, delete the file token.pickle.  
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
OB_LEAVE_CALENDAR_ID = 'c_a491d065cb2259ea0375b641f8689a69c0996f452a260d8d6095412652b74c19@group.calendar.google.com'
OMS_LEAVE_CALENDAR_ID = 'c_63d754b515ff1daee2f6024ace3f2b4a6a2e7e62cea125e879d8c2ec4b43b1bb@group.calendar.google.com'
PROMOTION_LEAVE_CALENDAR_ID = 'c_b3e01aa8d458ebdf3dc424dca9ad353ec9c898f06bb394c479113bf593da8252@group.calendar.google.com'
  
def authenticate_google_calendar():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                creds = None
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            flow.redirect_uri = 'http://localhost'
            creds = flow.run_local_server()
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds
  
def fetch_calendar_entries(start_date, end_date, calendar_id='primary'):
    creds = authenticate_google_calendar()
    print("Authenticated")
    service = build('calendar', 'v3', credentials=creds)
  
    events_result = service.events().list(calendarId=calendar_id, timeMin=start_date, timeMax=end_date,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    print(f"Found {len(events)} events")
    result = []
  
    if not events:
        print('No upcoming events found.')
    for event in events:
        if event.get('eventType') in ['workingLocation', 'focusTime']:
            continue
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        print(f"Event: {event['summary']}, Organizer: {event.get('organizer', {}).get('email', 'N/A')}, Start: {start}, End: {end}, Status: {get_self_response_status(event)}, Event type: {event.get('eventType', 'N/A')}")
        # print(event)
        result.append(event)
    return result

def get_self_response_status(event):
    attendees = event.get('attendees', [])
    for attendee in attendees:
        if attendee.get('self', False):
            return attendee.get('responseStatus')

def fetch_calendar_list():
    creds = authenticate_google_calendar()
    print("Authenticated")
    service = build('calendar', 'v3', credentials=creds)
  
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            print(calendar_list_entry)
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

def fetch_event():  
    # Define your start and end date here  
    start_date = datetime.datetime.now(datetime.timezone.utc).astimezone()
    end_date = start_date + datetime.timedelta(days=1)
    primary_entries = fetch_calendar_entries(start_date.isoformat(), end_date.isoformat())
    ob_leave_entries = fetch_calendar_entries(start_date.isoformat(), end_date.isoformat(), OB_LEAVE_CALENDAR_ID)
    oms_leave_entries = fetch_calendar_entries(start_date.isoformat(), end_date.isoformat(), OMS_LEAVE_CALENDAR_ID)
    promotion_leave_entries = fetch_calendar_entries(start_date.isoformat(), end_date.isoformat(), PROMOTION_LEAVE_CALENDAR_ID)
    leave_entries = ob_leave_entries + oms_leave_entries + promotion_leave_entries
    return primary_entries, leave_entries

if __name__ == "__main__":
    fetch_event()