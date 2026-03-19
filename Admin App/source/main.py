"""
Password Generator Application - Main Entry Point
"""

import sys
import os
import signal
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer

# Install global exception hook to catch ALL unhandled exceptions (including Qt slot crashes)
def _global_exception_hook(exc_type, exc_value, exc_tb):
    # Don't print KeyboardInterrupt as a crash
    if exc_type is KeyboardInterrupt:
        sys.exit(0)
    
    traceback.print_exception(exc_type, exc_value, exc_tb)
    sys.__excepthook__(exc_type, exc_value, exc_tb)

sys.excepthook = _global_exception_hook

# Windows: set AppUserModelID BEFORE QApplication is created so taskbar shows the icon
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ClosetsByDesign.IdentityManager.1.0")
    except Exception:
        pass

def resource_path(relative_path: str) -> str:
    """Get absolute path to resource — works for dev and PyInstaller frozen EXE."""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)

def _set_taskbar_icon_win32(widget, ico_path: str):
    """Directly send WM_SETICON to the native HWND — the only reliable method on Windows."""
    if sys.platform != "win32" or not os.path.exists(ico_path):
        return
    try:
        import ctypes
        WM_SETICON      = 0x0080
        ICON_SMALL      = 0
        ICON_BIG        = 1
        LR_LOADFROMFILE = 0x0010
        IMAGE_ICON      = 1
        hwnd = int(widget.winId())

        sm = ctypes.windll.user32.GetSystemMetrics(49)  # SM_CXSMICON
        bg = ctypes.windll.user32.GetSystemMetrics(11)  # SM_CXICON
        if sm == 0: sm = 16
        if bg == 0: bg = 32

        hicon_small = ctypes.windll.user32.LoadImageW(
            None, ico_path, IMAGE_ICON, sm, sm, LR_LOADFROMFILE
        )
        hicon_big = ctypes.windll.user32.LoadImageW(
            None, ico_path, IMAGE_ICON, bg, bg, LR_LOADFROMFILE
        )
        if hicon_small:
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon_small)
        if hicon_big:
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon_big)
    except Exception:
        pass

class PasswordGeneratorApp:
    """Main application class."""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Identity Manager")
        self.app.setApplicationDisplayName("Identity Manager")
        self.app.setApplicationVersion("1.0")
        
        # Load icon once and reuse everywhere
        self._app_icon = self._load_icon()
        if self._app_icon:
            self.app.setWindowIcon(self._app_icon)

    def _load_icon(self):
        """Load the best available icon for the application."""
        candidates = [
            resource_path(os.path.join("assets", "app_icon.ico")),
            resource_path(os.path.join("assets", "Logo without text.png")),
            resource_path(os.path.join("assets", "Logo 1.png")),
        ]
        for path in candidates:
            if os.path.exists(path):
                icon = QIcon(path)
                if not icon.isNull():
                    return icon
        return None
    
    def run(self):
        """Run the application."""
        try:
            # Prevent Qt from quitting when the credentials dialog is hidden
            self.app.setQuitOnLastWindowClosed(False)
            
            # Set up signal handlers for graceful shutdown
            def signal_handler(sig, frame):
                self.app.quit()
            
            signal.signal(signal.SIGINT, signal_handler)
            if hasattr(signal, 'SIGTERM'):
                signal.signal(signal.SIGTERM, signal_handler)
            
            # Add a timer that fires frequently to allow signal handling
            timer = QTimer()
            timer.timeout.connect(lambda: None)  # Process the Qt event loop
            timer.start(100)  # Fire every 100ms
            
            # Show database credentials dialog first
            from login_ui import DatabaseCredentialsDialog
            
            self.creds_dialog = DatabaseCredentialsDialog(parent_app=self)
            self.dashboard = None
            self.creds_dialog.show()
            # Apply native taskbar icon after the window handle is created
            _set_taskbar_icon_win32(self.creds_dialog, resource_path(os.path.join("assets", "app_icon.ico")))
            
            # Run the Qt application loop
            result = self.app.exec()
            
            return result
            
        except KeyboardInterrupt:
            return 0
        except Exception as e:
            QMessageBox.critical(None, "Application Error", f"Failed to start the application:\n\n{str(e)}")
            return 1


def main():
    """Main entry point."""
    try:
        # Create and run the application
        app = PasswordGeneratorApp()
        return app.run()
        
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        return 1


if __name__ == "__main__":
    sys.exit(main())

