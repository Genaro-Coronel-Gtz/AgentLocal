#!/usr/bin/env python3

import os
from pytube import YouTube

def download_youtube_video(url, output_path, download_mp3=False):
    try:
        yt = YouTube(url)
        if download_mp3:
            stream = yt.streams.filter(only_audio=True, file_extension='mp3').first()
            output_path = os.path.splitext(output_path)[0] + '.mp3'
        else:
            stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
        stream.download(output_path=output_path)
        print(f'Video downloaded successfully to {output_path}')
    except Exception as e:
        print(f'Error downloading video: {e}')

if __name__ == '__main__':
    url = input('Enter the YouTube URL: ')
    output_path = input('Enter the output path for the video: ')
    download_mp3 = input('Download as MP3? (yes/no): ').lower() == 'yes'
    download_youtube_video(url, output_path, download_mp3=download_mp3)