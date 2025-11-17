"""
Local Video Player Dialog
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QSlider, QStyle, QWidget)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtGui import QPixmap
import os


class VideoPlayerDialog(QDialog):
    """Dialog for playing local video files"""

    def __init__(self, parent, video_path, title, thumbnail_path=None):
        super().__init__(parent)
        self.video_path = video_path
        self.thumbnail_path = thumbnail_path

        self.setWindowTitle(f"Playing: {title}")
        self.resize(800, 600)

        # Create media player
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

        self.init_ui()
        self.load_video()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Video widget
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)
        layout.addWidget(self.video_widget)

        # Create controls container to limit height
        self.controls_container = QWidget()
        self.controls_container.setFixedHeight(60)  # Approximately 10% of 600px height
        controls_layout = QVBoxLayout(self.controls_container)
        controls_layout.setContentsMargins(5, 2, 5, 2)
        controls_layout.setSpacing(0)

        # Position slider
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_position)
        controls_layout.addWidget(self.position_slider)

        # Time label and controls in horizontal layout
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(5)

        self.time_label = QLabel("00:00 / 00:00")
        bottom_layout.addWidget(self.time_label)

        # Play button
        self.play_btn = QPushButton()
        self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_btn.setFixedSize(32, 32)
        self.play_btn.clicked.connect(self.play_pause)
        bottom_layout.addWidget(self.play_btn)

        # Stop button
        stop_btn = QPushButton()
        stop_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        stop_btn.setFixedSize(32, 32)
        stop_btn.clicked.connect(self.stop)
        bottom_layout.addWidget(stop_btn)

        bottom_layout.addStretch()

        # Volume slider
        bottom_layout.addWidget(QLabel("Volume:"))
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMaximumWidth(80)
        self.volume_slider.valueChanged.connect(self.set_volume)
        bottom_layout.addWidget(self.volume_slider)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close_player)
        bottom_layout.addWidget(close_btn)

        controls_layout.addLayout(bottom_layout)
        layout.addWidget(self.controls_container)

        # Connect media player signals
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.errorOccurred.connect(self.on_media_error)

        # Set initial volume
        self.set_volume(70)
    
    def load_video(self):
        """Load video file"""
        if os.path.exists(self.video_path):
            self.media_player.setSource(QUrl.fromLocalFile(self.video_path))
        else:
            QLabel("Video file not found").show()
    
    def play_pause(self):
        """Toggle play/pause"""
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        else:
            self.media_player.play()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
    
    def stop(self):
        """Stop playback"""
        self.media_player.stop()
        self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
    
    def set_position(self, position):
        """Set playback position"""
        self.media_player.setPosition(position)
    
    def set_volume(self, value):
        """Set volume"""
        self.audio_output.setVolume(value / 100.0)
    
    def position_changed(self, position):
        """Update position slider"""
        self.position_slider.setValue(position)
        
        # Update time label
        current_time = self.format_time(position)
        total_time = self.format_time(self.media_player.duration())
        self.time_label.setText(f"{current_time} / {total_time}")
    
    def duration_changed(self, duration):
        """Update slider range"""
        self.position_slider.setRange(0, duration)
    
    def format_time(self, ms):
        """Format milliseconds to MM:SS"""
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def close_player(self):
        """Close player and stop playback"""
        self.cleanup_media_player()
        self.accept()

    def closeEvent(self, event):
        """Handle window close event"""
        self.cleanup_media_player()
        super().closeEvent(event)

    def on_media_error(self, error, error_string):
        """Handle media player errors"""
        print(f"Media player error: {error_string}")
        # Show error to user
        error_label = QLabel(f"Video playback error: {error_string}")
        error_label.setStyleSheet("color: red; font-weight: bold; padding: 10px;")
        self.layout().insertWidget(0, error_label)
        # Disable play button
        self.play_btn.setEnabled(False)

    def cleanup_media_player(self):
        """Properly cleanup media player resources"""
        try:
            # Disconnect signals first
            self.media_player.positionChanged.disconnect()
            self.media_player.durationChanged.disconnect()
            self.media_player.errorOccurred.disconnect()

            # Stop playback
            self.media_player.stop()

            # Clear outputs to prevent resource leaks
            self.media_player.setAudioOutput(None)
            self.media_player.setVideoOutput(None)

            # Clear the source
            self.media_player.setSource(QUrl())

            # Schedule for deletion after dialog closes
            self.media_player.deleteLater()
            self.audio_output.deleteLater()

        except Exception as e:
            # Silently handle cleanup errors to prevent issues
            print(f"Warning: Media player cleanup error: {e}")
            pass
