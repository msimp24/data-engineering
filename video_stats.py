import requests
import os
import json
from datetime import date
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.environ.get('YOUTUBE_API_KEY')
channel_handle = 'MrBeast'


def get_playlist_id( handle):
  
  try:

    url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={handle}&key={API_KEY}"

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()

    channel_items = data['items'][0]

    playlist_id = channel_items['contentDetails']['relatedPlaylists']['uploads']

    return playlist_id
  except requests.exceptions.RequestException as e:
    raise e
  
  
max_result = 10 

def get_video_ids(playlist_id):
  try:
    
    video_ids = []
    
    page_token = None
    
    base_url = f"https://www.googleapis.com/youtube/v3/playlistItems?playlistId={playlist_id}&maxResults={max_result}&part=contentDetails&key={API_KEY}"
    
    while True:
      url = base_url
      
      if page_token:
        url += f"&pageToken={page_token}"   
    
      response = requests.get(url)
        
      response.raise_for_status()

      data = response.json()
        
      for item in data.get('items', []):
        video_id = item['contentDetails']['videoId']
        video_ids.append(video_id)

      page_token = data.get('nextPageToken')
        
      if not page_token:
        break
        
    return video_ids
    
    
  except Exception as e:
    raise e 
  
    

    
def extract_video_data(video_ids):
  extracted_data = []
  
  def batch_list(video_id_list, batch_size):
    for video_id in range(0, len(video_id_list), batch_size):
      yield video_id_list[video_id:video_id + batch_size]
    
  try:
    for batch in batch_list(video_ids, max_result):
      video_ids_str = ",".join(batch)
      
      url=f"https://www.googleapis.com/youtube/v3/videos?id={video_ids_str}&maxResults={max_result}&part=contentDetails,snippet,statistics&key={API_KEY}"
      
      response = requests.get(url)
        
      response.raise_for_status()

      data = response.json()
      
      for item in data.get('items', []):
        video_id = item['id']
        snippet = item['snippet']
        contentDetails = item['contentDetails']
        statistics = item['statistics']
      
        video_data = {
        "video_id": video_id, 
        "title":snippet['title'],
        "publishedAt":snippet['publishedAt'],
        "duration":contentDetails['duration'],
        "viewCount":statistics.get('viewCount', None),
        "likeCount":statistics.get('likeCount', None),
        "commentCount": statistics.get('commentCount', None)
        }
        extracted_data.append(video_data)
    return extracted_data
      
  except requests.exceptions.RequestException as e:
    raise e  
  
def save_to_json(data):
  file_path = f"./data/YT_data_{date.today()}.json"
  
  with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4) 
  
if __name__ == "__main__":
  id = get_playlist_id(channel_handle)  
  video_ids = get_video_ids(id)
  data = extract_video_data(video_ids)
  save_to_json(data)