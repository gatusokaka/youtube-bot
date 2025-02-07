import os
import json
import time
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow  # 添加OAuth 2.0认证库

# YouTube API 配置
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
# 要监控的多个频道ID列表
CHANNEL_IDS = [
    "UCWV3obpZVGgJ3j9FVhEjF2Q",
    "UCLttSYJ6kPtlcurY96kXkQw",
    "UCKcx1uK38H4AOkmfv4ywlrg"
]
CLIENT_SECRET_FILE = "client_secret.json"  # 你的 OAuth 2.0 客户端秘钥文件
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
COMMENT_LOG = "commented_videos.json"  # 用于记录已评论过的视频

# 如果通过 GitHub Secrets 提供凭据，则写入文件
if not os.path.exists(CLIENT_SECRET_FILE) and os.getenv("YOUTUBE_CREDENTIALS"):
    with open(CLIENT_SECRET_FILE, "w") as f:
        f.write(os.getenv("YOUTUBE_CREDENTIALS"))

def authenticate_youtube():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return credentials

# 使用 OAuth 2.0 认证
credentials = authenticate_youtube()
youtube = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

# 加载已评论视频记录（防止重复评论）
if os.path.exists(COMMENT_LOG):
    with open(COMMENT_LOG, "r") as f:
        commented_videos = json.load(f)
else:
    commented_videos = {}

def get_latest_video(channel_id):
    """
    获取指定频道最新上传的视频的 videoId
    """
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        order="date",
        maxResults=1
    )
    response = request.execute()
    
    if "items" in response and response["items"]:
        video_item = response["items"][0]
        # 获取 videoId，有时 search 接口返回的是 playlistItem 需注意此处差异
        video_id = video_item["id"].get("videoId")
        return video_id
    return None

def post_comment(video_id, comment_text="好视频！继续加油！"):
    """
    在指定视频下发表评论
    """
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
    print(f"已在视频 {video_id} 下评论: {comment_text}")

def main():
    """
    轮询检查所有指定频道的最新视频，并对新视频发表评论
    """
    while True:
        for channel_id in CHANNEL_IDS:
            video_id = get_latest_video(channel_id)
            if video_id and video_id not in commented_videos:
                try:
                    post_comment(video_id)
                    commented_videos[video_id] = True
                    # 每次评论后保存记录，防止重复评论
                    with open(COMMENT_LOG, "w") as f:
                        json.dump(commented_videos, f)
                except Exception as e:
                    print(f"评论视频 {video_id} 时出错: {e}")
        # 每10分钟检查一次，可根据需求调整间隔
        time.sleep(600)

if __name__ == "__main__":
    main()
