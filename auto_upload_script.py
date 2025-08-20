import os
import json
import glob
import shutil
from pathlib import Path
from upload_youtube import upload_video
from utilites.argotranslate import translate_meta

def sanitize_filename(filename):
    """Sanitize filename for safe file operations"""
    return "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()

def find_matching_json(mp4_filename, json_dir="."):
    """Find JSON file that contains words from MP4 filename"""
    mp4_base = os.path.splitext(os.path.basename(mp4_filename))[0].lower()
    mp4_words = mp4_base.replace("_", " ").replace("-", " ").split()
    
    json_files = glob.glob(os.path.join(json_dir, "*.json"))
    
    for json_file in json_files:
        json_base = os.path.splitext(os.path.basename(json_file))[0].lower()
        json_words = json_base.replace("_", " ").replace("-", " ").split()
        
        # Check if any words from MP4 name are in JSON name
        if any(word in json_words for word in mp4_words if len(word) > 2):
            return json_file
    
    return None

def parse_json_metadata(json_file):
    """Parse JSON file and extract upload metadata"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    title = data.get("video_title", "").strip('"')
    description = data.get("video_description", "")
    hashtags = data.get("video_hashtags", "")
    
    # Convert hashtags to tags list
    tags = []
    if hashtags:
        tags = [tag.strip().replace("#", "") for tag in hashtags.split(",")]
    
    return title, description, tags

def create_translated_json_files(video_files, json_dir="video_output"):
    """Create translated JSON files for each video file"""
    # Get unique base names from video files
    base_names = set()
    for video_file in video_files:
        video_base = os.path.splitext(os.path.basename(video_file))[0]
        if video_base.endswith(('_en', '_ro', '_ru')):
            base_name = video_base[:-3]
        else:
            base_name = video_base
        base_names.add(base_name)
    
    # Create translated JSON files for each unique base name
    for base_name in base_names:
        original_json = os.path.join(json_dir, f"{base_name}.json")
        if not os.path.exists(original_json):
            continue
            
        with open(original_json, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        for language in ["en", "ro", "ru"]:
            translated_filename = os.path.join(json_dir, f"{base_name}_{language}.json")
            
            # Skip if already exists
            if os.path.exists(translated_filename):
                continue
                
            if language == "en":
                translated_meta = meta
            else:
                translated_meta = translate_meta(meta, language)
            
            with open(translated_filename, 'w', encoding='utf-8') as f:
                json.dump(translated_meta, f, ensure_ascii=False, indent=2)
            print(f"Created: {translated_filename}")

def find_subtitle_files(video_file, video_dir="video_output"):
    """Find matching subtitle files for a video"""
    video_base = os.path.splitext(os.path.basename(video_file))[0]
    subtitle_files = []
    
    # Look for SRT files with same base name
    srt_file = os.path.join(video_dir, f"{video_base}.srt")
    if os.path.exists(srt_file):
        # Extract language from filename
        if video_base.endswith('_en'):
            subtitle_files.append((srt_file, 'en'))
        elif video_base.endswith('_ro'):
            subtitle_files.append((srt_file, 'ro'))
        elif video_base.endswith('_ru'):
            subtitle_files.append((srt_file, 'ru'))
        else:
            subtitle_files.append((srt_file, 'en'))  # Default to English
    
    return subtitle_files

def auto_upload_videos(video_dir="video_output", json_dir="video_output", privacy_status="public"):
    """Find MP4 files, match with JSON, and upload automatically"""
    # Get all video files
    video_files = glob.glob(os.path.join(video_dir, "*.mp4"))
    
    # Create translated JSON files
    create_translated_json_files(video_files, json_dir)
    
    uploaded_dir = Path("uploaded_videos")
    uploaded_dir.mkdir(exist_ok=True)
    
    for video_file in video_files:
        video_base = os.path.splitext(os.path.basename(video_file))[0]
        json_file = os.path.join(json_dir, f"{video_base}.json")
        
        if os.path.exists(json_file):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    translated_meta = json.load(f)
                
                # Extract language from filename
                language = "en"
                if video_base.endswith('_ro'):
                    language = "ro"
                elif video_base.endswith('_ru'):
                    language = "ru"
                
                # Find matching subtitle files
                subtitle_files = find_subtitle_files(video_file, video_dir)
                
                upload_video(
                    file=video_file,
                    title=translated_meta["video_title"],
                    description=translated_meta["video_description"],
                    tags=translated_meta["video_hashtags"].split(", "),
                    language=language,
                    privacyStatus=privacy_status,
                    scheduled=True,
                    subtitle_files=subtitle_files
                )
                print(f"Successfully uploaded {video_base}")
                
                # Move files after successful upload
                shutil.move(video_file, str(uploaded_dir / os.path.basename(video_file)))
                shutil.move(json_file, str(uploaded_dir / os.path.basename(json_file)))
                
                # Move subtitle files too
                for subtitle_file, _ in subtitle_files:
                    if os.path.exists(subtitle_file):
                        shutil.move(subtitle_file, str(uploaded_dir / os.path.basename(subtitle_file)))
                
            except Exception as e:
                print(f"Error uploading {video_file}: {e}")
        else:
            print(f"No JSON file found for {video_file}")

if __name__ == "__main__":
    auto_upload_videos(video_dir=r"C:\AI\comfyui_automatization\video_output", json_dir=r"C:\AI\comfyui_automatization\video_output", privacy_status="private")