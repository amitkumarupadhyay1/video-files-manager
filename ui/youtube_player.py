"""
YouTube Video Player Dialog
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.file_manager import FileManager


class YouTubePlayerDialog(QDialog):
    """Dialog for playing YouTube videos"""
    
    def __init__(self, parent, youtube_url, title):
        super().__init__(parent)
        self.youtube_url = youtube_url
        
        self.setWindowTitle(f"YouTube: {title}")
        self.resize(900, 600)
        
        self.init_ui()
        self.load_youtube_video()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        
        # YouTube info
        info_label = QLabel(f"YouTube URL: {self.youtube_url}")
        info_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(info_label)
        
        # Web view for YouTube
        self.web_view = QWebEngineView()

        # Configure web engine settings for better compatibility
        settings = self.web_view.settings()
        settings.setAttribute(settings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(settings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(settings.WebAttribute.JavascriptCanAccessClipboard, True)
        settings.setAttribute(settings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(settings.WebAttribute.AllowRunningInsecureContent, True)

        # Connect error handling
        self.web_view.loadFinished.connect(self.on_load_finished)
        self.web_view.loadProgress.connect(self.on_load_progress)
        layout.addWidget(self.web_view)
        
        # Control buttons
        control_layout = QHBoxLayout()
        control_layout.addStretch()
        
        # Open in browser button
        browser_btn = QPushButton("🌐 Open in Browser")
        browser_btn.clicked.connect(self.open_in_browser)
        control_layout.addWidget(browser_btn)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        control_layout.addWidget(close_btn)
        
        layout.addLayout(control_layout)
    
    def load_youtube_video(self):
        """Load YouTube video in web view"""
        # Validate YouTube URL
        if not FileManager.validate_youtube_url(self.youtube_url):
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        margin: 0;
                        padding: 20px;
                        background-color: #ffebee;
                        color: #c62828;
                        font-family: Arial, sans-serif;
                        text-align: center;
                    }}
                </style>
            </head>
            <body>
                <h2>Invalid YouTube URL</h2>
                <p>The provided URL is not a valid YouTube link.</p>
                <p>URL: {self.youtube_url}</p>
            </body>
            </html>
            """
            self.web_view.setHtml(error_html)
            return

        # Convert to embed URL
        embed_url = FileManager.get_youtube_embed_url(self.youtube_url)
        
        # Create HTML with embedded YouTube player
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    background-color: #000;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    cursor: default;
                }}
                .message {{
                    position: absolute;
                    top: 10px;
                    left: 10px;
                    background-color: rgba(0, 0, 0, 0.7);
                    color: white;
                    padding: 8px;
                    border-radius: 4px;
                    font-family: Arial, sans-serif;
                    font-size: 12px;
                    z-index: 1000;
                    max-width: 300px;
                }}
                .error-message {{
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    background-color: rgba(255, 255, 255, 0.95);
                    color: #d32f2f;
                    padding: 20px;
                    border-radius: 8px;
                    font-family: Arial, sans-serif;
                    font-size: 14px;
                    text-align: center;
                    z-index: 2000;
                    display: none;
                    max-width: 400px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                }}
                iframe {{
                    width: 100%;
                    height: 100%;
                    border: none;
                    display: block;
                }}
            </style>
        </head>
        <body>
            <div class="message">
                Loading YouTube video...<br>
                If video doesn't load, use "Open in Browser" button.
            </div>

            <div id="error-message" class="error-message">
                This YouTube video cannot be embedded.<br>
                Please use the "🌐 Open in Browser" button.
            </div>

            <iframe
                id="youtube-player"
                src="{embed_url}?rel=0&modestbranding=1&showinfo=0&enablejsapi=1"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
                allowfullscreen
                onload="onIframeLoad()"
                onerror="onIframeError()">
            </iframe>

            <script>
                var loadTimeout;
                var loaded = false;

                function onIframeLoad() {{
                    loaded = true;
                    clearTimeout(loadTimeout);
                    document.querySelector('.message').style.display = 'none';
                }}

                function onIframeError() {{
                    showError();
                }}

                function showError() {{
                    document.querySelector('.message').style.display = 'none';
                    document.getElementById('error-message').style.display = 'block';
                    document.getElementById('youtube-player').style.display = 'none';
                }}

                // Check if iframe content is actually loaded
                function checkContentLoaded() {{
                    try {{
                        // Basic check - if iframe has content height > 0
                        var iframe = document.getElementById('youtube-player');
                        if (iframe.contentWindow && iframe.contentWindow.document) {{
                            loaded = true;
                            document.querySelector('.message').style.display = 'none';
                        }}
                    }} catch(e) {{
                        // Cross-origin restrictions may prevent this check
                    }}
                }}

                // Set timeout to detect loading issues
                loadTimeout = setTimeout(function() {{
                    if (!loaded) {{
                        // Give more time for slower connections
                        setTimeout(function() {{
                            if (!loaded) {{
                                showError();
                            }}
                        }}, 10000);
                    }}
                }}, 5000);

                // Check periodically if content loaded
                setTimeout(checkContentLoaded, 3000);
            </script>
        </body>
        </html>
        """
        
        self.web_view.setHtml(html)

    def on_load_finished(self, success):
        """Handle page load completion"""
        if not success:
            self.show_embed_error()

    def on_load_progress(self, progress):
        """Handle loading progress"""
        # Could add a progress bar here if needed
        pass

    def show_embed_error(self):
        """Show error when YouTube embed fails"""
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    background-color: #fff3e0;
                    color: #ef6c00;
                    font-family: Arial, sans-serif;
                    text-align: center;
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                }}
                .error-icon {{
                    font-size: 48px;
                    margin-bottom: 20px;
                }}
                .title {{
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 16px;
                }}
                .message {{
                    font-size: 16px;
                    line-height: 1.5;
                    margin-bottom: 24px;
                    max-width: 600px;
                }}
                .url {{
                    background-color: #f5f5f5;
                    padding: 8px 12px;
                    border-radius: 4px;
                    font-family: monospace;
                    word-break: break-all;
                    margin: 12px 0;
                }}
                .suggestions {{
                    background-color: #e8f5e8;
                    padding: 16px;
                    border-radius: 8px;
                    text-align: left;
                    max-width: 600px;
                    margin-top: 20px;
                }}
                .suggestions ul {{
                    margin: 8px 0;
                    padding-left: 20px;
                }}
                .suggestions li {{
                    margin: 6px 0;
                }}
            </style>
        </head>
        <body>
            <div class="error-icon">🚫</div>
            <div class="title">YouTube Video Unavailable</div>
            <div class="message">
                This YouTube video cannot be embedded in the application due to one of the following reasons:
            </div>
            <div class="url">{self.youtube_url}</div>

            <div class="suggestions">
                <strong>Possible Solutions:</strong>
                <ul>
                    <li><b>Copyright Restriction:</b> The video uploader has disabled embedding</li>
                    <li><b>Age Restrictions:</b> The video has age restrictions that prevent embedding</li>
                    <li><b>Private Video:</b> The video is set to private</li>
                    <li><b>Region Restrictions:</b> The video is restricted in your region</li>
                </ul>
                <strong>Recommended Action:</strong><br>
                Click the "🌐 Open in Browser" button below to watch this video in your default web browser.
            </div>
        </body>
        </html>
        """

        self.web_view.setHtml(error_html)

    def open_in_browser(self):
        """Open YouTube video in default browser"""
        import webbrowser
        webbrowser.open(self.youtube_url)
