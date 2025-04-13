import json
import random
import requests
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(
    filename='meme_notifier.log',
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)

class MemeManager:
    def __init__(self):
        self.apis = self._load_apis()
        self.settings = self._load_settings()
        self.meme_dir = Path(self.settings['storage']['meme_dir']).expanduser()
        self.meme_dir.mkdir(parents=True, exist_ok=True)

    def _load_apis(self) -> Dict:
        try:
            with open(Path(__file__).parent.parent/'config/apis.json') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading APIs: {str(e)}")
            return {}

    def _load_settings(self) -> Dict:
        try:
            with open(Path(__file__).parent.parent/'config/settings.json') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading settings: {str(e)}")
            return {
                'storage': {
                    'meme_dir': '~/.local/share/meme_notifier',
                    'max_files': 50
                },
                'category_weights': {
                    'programming': 0.4,
                    '3d_design': 0.3,
                    'general': 0.3
                }
            }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _make_request(self, url: str, headers: dict, method: str = 'GET') -> Optional[requests.Response]:
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=15
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logging.error(f"Request failed: {str(e)}")
            raise

    def _process_response(self, api_config: Dict, data) -> Optional[Dict]:
        try:
            processor = eval(api_config['processor'])
            result = processor(data)
            if not result or not result.get('url'):
                raise ValueError("Invalid meme data")
            return result
        except Exception as e:
            logging.error(f"Error processing response: {str(e)}")
            return None

    def get_random_meme(self) -> Optional[Dict]:
        for _ in range(3):  # Try up to 3 different APIs
            category = random.choices(
                list(self.settings['category_weights'].keys()),
                weights=list(self.settings['category_weights'].values()),
                k=1
            )[0]

            if not self.apis.get(category):
                continue

            api_name, api_config = random.choice(list(self.apis[category].items()))
            try:
                response = self._make_request(
                    url=api_config['url'],
                    headers=api_config['headers'],
                    method=api_config['method']
                )
                
                if response:
                    meme = self._process_response(api_config, response.json())
                    if meme:
                        return meme
            
            except Exception as e:
                logging.error(f"API {api_name} failed: {str(e)}")

        # Fallback to default meme
        return {
            'title': "No se pudo obtener memes 😢",
            'url': "https://i.imgur.com/6v8Q7Xy.jpg",
            'source': "Sistema"
        }

    def download_meme(self, url: str) -> Optional[Path]:
        try:
            response = requests.get(url, timeout=20, stream=True)
            response.raise_for_status()
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            meme_path = self.meme_dir / f"meme_{timestamp}.jpg"
            
            with open(meme_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            
            self._clean_old_files()
            return meme_path
        except Exception as e:
            logging.error(f"Download failed: {str(e)}")
            return None

    def _clean_old_files(self):
        try:
            files = sorted(self.meme_dir.glob('meme_*.jpg'), key=os.path.getmtime)
            if len(files) > self.settings['storage']['max_files']:
                for old_file in files[:-self.settings['storage']['max_files']]:
                    old_file.unlink()
        except Exception as e:
            logging.error(f"Error cleaning files: {str(e)}")