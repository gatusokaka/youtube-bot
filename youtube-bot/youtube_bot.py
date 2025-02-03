import os
import json
import time
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# ���Ŀ�� YouTube Ƶ�� ID
CHANNEL_ID = "UC_x5XG1OV2P6uZZ5FSM9Ttw"  # �滻ΪĿ��Ƶ��ID

# �����������
COMMENT_TEXT = "�����������������Ƶ��[���������Ƶ����]"

# API ������
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# ��֤������ API ����
def youtube_authenticate():
    creds = None
    if os.path.exists("token.json"):
        with open("token.json", "r") as token:
            creds = json.load(token)
    
    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            json.dump(creds.to_json(), token)
    
    return build("youtube", "v3", credentials=creds)

# ��ȡƵ��������Ƶ
def get_latest_video(youtube, channel_id):
    request = youtube.search().list(
        part="id",
        channelId=channel_id,
        order="date",
        maxResults=1
    )
    response = request.execute()
    if "items" in response and len(response["items"]) > 0:
        return response["items"][0]["id"]["videoId"]
    return None

# ����Ƶ�·�����
def post_comment(youtube, video_id, comment_text):
    request = youtube.commentThreads().insert(
        part="snippet",
        body={
            "snippet": {
                "videoId": video_id,
                "topLevelComment": {
                    "snippet": {
                        "textOriginal": comment_text
                    }
                }
            }
        }
    )
    response = request.execute()
    return response

# ������
if __name__ == "__main__":
    youtube = youtube_authenticate()
    
    last_video_id = None
    while True:
        video_id = get_latest_video(youtube, CHANNEL_ID)
        
        if video_id and video_id != last_video_id:
            print(f"��������Ƶ: {video_id}")
            post_comment(youtube, video_id, COMMENT_TEXT)
            last_video_id = video_id
        
        time.sleep(300)  # ÿ5���Ӽ��һ��
