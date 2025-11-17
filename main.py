"""
School Video Management Application
Main entry point
"""
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    """Main application entry point"""
    # Ensure Qt WebEngine can be initialized safely by setting the
    # AA_ShareOpenGLContexts attribute before creating the QApplication.
    from PyQt6.QtCore import Qt, QCoreApplication
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)
    # Basic logging configuration (log to storage/app.log and console)
    import logging
    import os
    try:
        from config import STORAGE_DIR
    except Exception:
        STORAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'storage')

    os.makedirs(STORAGE_DIR, exist_ok=True)
    log_file = os.path.join(STORAGE_DIR, 'app.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
