import os
import json
import time
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# 你的目标 YouTube 频道 ID
CHANNEL_ID = "UC_x5XG1OV2P6uZZ5FSM9Ttw"  # 替换为目标频道ID

# 你的评论内容
COMMENT_TEXT = "快来看看这个精彩视频！[插入你的视频链接]"

# API 作用域
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# 认证并建立 API 服务
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

# 获取频道最新视频
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

# 在视频下方评论
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

# 主函数
if __name__ == "__main__":
    youtube = youtube_authenticate()
    
    last_video_id = None
    while True:
        video_id = get_latest_video(youtube, CHANNEL_ID)
        
        if video_id and video_id != last_video_id:
            print(f"发现新视频: {video_id}")
            post_comment(youtube, video_id, COMMENT_TEXT)
            last_video_id = video_id
        
        time.sleep(300)  # 每5分钟检查一次
