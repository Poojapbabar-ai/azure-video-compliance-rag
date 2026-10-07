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
        self.subscription_id = os.get("AZURE_SUBSCRIPTION_ID")
        self.resouce_group = os.get("AZURE_RESOURCE_GROUP")
        self.vi_name = os.get("AZURE_VI_NAME")
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
            f"/generateAccessToken?api-version=2025-04-14"
        )

        headers = {"Authorization" : f"Bearer {arm_access_token}"}
        payload = {"permissionType":"Contributor","scope":"Account"}
        response = requests.post(url,header = headers,json = payload)
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

        logger.info(f"Downloading the youtube video : {url}")

        ydl_opts = {
            "format": 'best[ext= mp4]',
            'outtmpl':output_path,
            'quiet' :True,
            'overwrites' :True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            logger.info("Download complete")
            return output_path

        except Exception as e:
            raise Exception(f"Youtube  video Download Failed :{str(e)}")


# Upload the video to azure Video Indexer 

def upload_video(self, video_path,video_name):
    arm_token  = self.get_access_token()
    vi_token = self.get_account_token(arm_token)

    api_url = f"https://api.videoindexer.ai/{self.location}/Accounts/{self.account_id}/Videos"

    params  ={

        "accessToken":vi_token,
        "name":video_name,
        "privacy":"Private",
        "indexPresent" : "Default"

    }
    logger.info(f"Uploading the file {video_path} to azure ....")



# open the file in binary and stream it on azure
    with open(video_path,'rb') as video_file:
        files = {'file':video_file}
        response = requests.post(api_url,params=params,files = files)


    if response.status_code != 200:
        raise Exception(f"Azure Upload Failed: {response.text}")


def wait_for_processing(self,video_id):
    logger.info(f"Waiting for the video {video_id} to process...")
    while True:
        arm_token = self.get_access_token()
        vi_token = self.get_account_token(arm_token)


        url = "https://api.videoindexer.ai/{self.location}/Accounts/{self.account_id}/Videos"
        params  = {"access_token":vi_token}
        response = requests.get(url,params=params)
        data = response.json()

        state = data.get("state")
        if state  == "Processed":
            return data
        elif state == "Failed":
            raise Exception("Video INdexing Failed in azure")
        elif state == "Quarantined":
            raise Exception("Video Quarantined (Copy Right/Content Policy Violation)")
        logger.info(f"Status{state} waiting 30 seconds")
        time.sleep(30)
    
def extract_data(self, vi_json):
    """Parses the JSON into our state format."""
    transcript_lines = []
        insight.get("text")
        for v in vi_json.get("videos", [])
        for insight in v.get("insights", {}).get("transcript", [])
    ]

https://youtu.be/I3CWFDgqvq8 (3:53)