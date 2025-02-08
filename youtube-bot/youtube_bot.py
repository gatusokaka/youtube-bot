import os
import json
import time
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# YouTube API 配置
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
CHANNEL_IDS = [
    "UCWV3obpZVGgJ3j9FVhEjF2Q",
    "UCLttSYJ6kPtlcurY96kXkQw",
    "UCKcx1uK38H4AOkmfv4ywlrg"
]
CREDENTIALS_FILE = "credentials.json"  # OAuth 2.0 凭据
TOKEN_FILE = "token.pickle"  # 用于存储和刷新令牌
COMMENT_LOG = "commented_videos.json"  # 记录已评论视频
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# 处理 OAuth 2.0 认证
def get_authenticated_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    return build(API_SERVICE_NAME, API_VERSION, credentials=creds)

youtube = get_authenticated_service()

# 加载已评论视频
if os.path.exists(COMMENT_LOG):
    with open(COMMENT_LOG, "r") as f:
        commented_videos = json.load(f)
else:
    commented_videos = {}

def get_latest_video(channel_id):
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        order="date",
        maxResults=1
    )
    response = request.execute()
    if "items" in response and response["items"]:
        video_id = response["items"][0]["id"].get("videoId")
        return video_id
    return None

def post_comment(video_id, comment_text="好视频！继续加油！"):
    request = youtube.commentThreads().insert(
        part="snippet",
        body={
            "snippet": {
                "videoId": video_id,
                "topLevelComment": {
                    "snippet": {"textOriginal": comment_text}
                }
            }
        }
    )
    request.execute()
    print(f"已在视频 {video_id} 下评论: {comment_text}")

def main():
    while True:
        for channel_id in CHANNEL_IDS:
            video_id = get_latest_video(channel_id)
            if video_id and video_id not in commented_videos:
                try:
                    post_comment(video_id)
                    commented_videos[video_id] = True
                    with open(COMMENT_LOG, "w") as f:
                        json.dump(commented_videos, f)
                except Exception as e:
                    print(f"评论视频 {video_id} 时出错: {e}")
        time.sleep(600)

if __name__ == "__main__":
    main()
