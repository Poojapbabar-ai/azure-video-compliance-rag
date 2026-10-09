#Video indexer : 


'''
Connector : python and Azure video Indexer
'''

import os 
import time
import logging
import requests
import yt_dlp
from azure.identity import DefaultAzureCredential


logger = logging.getLogger("Video_Indexer")



class VideoIndexService:
    def __init__(self):
        self.account_id = os.getenv("AZURE_VI_ACCOUNT_ID")
        self.location = os.getenv("AZURE_VI_LOCATION")
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        self.resource_group = os.getenv("AZURE_RESOURCE_GROUP")
        self.vi_name = os.getenv("AZURE_VI_NAME")
        self.credential = DefaultAzureCredential()


    def get_access_token(self):
        '''
        Generates an ARM  ACCESS TOKEN
        '''
        try:
            token_object = self.credential.get_token("https://management.azure.com/.default")
            return token_object.token
        except Exception as e:
            logger.error(f"Failed  to get Azure token : {e}")
            raise

    def get_account_token(self,arm_access_token):
        '''
        Exchange  the ARM token for Video Indexer account team
        '''
        url = (
            f"https://management.azure.com/subscriptions/{self.subscription_id}"
            f"/resourceGroups/{self.resource_group}"
            f"/providers/Microsoft.VideoIndexer/accounts/{self.vi_name}"
            f"/generateAccessToken?api-version=2025-04-01"
        )

        headers = {"Authorization" : f"Bearer {arm_access_token}"}
        payload = {"permissionType":"Contributor","scope":"Account"}
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to get VI Account token :{response.text}")
        return response.json().get("accessToken")


    # Function to download youtbe url


    def download_youtube_video(self,url,output_path ="temp_video.mp4"):
        # '''
        # Docstring for download_youtube_video

        # :param self:Description
        # :param url : Description 
        # :param output : Description
        # '''
        """Download a Youtube Video to a local file."""
        logger.info(f"Downloading the youtube video : {url}")

        ydl_opts = {
            "format": 'best',
            'outtmpl':output_path,#output template
            'quiet' :False, #control console output
            'no warnings':False, #control warning

            'extractor_args':{'youtube':{'player_client':['android','web']}}, 

            'http_headers':{
                'User-Agent' : 'Mozilla/5.0  (Windows NT 10.0; Win64; x64)  AppleWebKit/537.36'
            }


        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            logger.info("Download complete")
            return output_path

        except Exception as e:
            raise Exception(f"Youtube  video Download Failed :{str(e)}")


# Upload the video to Azure Video Indexer
    def upload_video(self, video_path, video_name):
        arm_token = self.get_access_token()
        vi_token = self.get_account_token(arm_token)

        api_url = f"https://api.videoindexer.ai/{self.location}/Accounts/{self.account_id}/Videos"
        params = {
            "accessToken": vi_token,
            "name": video_name,
            "privacy": "Private",
            "indexPresent": "Default",
        }
        logger.info(f"Uploading the file {video_path} to Azure....")

        with open(video_path, "rb") as video_file:
            response = requests.post(
                api_url,
                params=params,
                files={"file": video_file},
                timeout=300,
            )

        if response.status_code not in (200, 201):
            raise Exception(f"Azure upload failed: {response.text}")

        payload = response.json()
        return payload.get("id") or payload.get("videoId") or video_name

    def upload_video_to_azure(self, video_path, video_name):
        return self.upload_video(video_path, video_name)

    def wait_for_processing(self, video_id):
        logger.info(f"Waiting for the video {video_id} to process...")
        while True:
            arm_token = self.get_access_token()
            vi_token = self.get_account_token(arm_token)
            url = (
                f"https://api.videoindexer.ai/{self.location}/Accounts/"
                f"{self.account_id}/Videos/{video_id}/Index"
            )
            response = requests.get(
                url,
                params={"accessToken": vi_token},
                timeout=30,
            )
            if response.status_code != 200:
                raise Exception(f"Failed to get Video Indexer status: {response.text}")

            data = response.json()
            state = data.get("state")
            if state == "Processed":
                return data
            if state == "Failed":
                raise Exception("Video indexing failed in Azure")
            if state == "Quarantined":
                raise Exception("Video quarantined (copyright/content policy violation)")

            logger.info(f"Status {state}; waiting 30 seconds")
            time.sleep(30)

    def extract_data(self, vi_json):
        """Parse Video Indexer JSON into the workflow state format."""
        transcript_lines = []
        ocr_lines = []
        for video in vi_json.get("videos", []):
            insights = video.get("insights", {})
            transcript_lines.extend(
                item.get("text", "")
                for item in insights.get("transcript", [])
                if item.get("text")
            )
            ocr_lines.extend(
                item.get("text", "")
                for item in insights.get("ocr", [])
                if item.get("text")
            )

        return {
            "transcript": " ".join(transcript_lines),
            "ocr_text": ocr_lines,
            "video_metadata": {
                "duration": vi_json.get("summarizedInsights", {}).get("duration"),
                "platform": "youtube",
            },
        }


        
