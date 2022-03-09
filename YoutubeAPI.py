import re
from datetime import timedelta
from googleapiclient.discovery import build

# Enter your API key here.
api_key = 'YOURAPIKEY'

# Indicate which API you're going to use. In this case, YouTube API.
youtube = build('youtube', 'v3', developerKey=api_key)

# Regular expression patterns for hours, minutes, seconds and date.
h_pattern = re.compile(r'(\d+)H')
min_pattern = re.compile(r'(\d+)M')
sec_pattern = re.compile(r'(\d+)S')
date_pattern = re.compile(r'(\d+)-(\d+)-(\d+)')

# Next page token and counters.
next_page_token = None
total_seconds = 0
video_count = 0

while True:
    # Making a request using playlistItems and setting max results to 50 (default: 5)
    playlist_request = youtube.playlistItems().list(
        part='snippet, contentDetails',
        playlistId='PLyORnIW1xT6zC14Z45V6c00JFwRBWdh8P',  # put a playlist ID here
        maxResults=50,
        pageToken=next_page_token
    )

    # Call the execute function to get a response.
    playlist_response = playlist_request.execute()

    video_ids = []

    # Looping through playlist response.
    for item in playlist_response['items']:

        # Use the pattern to get only the date.
        try:
            date = date_pattern.search(item['contentDetails']['videoPublishedAt'])
            date = date.group(0)
        except KeyError:
            date = None

        # Append video IDs to our list.
        video_ids.append(item['contentDetails']['videoId'])

        # Print out the title, link and publishing date of the video.
        print(f"{item['snippet']['title']}")
        print(f"Link: https://www.youtube.com/watch?v={item['contentDetails']['videoId']}")
        print(f"Published at: {date}\n")
        video_count += 1

    # Make another request using video IDs that we previously got.
    video_requests = youtube.videos().list(
        part='contentDetails',
        id=','.join(video_ids)
    )

    video_response = video_requests.execute()

    # Loop and get videos duration, using the patterns, and convert to the seconds.
    for item in video_response['items']:
        duration = item['contentDetails']['duration']

        hours = h_pattern.search(duration)
        minutes = min_pattern.search(duration)
        seconds = sec_pattern.search(duration)

        hours = int(hours.group(1)) if hours else 0
        minutes = int(minutes.group(1)) if minutes else 0
        seconds = int(seconds.group(1)) if seconds else 0

        video_seconds = timedelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        ).total_seconds()

        total_seconds += video_seconds

    # Get nextPageToken if it exists, else break the while loop.
    next_page_token = playlist_response.get('nextPageToken')

    if not next_page_token:
        break

# Convert total seconds from float to int so that we can make calculations.
total_seconds = int(total_seconds)

print('Total videos:', video_count)

# Making our calculations to convert seconds to minutes and minutes to hours.
minutes, seconds = divmod(total_seconds, 60)
hours, minutes = divmod(minutes, 60)

print('Total duration of the playlist: {:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds))

# Close the connection.
youtube.close()

