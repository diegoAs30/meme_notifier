#!/usr/bin/env python3
import time
import schedule
from datetime import datetime
from lib.meme_manager import MemeManager
from lib.notification import Notifier
import signal
import sys
import os

def signal_handler(sig, frame):
    print("\n🛑 Script stopped by user")
    sys.exit(0)

def main():
    # Configuración inicial
    signal.signal(signal.SIGINT, signal_handler)
    os.environ['DISPLAY'] = ':0'
    os.environ['DBUS_SESSION_BUS_ADDRESS'] = f'unix:path=/run/user/{os.getuid()}/bus'

    # Inicializar componentes
    meme_manager = MemeManager()
    notifier = Notifier(meme_manager.settings)

    def job():
        print(f"\n[{datetime.now()}] Fetching new meme...")
        meme = meme_manager.get_random_meme()
        
        if meme:
            print(f"🎁 New meme from {meme.get('source', 'unknown')}")
            print(f"📝 Title: {meme['title']}")
            
            meme_path = meme_manager.download_meme(meme['url'])
            if meme_path:
                notifier.show_notification(
                    title=f"🖼️ {meme.get('source', 'Meme')}",
                    message=meme['title'],
                    image_path=meme_path
                )
                time.sleep(3)
                notifier.open_image(meme_path)
        else:
            notifier.show_notification(
                title="⚠️ Meme Notifier",
                message="Failed to get memes from all sources"
            )

    # Programar tareas
    schedule.every().day.at("10:00").do(job)
    schedule.every().day.at("15:00").do(job)
    schedule.every().day.at("20:00").do(job)

    # Ejecutar una vez al inicio
    job()

    # Bucle principal
    print("\n✅ Meme Notifier is running...")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()