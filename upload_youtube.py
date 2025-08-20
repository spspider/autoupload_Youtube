import os
import pickle
from datetime import datetime, timedelta
import pytz
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Путь к client_secrets.json
CLIENT_SECRETS_FILE = "client_secrets.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]

# Авторизация и создание сервиса
def get_authenticated_service():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)

def get_optimal_publish_time(language):
    """Get optimal publish time based on language/region peak hours"""
    from datetime import datetime, timedelta
    import pytz
    
    now = datetime.now(pytz.UTC)
    
    # Target peak evening hours in local time zones
    if language == "en":
        # US Eastern Time - 8 PM (20:00)
        target_tz = pytz.timezone('US/Eastern')
        target_hour = 20
    elif language == "ro":
        # Romania EET - 8 PM (20:00)
        target_tz = pytz.timezone('Europe/Bucharest')
        target_hour = 20
    elif language == "ru":
        # Russia MSK - 9 PM (21:00)
        target_tz = pytz.timezone('Europe/Moscow')
        target_hour = 21
    else:
        # Default to UTC
        target_tz = pytz.UTC
        target_hour = 20
    
    # Get current time in target timezone
    local_now = now.astimezone(target_tz)
    
    # Set target time to today at target hour
    target_time = local_now.replace(hour=target_hour, minute=0, second=0, microsecond=0)
    
    # If target time has passed today, schedule for tomorrow
    if target_time <= local_now:
        target_time += timedelta(days=1)
    
    # Convert back to UTC for YouTube API
    utc_time = target_time.astimezone(pytz.UTC)
    
    return utc_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")

def upload_subtitles(youtube, video_id, subtitle_file, language):
    """Upload subtitle file to YouTube video"""
    try:
        body = {
            "snippet": {
                "videoId": video_id,
                "language": language,
                "name": f"Subtitles ({language})"
            }
        }
        
        media = MediaFileUpload(subtitle_file, mimetype="text/plain")
        
        request = youtube.captions().insert(
            part="snippet",
            body=body,
            media_body=media
        )
        
        response = request.execute()
        print(f"Subtitles uploaded successfully for language {language}. Caption ID: {response['id']}")
        return response['id']
        
    except Exception as e:
        print(f"Error uploading subtitles for {language}: {e}")
        return None

# Загрузка видео
def upload_video(file, title, description, tags=None, categoryId="22", privacyStatus="public", language="en", scheduled=True, subtitle_files=None):
    youtube = get_authenticated_service()
    
    print(f"Uploading video with title: '{title}' in language: {language}")

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": categoryId,
            "defaultLanguage": language,
            "defaultAudioLanguage": language
        },
        "status": {
            "privacyStatus": "private" if scheduled else privacyStatus
        }
    }
    
    # Add scheduled publish time if requested
    if scheduled:
        publish_time = get_optimal_publish_time(language)
        body["status"]["publishAt"] = publish_time
        body["status"]["privacyStatus"] = "private"
        print(f"Scheduled to publish at: {publish_time}")

    media = MediaFileUpload(file, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploading... {int(status.progress() * 100)}%")

    print("Upload complete. Video ID:", response["id"])
    
    # Upload subtitles if provided
    if subtitle_files:
        for subtitle_file, sub_language in subtitle_files:
            if os.path.exists(subtitle_file):
                upload_subtitles(youtube, response["id"], subtitle_file, sub_language)
            else:
                print(f"Subtitle file not found: {subtitle_file}")
    
    return response["id"]

# Пример запуска
if __name__ == "__main__":
    upload_video(
        file="video.mp4",
        title="Заголовок видео",
        description="Описание видео",
        tags=["example", "test"],
        privacyStatus="unlisted"
    )
