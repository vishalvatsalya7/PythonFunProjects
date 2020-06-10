from src.config import Config
import re
from googleapiclient.discovery import build
from datetime import timedelta
from urllib.parse import parse_qs

#Just give youtube playlist link and get the duration to finish your playlist

class Analytics:
    def __init__(self, link):
        conf = Config()
        self.api_key = conf.get_api()
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.link = link

    def get_playlist_id(self, s):
        x = parse_qs(s)
        return x['list'][0]

    def get_time(self):
        hours_pattern = re.compile(r'(\d+)H')
        minutes_pattern = re.compile(r'(\d+)M')
        seconds_pattern = re.compile(r'(\d+)S')
        id = self.get_playlist_id(self.link)
        nextPageToken = None
        total_seconds = 0
        while True:
            pl_request = self.youtube.playlistItems().list(
                part = 'contentDetails',
                playlistId = id,
                maxResults=50,
                pageToken = nextPageToken
            )
            pl_response = pl_request.execute()

            vid_ids = []
            for item in pl_response['items']:
                vid_id = item['contentDetails']['videoId']
                vid_ids.append(vid_id)

            vid_request = self.youtube.videos().list(
                part = 'contentDetails',
                id = ','.join(vid_ids)
            )

            vid_response = vid_request.execute()
            for item in vid_response['items']:
                duration = item['contentDetails']['duration']

                hours = hours_pattern.search(duration)
                minutes = minutes_pattern.search(duration)
                seconds = seconds_pattern.search(duration)

                hours = int(hours.group(1)) if hours else 0
                minutes = int(minutes.group(1)) if minutes else 0
                seconds = int(seconds.group(1)) if seconds else 0

                video_seconds = timedelta(
                    hours = hours,
                    minutes = minutes,
                    seconds = seconds
                ).total_seconds()
                total_seconds += video_seconds

            nextPageToken = pl_response.get('nextPageToken')
            if not nextPageToken:
                break

        total_seconds = int(total_seconds)

        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return (hours, minutes, seconds)


# Can give any youtube playlist link
youtube_playlist_link = 'https://www.youtube.com/watch?v=Zf1F4cz8GHU&list=PLS1QulWo1RIa7D1O6skqDQ-JZ1GGHKK-K&index=17'
obj = Analytics(youtube_playlist_link)
hour, minute, second = obj.get_time()

