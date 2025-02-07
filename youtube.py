import sys
import os
import re
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QComboBox, QFileDialog, QMessageBox, QProgressBar)
from PyQt5.QtCore import QThread, pyqtSignal
import yt_dlp

class DownloadThread(QThread):
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(float)

    def __init__(self, url, output_path, format_option):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.format_option = format_option

    def run(self):
        try:
            ydl_opts = {
                'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best' if self.format_option == "video" else 'bestaudio/best',
                'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
            }
            
            if self.format_option == "video":
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mov',
                }]
            else:  # audio
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }]
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            self.finished.emit(True, "Download completato con successo!")
        except Exception as e:
            self.finished.emit(False, f"Errore durante il download: {str(e)}")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            p = d['_percent_str']
            p = re.sub(r'\x1b\[[0-9;]*m', '', p)  # Rimuove i caratteri di escape ANSI
            p = p.replace('%','')
            self.progress.emit(float(p))
        elif d['status'] == 'finished':
            self.progress.emit(100.0)

class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('YouTube Downloader (QuickTime Compatible)')
        self.setGeometry(300, 300, 450, 200)
        
        layout = QVBoxLayout()

        # URL input
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL YouTube:"))
        self.url_input = QLineEdit()
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # Output folder selection
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel("Cartella di destinazione:"))
        self.folder_input = QLineEdit()
        folder_layout.addWidget(self.folder_input)
        self.browse_button = QPushButton("Sfoglia")
        self.browse_button.clicked.connect(self.browse_folder)
        folder_layout.addWidget(self.browse_button)
        layout.addLayout(folder_layout)

        # Format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Formato:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Video MOV (massimo 1080p)", "Audio MP3 (alta qualità)"])
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }

            QProgressBar::chunk {
                background-color: #05B8CC;
                width: 20px;
            }
        """)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # Download button
        self.download_button = QPushButton("Scarica")
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button)

        self.setLayout(layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleziona cartella di destinazione")
        if folder:
            self.folder_input.setText(folder)

    def start_download(self):
        url = self.url_input.text()
        output_path = self.folder_input.text()
        format_option = "video" if self.format_combo.currentIndex() == 0 else "audio"

        if not url or not output_path:
            QMessageBox.warning(self, "Errore", "Inserisci l'URL e seleziona la cartella di destinazione.")
            return

        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.download_button.setEnabled(False)

        self.download_thread = DownloadThread(url, output_path, format_option)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(int(value))

    def on_download_finished(self, success, message):
        self.download_button.setEnabled(True)
        self.progress_bar.hide()
        if success:
            QMessageBox.information(self, "Successo", message)
        else:
            QMessageBox.warning(self, "Errore", message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = YouTubeDownloader()
    ex.show()
    sys.exit(app.exec_())
