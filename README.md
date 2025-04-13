# meme_notifier

🔧 Instalación y configuración
Estructura de archivos:

bash
Copy
mkdir -p ~/meme_notifier/{config,lib}
touch ~/meme_notifier/{meme_notifier.py,config/{apis.json,settings.json},lib/{meme_manager.py,notification.py}}
Dependencias:

bash
Copy
pip install pillow requests schedule
sudo apt install libnotify-bin imagemagick xdg-utils
Hacer ejecutable:

bash
Copy
chmod +x ~/meme_notifier/meme_notifier.py
