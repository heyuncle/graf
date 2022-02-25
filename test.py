import sys
import os

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QUrl, QFile, QIODevice,  QBuffer
from PyQt5.QtMultimedia import QMediaContent, QMediaPlaylist, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget


class SimplePlayer(QMainWindow):
    """
    Extremely simple video player using QMediaPlayer
    Consists of vertical layout, widget, and a QLabel
    """

    def __init__(self, master=None):
        QMainWindow.__init__(self, master)

        # Define file variables
        self.playlist_files = ['video_file_1.mp4', 'video_file_2.mp4']

        # Define the ui-specific variables we're going to use
        self.vertical_box_layout = QVBoxLayout()
        self.central_widget = QWidget(self)
        self.video_frame = QVideoWidget()

        # Define the media player related information
        self.playlist = QMediaPlaylist()
        self.video_player = QMediaPlayer(flags=QMediaPlayer.VideoSurface)

        # Create the user interface, set up the player, and play the 2 videos
        self.create_user_interface()
        self.video_player_setup()

    def video_player_setup(self):
        """Sets media list for the player and then sets output to the video frame"""
        self.video_player.setVideoOutput(self.video_frame)

        self.set_buffer()
        # self.set_playlist()
        self.video_player.play()

    def set_playlist(self):
        """Opens a single video file, puts it into a playlist which is read by the QMediaPlayer"""
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(os.path.abspath(self.playlist_files[0]))))
        self.playlist.setCurrentIndex(0)
        self.video_player.setPlaylist(self.playlist)

    def set_buffer(self):
        """Opens a single video file and writes it to a buffer to be read by QMediaPlayer"""
        media_file_name = os.path.abspath(self.playlist_files[0])
        media_file = QFile(media_file_name)
        media_file.open(QIODevice.ReadOnly)

        byte_array = media_file.readAll()
        buffer = QBuffer(byte_array)
        buffer.setData(byte_array)

        buffer.open(QIODevice.ReadOnly)

        self.video_player.setMedia(QMediaContent(), buffer)

    def create_user_interface(self):
        """Create a 1280x720 UI consisting of a vertical layout, central widget, and QLabel"""
        self.setCentralWidget(self.central_widget)
        self.vertical_box_layout.addWidget(self.video_frame)
        self.central_widget.setLayout(self.vertical_box_layout)

        self.resize(1280, 720)


if __name__ == '__main__':
    app = QApplication([])
    player = SimplePlayer()
    player.show()
    sys.exit(app.exec_())
