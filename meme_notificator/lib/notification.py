import subprocess
from pathlib import Path
from PIL import Image
import os

class Notifier:
    def __init__(self, settings):
        self.settings = settings

    def resize_image(self, image_path: Path) -> Path:
        try:
            with Image.open(image_path) as img:
                img.thumbnail((self.settings['notification']['max_size'], 
                             self.settings['notification']['max_size']))
                resized_path = image_path.parent / "meme_resized.jpg"
                img.save(resized_path, "JPEG", quality=95)
                return resized_path
        except Exception as e:
            print(f"Resize failed: {str(e)}")
            return image_path

    def show_notification(self, title: str, message: str, image_path: Path = None):
        try:
            cmd = [
                'notify-send',
                title,
                message,
                f'--expire-time={self.settings["notification"]["duration"] * 1000}',
                '--urgency=normal'
            ]

            if image_path and image_path.exists():
                resized_img = self.resize_image(image_path)
                cmd.extend([f'--icon={resized_img}'])
            else:
                cmd.extend([f'--icon={self.settings["notification"]["fallback_icon"]}'])

            subprocess.run(cmd)
        except Exception as e:
            print(f"Notification failed: {str(e)}")

    def open_image(self, image_path: Path):
        if image_path and image_path.exists():
            subprocess.run(['xdg-open', str(image_path)])