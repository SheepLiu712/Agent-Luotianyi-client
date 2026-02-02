import sys
import os
import time
import threading

# Ensure src is in path
cwd = os.path.dirname(os.path.abspath(__file__))
if cwd not in sys.path:
    sys.path.append(cwd)

# Fix for QDialog import if needed or just use PySide6 direct
from PySide6.QtWidgets import QDialog

from src.utils.helpers import load_config
from src.gui import ui_init, MainWindow
from src.gui.binder import AgentBinder
from src.live2d import live2d
from src.network_client import NetworkClient
from src.gui.login_dialog import LoginDialog

if __name__ == "__main__":
    main_config_path = os.path.join(cwd, "config", "config.json")
    if not os.path.exists(main_config_path):
        print(f"Config not found at {main_config_path}")
        
    config = load_config(main_config_path)

    app = ui_init()
    
    # Login Flow
    network_client = NetworkClient()
    login_dialog = LoginDialog(network_client)
    
    # Try auto login
    if not login_dialog.try_auto_login():
        if login_dialog.exec() != QDialog.DialogCode.Accepted:
            live2d.dispose()
            sys.exit(0)
        
    print(f"Logged in as {network_client.user_id}")
    
    binder = AgentBinder(hear_callback=network_client.network_hear_callback, history_callback=network_client.network_history_callback)
    
    try:
        window = MainWindow(config["gui"], config["live2d"], binder)
        window.show()
    except Exception as e:
        print(f"Error creating MainWindow: {e}")
        import traceback
        traceback.print_exc()
        live2d.dispose()
        sys.exit(1)

    ret = app.exec()
    live2d.dispose()
    sys.exit(ret)
