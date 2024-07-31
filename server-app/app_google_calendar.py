import time
import schedule
import google_calendar_fetcher
import calendar_image_creator
import convert
import pico_util
import datetime

def map_event(event):  
    return {  
        'summary': event['summary'],  
        'start': sanitize_date(event['start'].get('dateTime', event['start'].get('date'))),
        'end': sanitize_date(event['end'].get('dateTime', event['end'].get('date'))),
        'status': google_calendar_fetcher.get_self_response_status(event)
    }

def sanitize_date(date_str: str):
    # convert date to iso format
    try:
        # Attempt to parse the date string as ISO format
        datetime.datetime.fromisoformat(date_str)
        return date_str  # Already in ISO format
    except ValueError:
        # Not in ISO format, try to parse and reformat
        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.isoformat()
        except ValueError:
            raise ValueError("Invalid date format")


def job():
    events, leave_events = google_calendar_fetcher.fetch_event()
    events = list(map(map_event, events))
    leave_events = list(map(map_event, leave_events))
    file_path = calendar_image_creator.create_calendar_image(events, leave_events)
    sending_file = convert.convert(file_path)
    pico_util.send_file_to_pico('/dev/tty.usbmodem1101', sending_file)

job()
schedule.every(1).hours.do(job)  
while True:  
    schedule.run_pending()  
    time.sleep(1)