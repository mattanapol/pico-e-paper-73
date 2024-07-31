from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# Sample events
test_events = [
    {"start": "2024-07-30T15:00:00+07:00", "end": "2024-07-30T15:00:00+07:00", "summary": "Event 1 อีเวนท์ 1", "status": "accepted"},
    {"start": "2024-07-30T16:00:00+07:00", "end": "2024-07-30T16:00:00+07:00", "summary": "Event 2 อีเวนท์ 2", "status": "needsAction"},
    {"start": "2024-07-30T17:00:00+07:00", "end": "2024-07-30T17:00:00+07:00", "summary": "Event 3 อีเวนท์ 3", "status": "needsAction"},
    {"start": "2024-07-29T18:00:00+07:00", "end": "2024-07-30T18:00:00+07:00", "summary": "Event 4 อีเวนท์ 4", "status": "accepted"},
    {"start": "2024-07-30T19:00:00+07:00", "end": "2024-07-30T19:00:00+07:00", "summary": "Event 5 อีเวนท์ 5", "status": "accepted"},
    {"start": "2024-07-30T20:00:00+07:00", "end": "2024-07-30T20:00:00+07:00", "summary": "Event 6 อีเวนท์ 6", "status": "accepted"},
    {"start": "2024-07-31T21:00:00+07:00", "end": "2024-07-31T21:00:00+07:00", "summary": "Event 7 อีเวนท์ 7", "status": "accepted"},
]
test_leave_events = [
    {"start": "2024-07-30", "end": "2024-07-31", "summary": "ESS Leave 1", "status": "accepted"},
    {"start": "2024-07-29T16:00:00+07:00", "end": "2024-07-29T16:01:00+07:00", "summary": "Bee Leave 2", "status": "needsAction"},
    {"start": "2024-07-30T17:00:00+07:00", "end": "2024-07-30T17:00:00+07:00", "summary": "Promotion Leave 3", "status": "needsAction"},
    {"start": "2024-07-29T18:00:00+07:00", "end": "2024-07-30T18:00:00+07:00", "summary": "OB Leave 4", "status": "accepted"},
    {"start": "2024-07-30T19:00:00+07:00", "end": "2024-07-30T19:00:00+07:00", "summary": "OMS Leave 5", "status": "accepted"},
    {"start": "2024-07-27", "end": "2024-07-30", "summary": "Promotion Leave 6", "status": "accepted"},
    {"start": "2024-07-31T21:00:00+07:00", "end": "2024-07-31T21:00:00+07:00", "summary": "OB Leave 7", "status": "accepted"},
]

# Constants
IMAGE_WIDTH = 800
IMAGE_HEIGHT = 480
MAX_EVENTS_DISPLAY = 8
EVENT_HEIGHT = IMAGE_HEIGHT // MAX_EVENTS_DISPLAY
FONT_SIZE = 30
LEAVE_FONT_SIZE = 25
EMOJI_FONT_SIZE = 32
Y_OFFSET = 7
FONT_PATH = "/System/Library/Fonts/Supplemental/SukhumvitSet.ttc"
EMOJI_FONT_PATH = "/System/Library/Fonts/Apple Color Emoji.ttc"

# Function to format time
def format_time(dt_str):
    dt = datetime.fromisoformat(dt_str)
    return dt.strftime("%H:%M")

def format_date(dt_str):
    dt = datetime.fromisoformat(dt_str)
    return dt.strftime("%d %b, %a")

def get_date(dt_str):
    dt = datetime.fromisoformat(dt_str)
    return dt.strftime("%Y-%m-%d")

def calculate_vertical_position(y_position, font: ImageFont.FreeTypeFont):
    text_height = font.getmetrics()[0]
    return y_position - Y_OFFSET + (EVENT_HEIGHT - text_height) // 2

def draw_text(draw, position, text, font, fill="black"):
    draw.text(position, text, fill=fill, font=font, stroke_width=1, stroke_fill=fill)

def draw_subtext(draw, position, text, font, fill="black"):
    draw.text(position, text, fill=fill, font=font)

def get_emoji_status(status):
    if status == "accepted":
        return "✅"
    elif status == "needsAction":
        return "🤔"
    else:
        return "❌"

def get_leave_event_on_date(events, date):
    # filter events that date is between start and end
    return [event for event in events if (event["start"] <= date and event["end"] > date) or event["start"].startswith(date)]

def get_summary_list_as_string(events):
    return ", ".join([event["summary"] for event in events])

def sanitize_date(date_str: str):
    # convert date to iso format
    try:
        # Attempt to parse the date string as ISO format
        datetime.fromisoformat(date_str)
        return date_str  # Already in ISO format
    except ValueError:
        # Not in ISO format, try to parse and reformat
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.isoformat()
        except ValueError:
            raise ValueError("Invalid date format")

def create_calendar_image(events, leave_events):
    events.sort(key=lambda e: sanitize_date(e["start"]))
    leave_events.sort(key=lambda e: sanitize_date(e["start"]))

    # Create an image with white background
    image = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), "white")
    draw = ImageDraw.Draw(image)

    # Track the current date
    current_date = None
    y_position = 0
    font = None
    leave_font = None
    
    emoji_font = ImageFont.truetype(EMOJI_FONT_PATH, EMOJI_FONT_SIZE)
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        leave_font = ImageFont.truetype(FONT_PATH, LEAVE_FONT_SIZE)
    except IOError:
        print("Font file not found. Using default font.")
        font = ImageFont.load_default(FONT_SIZE)
        leave_font = ImageFont.load_default(LEAVE_FONT_SIZE)

    # Draw events
    for i, event in enumerate(events[:MAX_EVENTS_DISPLAY]):
        event_date = format_date(event["start"])

        if event_date != current_date:
            # Draw date change marker
            current_date = event_date
            leave_event_string = get_summary_list_as_string(get_leave_event_on_date(leave_events, get_date(event["start"])))
            draw_text(draw, (15, calculate_vertical_position(y_position, font)), current_date, font)
            if leave_event_string:
                draw_subtext(draw, (190, calculate_vertical_position(y_position + 7, font)), leave_event_string, leave_font)
            y_position += EVENT_HEIGHT

        
        text_y_position = calculate_vertical_position(y_position, font)

        # Draw event status
        status_text = get_emoji_status(event["status"])
        status_position = (15, text_y_position + 8)
        draw.text(status_position, status_text, embedded_color=True, font=emoji_font)
        
        # Time column
        time_text = f"{format_time(event['start'])}-{format_time(event['end'])}"
        time_position = (55, text_y_position)
        draw_text(draw, time_position, time_text, font)
        
        # Event name column
        event_text_x = IMAGE_WIDTH // 4 + 20
        name_text = event["summary"]
        event_position = (event_text_x, text_y_position)
        draw_text(draw, event_position, name_text, font)

        y_position += EVENT_HEIGHT
        if y_position >= IMAGE_HEIGHT:
            break

    # Save the image
    output_filename = "events_image.png"
    image.save(output_filename)
    print(f"Image saved as {output_filename}")
    return output_filename

if __name__ == "__main__":
    create_calendar_image(test_events, test_leave_events)