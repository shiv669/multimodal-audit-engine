'''
this is the connector between the python and indexer service
'''

import os
import time
import yt_dlp
import requests
import logging
import json
import whisper
import pytesseract
import cv2


logger = logging.getLogger("video-indexer")

class videoIndexerService:
    def __init__(self):
        logger.info("video indexing started")


    def download_youtube_video(self, url, output_path="temp_video.mp4"):
        '''
        downloads the youtube video locally on the device
        '''
        logger.info(f"downloading the youtube video {url}")

        ydl_opts = {
            "format" : 'best[ext=mp4]',
            'outtmpl' : output_path,
            'quiet' : True,
            'overwrites' : True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                logger.info("download completed")
                return output_path
        except Exception as e:
            raise Exception(f"failed to download the video : {str(e)}")
        
    def extract_video_data(self, local_path, video_id):
        '''
        exract transcript and ocr from the video
        '''
        logger.info(f"extracting data from {video_id}")
        try:
            logger.info("loading whisper model")
            model = whisper.load_model("base")

            logger.info("transcribing audio")
            result = model.transcribe(local_path)
            transcript = result["text"]
            logger.info("transcription completed")

            logger.info("extracting frames to run ocr")
            ocr_text = []

            video = cv2.VideoCapture(local_path)
            frame_count = 0

            while True:
                ret, frame = video.read()

                if not ret:
                    break

                if frame_count % 10 == 0:
                    text = pytesseract.image_to_string(frame)
                    if text.strip():
                        ocr_text.append(text)
                
                frame_count = frame_count + 1

            video.release()
            logger.info("ocr extraction successful")

            return {
                "transcript" : transcript,
                "ocr_text" : ocr_text
            }
        
        except Exception as e:
            logger.error(f"failed to extarct video data {str(e)}")
            raise Exception(f"extraction failed {str(e)}")
        
    def extract_data(self, raw_insights):
        '''
        clean and format data for the audit pipeline
        '''
        try:
            transcript = raw_insights.get("transcript", "")

            ocr = raw_insights.get("ocr_text", [])

            return {
                "video_transcript" : transcript,
                "ocr_text" : ocr
            }
        
        except Exception as e:
            logger.error(f"failed to format extracted data {str(e)}")
            raise Exception(f"formatting failed due to : {str(e)}")