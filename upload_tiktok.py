import os
import json
import glob
import shutil
from pathlib import Path
from tiktok_uploader.upload import upload_videos
from tiktok_uploader.auth import AuthBackend

def parse_json_metadata(json_file):
    """Parse JSON file and extract upload metadata"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    title = data.get("video_title", "").strip('"')
    description = data.get("video_description", "")
    hashtags = data.get("video_hashtags", "")
    
    # Combine title, description and hashtags for TikTok description
    tiktok_description = f"{title}\n\n{description}\n\n{hashtags}"
    
    return tiktok_description

def auto_upload_tiktok_videos(video_dir=r"C:\AI\autoupload_Youtube\uploaded_videos", cookies_file="cookies.txt"):
    """Upload videos from YouTube uploaded_videos folder to TikTok"""
    
    # Create output directory for TikTok uploaded videos
    tiktok_uploaded_dir = Path("uploaded_videos_tiktok")
    tiktok_uploaded_dir.mkdir(exist_ok=True)
    
    # Get all MP4 files from uploaded_videos directory
    video_files = glob.glob(os.path.join(video_dir, "*.mp4"))
    
    if not video_files:
        print("No video files found in uploaded_videos directory")
        return
    
    # Check if cookies file exists
    if not os.path.exists(cookies_file):
        print(f"Cookies file '{cookies_file}' not found. Please create it first.")
        print("Instructions:")
        print("1. Login to TikTok in your browser")
        print("2. Export cookies using browser extension or developer tools")
        print("3. Save as 'cookies.txt' in the project root")
        return
    
    # Prepare videos for upload
    videos_to_upload = []
    
    for video_file in video_files:
        video_base = os.path.splitext(os.path.basename(video_file))[0]
        json_file = os.path.join(video_dir, f"{video_base}.json")
        
        if os.path.exists(json_file):
            try:
                description = parse_json_metadata(json_file)
                
                videos_to_upload.append({
                    'video': video_file,
                    'description': description[:2200]  # TikTok description limit
                })
                
            except Exception as e:
                print(f"Error processing metadata for {video_file}: {e}")
                # Use filename as description if JSON parsing fails
                videos_to_upload.append({
                    'video': video_file,
                    'description': video_base.replace('_', ' ')
                })
        else:
            # Use filename as description if no JSON found
            videos_to_upload.append({
                'video': video_file,
                'description': video_base.replace('_', ' ')
            })
    
    if not videos_to_upload:
        print("No videos prepared for upload")
        return
    
    print(f"Preparing to upload {len(videos_to_upload)} videos to TikTok...")
    
    try:
        # Initialize TikTok auth
        auth = AuthBackend(cookies=cookies_file)
        
        # Upload videos
        failed_videos = upload_videos(videos=videos_to_upload, auth=auth)
        
        # Process results
        successful_uploads = []
        for video_data in videos_to_upload:
            if video_data not in failed_videos:
                successful_uploads.append(video_data['video'])
        
        # Move successfully uploaded files
        for video_file in successful_uploads:
            video_base = os.path.splitext(os.path.basename(video_file))[0]
            json_file = os.path.join(video_dir, f"{video_base}.json")
            srt_file = os.path.join(video_dir, f"{video_base}.srt")
            
            # Move video file
            shutil.move(video_file, str(tiktok_uploaded_dir / os.path.basename(video_file)))
            print(f"Moved {os.path.basename(video_file)} to uploaded_videos_tiktok/")
            
            # Move JSON file if exists
            if os.path.exists(json_file):
                shutil.move(json_file, str(tiktok_uploaded_dir / os.path.basename(json_file)))
            
            # Move SRT file if exists
            if os.path.exists(srt_file):
                shutil.move(srt_file, str(tiktok_uploaded_dir / os.path.basename(srt_file)))
        
        # Report results
        print(f"\nUpload Results:")
        print(f"✅ Successfully uploaded: {len(successful_uploads)} videos")
        print(f"❌ Failed uploads: {len(failed_videos)} videos")
        
        if failed_videos:
            print("\nFailed videos:")
            for video in failed_videos:
                print(f"  - {os.path.basename(video['video'])}")
        
    except Exception as e:
        print(f"Error during TikTok upload process: {e}")
        print("Make sure your cookies.txt file is valid and up to date")

if __name__ == "__main__":
    auto_upload_tiktok_videos()