import sys
import csv
import re
import requests
from urllib.parse import quote
import json
import os
import icons_rc
import pyttsx3
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5 import QtWidgets, QtCore, QtWebEngineWidgets, QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile
from PyQt5.QtCore import QUrl, QTimer, QFileInfo, QDir, pyqtSignal, QThread, Qt, QRunnable, QThreadPool, QEasingCurve, QPropertyAnimation, QPoint, Qt, QUrlQuery, QDateTime
from PyQt5.QtWidgets import QWidget, QCompleter, QMainWindow, QTabWidget, QLabel, QAction, QFileDialog, QStyleFactory, QListWidgetItem, QProgressBar, QFileDialog, QMenu, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QGridLayout, QApplication
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtGui import QIcon, QCursor
from datetime import datetime, timedelta
from functools import partial
from PyQt5.QtWebEngineWidgets import QWebEngineSettings

class DownloadItemWidget(QtWidgets.QWidget):
    def __init__(self, download_info):
        super().__init__()
        self.download_info = download_info
        self.init_ui()
        
    def init_ui(self):
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(16)
        
        self.icon = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(":/icons/file.svg").scaled(24, 24, 
                    QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.icon.setPixmap(pixmap)
        layout.addWidget(self.icon)
        
        content_layout = QtWidgets.QVBoxLayout()
        content_layout.setSpacing(4)
        
        self.filename = QtWidgets.QLabel()
        self.set_elided_text(self.filename, self.download_info['file_name'], 300)
        
        self.status = QtWidgets.QLabel()
        self.status.setAlignment(QtCore.Qt.AlignCenter)
        
        content_layout.addWidget(self.filename)
        content_layout.addWidget(self.status)
        layout.addLayout(content_layout)
        
        self.progress = QtWidgets.QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                height: 6px;
                background: #e9ecef;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: #4dabf7;
                border-radius: 3px;
            }
        """)
        self.progress.setValue(0)
        layout.addWidget(self.progress, 1)
        
        control_layout = QtWidgets.QHBoxLayout()
        control_layout.setSpacing(8)
        
        self.pause_btn = QtWidgets.QPushButton()
        self.pause_btn.setIcon(QtGui.QIcon(":/icons/pause.svg"))
        self.pause_btn.setStyleSheet("padding: 4px; border-radius: 4px;")
        self.pause_btn.clicked.connect(self.toggle_pause)
        
        self.cancel_btn = QtWidgets.QPushButton()
        self.cancel_btn.setIcon(QtGui.QIcon(":/icons/close.svg"))
        self.cancel_btn.setStyleSheet("padding: 4px; border-radius: 4px;")
        self.cancel_btn.clicked.connect(self.cancel_download)
        
        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.cancel_btn)
        layout.addLayout(control_layout)
        
        self.setLayout(layout)
        self.update_state()

    def set_elided_text(self, label, text, width):
        metrics = QtGui.QFontMetrics(label.font())
        elided = metrics.elidedText(text, QtCore.Qt.ElideRight, width)
        label.setText(elided)
        label.setToolTip(text)
        
    def update_progress(self, received, total):
        progress = int((received / total) * 100) if total > 0 else 0
        self.progress.setValue(progress)
        self.status.setText(f"{progress}% • {self.format_speed(received)}")
        
    def format_speed(self, bytes_received):
        return f"{bytes_received//1024} KB/s"
        
    def toggle_pause(self):
        pass
        
    def cancel_download(self):
        pass
        
    def update_state(self):
        state = self.download_info.get('state', 'active')
        states = {
            'active': {'color': '#4dabf7', 'icon': ':/icons/download.svg'},
            'paused': {'color': '#868e96', 'icon': ':/icons/pause.svg'},
            'completed': {'color': '#2b8a3e', 'icon': ':/icons/check.svg'},
            'error': {'color': '#c92a2a', 'icon': ':/icons/error.svg'}
        }
        style = states.get(state, states['active'])
        self.icon.setStyleSheet(f"color: {style['color']};")
        self.status.setStyleSheet(f"color: {style['color']};")

class DownloadManager(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            DownloadManager {
                background-color: #f8f9fa;
            }
            QListWidget {
                background: white;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 4px;
            }
        """)
        self.init_ui()
        self.downloads = {}
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.download_finished)

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header = QtWidgets.QLabel("Downloads")
        header.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: #212529;
            padding-bottom: 8px;
        """)
        header.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(header)
        
        # Downloads List
        self.download_list = QtWidgets.QListWidget()
        self.download_list.setStyleSheet("""
            QListWidget::item {
                border-bottom: 1px solid #e9ecef;
                padding: 4px;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
        """)
        layout.addWidget(self.download_list)
        
        # Empty State
        self.empty_state = QtWidgets.QWidget()
        empty_layout = QtWidgets.QVBoxLayout()
        empty_layout.setAlignment(QtCore.Qt.AlignCenter)
        
        icon = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(":/icons/download.svg").scaled(64, 64, 
                    QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        icon.setPixmap(pixmap)
        empty_layout.addWidget(icon)
        
        text = QtWidgets.QLabel("No active or completed downloads")
        text.setStyleSheet("""
            font-size: 16px;
            color: #868e96;
            padding-top: 16px;
        """)
        empty_layout.addWidget(text)
        self.empty_state.setLayout(empty_layout)
        layout.addWidget(self.empty_state)
        
    def add_download(self, url):
        file_info = QFileInfo(url.path())
        file_name = file_info.fileName()
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", QDir.homePath() + "/Downloads/" + file_name
        )
        
        if save_path:
            request = QNetworkRequest(QUrl(url))
            reply = self.network_manager.get(request)
            
            item = QtWidgets.QListWidgetItem()
            widget = DownloadItemWidget({
                'url': url.toString(),
                'file_name': file_name,
                'path': save_path,
                'state': 'active'
            })
            item.setSizeHint(widget.sizeHint())
            
            self.download_list.addItem(item)
            self.download_list.setItemWidget(item, widget)
            self.downloads[reply] = {
                'item': item,
                'widget': widget,
                'file': open(save_path, 'wb')
            }
            reply.downloadProgress.connect(
                lambda rec, tot, r=reply: self.update_progress(rec, tot, r)
            )
            
    def update_progress(self, received, total, reply):
        download = self.downloads.get(reply)
        if download:
            download['widget'].update_progress(received, total)
            
    def download_finished(self, reply):
        download = self.downloads.get(reply)
        if download:
            download['file'].close()
            self.downloads.pop(reply)
            download['widget'].download_info['state'] = 'completed'
            download['widget'].update_state()

class AboutDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About PyBrowse")
        self.setFixedSize(500, 400)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', sans-serif;
            }

            QLabel {
                font-size: 14px;
                color: #495057;
                margin: 4px 0;
            }

            QLabel#title {
                font-size: 28px;
                font-weight: 600;
                color: #212529;
            }

            QLabel#version {
                font-size: 16px;
                color: #6c757d;
            }
            
            QLabel#links {
                margin-top: 12px;
            }

            QLabel {
                font-size: 14px;
                color: #495057;
                margin: 4px 0;
            }

            QTextBrowser {
                background: transparent;
                border: none;
                color: #495057;
                font-size: 14px;
                text-align: center;
            }

            QPushButton {
                background: #e9ecef;
                border: 1px solid #dee2e6;
                color: #212529;
                padding: 8px 32px;
                min-width: 100px;
            }

            QPushButton:hover {
                background: #dee2e6;
            }

            QPushButton:pressed {
                background: #ced4da;
            }

            QLabel#build_number {
                font-size: 12px;
                color: #868e96;
                padding: 8px 0;
            }
            QFrame#separator {
                color: #dee2e6;
            }
        """)

        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15)

        icon = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(":/icons/app_icon.png").scaled(72, 72, 
                    QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        icon.setPixmap(pixmap)
        icon.setAlignment(QtCore.Qt.AlignCenter)

        title = QtWidgets.QLabel("PyBrowse")
        title.setObjectName("title")
        title.setAlignment(QtCore.Qt.AlignCenter)

        version = QtWidgets.QLabel("Version 0.3.0")
        version.setObjectName("version")
        version.setAlignment(QtCore.Qt.AlignCenter)

        desc = QtWidgets.QTextBrowser()
        desc.setPlainText(
            "A browser written in Python using the PyQt5 libraries. Part of the PySuite group of apps.\n\n"
            "© 2024 - 2025 Tay Rake\n"
            "GPL-3.0 License"
        )
        desc.setAlignment(QtCore.Qt.AlignCenter)
        desc.setFixedHeight(80)

        links_layout = QtWidgets.QVBoxLayout()
        links_layout.addWidget(self.create_centered_link("https://github.com/DivinityCube/PyBrowse", "GitHub Repository"))
        links_layout.setSpacing(10)

        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setObjectName("separator")
        main_layout.addWidget(separator)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.setContentsMargins(0, 10, 0, 0)

        build_number = QtWidgets.QLabel("Build 0.3.0.200 [Stable Release]\n30-01-2025") # the 4th number is the browser build number; it's to keep track of the amount of changes in between releases. build number resets to 1 after every new release development build (e.g. this release, 0.3.0, will still have a build number like 200 upon full release, it'll only reset in the dev build of 0.3.1)
                                                                                        # [DEV] is for development builds, [RC] is for release candidates, and nothing is for stable releases (although the build number will still be present for a full release)
        build_number.setObjectName("build_number")                                      # we'd usually have 2 release candidates on average, but it can be more or less depending on the amount of changes
        build_number.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn = QtWidgets.QPushButton("OK")
        btn.clicked.connect(self.accept)
        btn_layout.addWidget(btn)

        bottom_layout.addWidget(build_number)
        bottom_layout.addLayout(btn_layout)

        main_layout.addWidget(icon)
        main_layout.addWidget(title)
        main_layout.addWidget(version)
        main_layout.addWidget(desc)
        main_layout.addLayout(links_layout)
        main_layout.addLayout(btn_layout)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def create_centered_link(self, url, text):
        link = QtWidgets.QLabel(f'<a href="{url}" style="color: #0078d4; text-decoration: none;">{text}</a>')
        link.setAlignment(QtCore.Qt.AlignCenter)
        link.linkActivated.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(url)))
        return link

class StyledCheckBox(QtWidgets.QCheckBox):
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        text = self.text()
        font = self.font()
        text_width = self.fontMetrics().horizontalAdvance(text)
        box_size = 18
        spacing = 8
        
        box_rect = QtCore.QRect(0, (self.height()-box_size)//2, box_size, box_size)
        painter.setBrush(QtGui.QBrush(QtGui.QColor("#ffffff")))
        painter.setPen(QtGui.QPen(QtGui.QColor("#dee2e6"), 1))
        painter.drawRect(box_rect)
        
        if self.isChecked():
            painter.setPen(QtGui.QPen(QtGui.QColor("#0078d4"), 2))
            painter.drawLine(4, self.height()//2 + 1, 7, self.height()//2 + 4)
            painter.drawLine(7, self.height()//2 + 4, 14, self.height()//2 - 3)
        
        painter.setFont(font)
        painter.setPen(QtGui.QPen(self.palette().text().color()))
        text_rect = QtCore.QRect(box_size + spacing, 0, text_width, self.height())
        painter.drawText(text_rect, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, text)

    def sizeHint(self):
        text_width = self.fontMetrics().horizontalAdvance(self.text())
        return QtCore.QSize(18 + 8 + text_width + 10, 24)

class CustomNewTabPage(QWidget):
    def __init__(self, main_window, is_private=False):
        super().__init__(parent=main_window)
        self.main_window = main_window
        self.is_private = is_private
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        mode_label = QLabel("Private Browsing" if self.is_private else "Normal Browsing")
        mode_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(mode_label)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search or enter address")
        self.search_bar.returnPressed.connect(self.perform_search)
        layout.addWidget(self.search_bar)
        if not self.is_private:
            most_visited_layout = QGridLayout()
            for i in range(8):
                site_button = QPushButton(f"Site {i+1}")
                site_button.clicked.connect(partial(self.open_url, f"https://example{i+1}.com"))
                most_visited_layout.addWidget(site_button, i // 4, i % 4)
            layout.addLayout(most_visited_layout)
        quick_links_layout = QHBoxLayout()
        quick_links = [("Google", "https://www.google.com"),
                       ("YouTube", "https://www.youtube.com"),
                       ("GitHub", "https://www.github.com")]
        for name, url in quick_links:
            link_button = QPushButton(name)
            link_button.clicked.connect(partial(self.open_url, url))
            quick_links_layout.addWidget(link_button)
        layout.addLayout(quick_links_layout)
        if not self.is_private:
            weather_label = QLabel("Weather: Placeholder")
            layout.addWidget(weather_label)
            news_label = QLabel("Latest News: PyBrowse 0.3.0 Released!")
            layout.addWidget(news_label)

        self.setLayout(layout)

    def perform_search(self):
        query = self.search_bar.text()
        if not query:
            return
        
        if re.match(r'^https?://', query):
            url = QUrl(query)
        else:
            url = QUrl(f"https://www.google.com/search?q={query}")
        
        self.main_window.add_new_tab(url.toString(), is_private=self.is_private)

    def open_url(self, url):
        self.main_window.add_new_tab(url, is_private=self.is_private)

class TextToSpeechEngine(QRunnable):
    def __init__(self, text, finished_callback):
        super().__init__()
        self.engine = None  # lazy init
        self.text = text
        self.finished_callback = finished_callback

    def run(self):
        # initialize engine only when needed
        if self.engine is None:
            self.engine = pyttsx3.init()
        self.engine.say(self.text)
        self.engine.runAndWait()
        self.finished_callback()

class AccessibilityPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            AccessibilityPage {
                background-color: #f8f9fa;
            }
            
            QLabel#section_title {
                font-size: 18px;
                font-weight: 600;
                color: #212529;
                padding: 12px 0 4px 0;
            }
            
            QCheckBox {
                spacing: 12px;
                padding: 8px 0;
                font-size: 14px;
            }
            
            QScrollArea {
                border: none;
                background: transparent;
            }
            
            QLabel {
                font-size: 14px;
                color: #495057;
                line-height: 1.4;
                padding: 4px 0;
            }
            
            QLabel[type="feature"] {
                padding-left: 24px;
                background: url(:/icons/bullet.svg) left center no-repeat;
            }
        """)
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(24, 16, 24, 24)
        main_layout.setSpacing(8)

        # Header Section
        header = QtWidgets.QLabel("Accessibility Features")
        header.setAlignment(QtCore.Qt.AlignCenter)
        header.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: #212529;
            padding-bottom: 16px;
        """)
        main_layout.addWidget(header)

        # Toggles Section
        toggles_layout = QtWidgets.QVBoxLayout()
        self.high_contrast_toggle = self.create_toggle("High Contrast Mode", ":/icons/contrast.svg")
        self.tts_toggle = self.create_toggle("Text-to-Speech", ":/icons/tts.svg")
        toggles_layout.addWidget(self.high_contrast_toggle)
        toggles_layout.addWidget(self.tts_toggle)
        main_layout.addLayout(toggles_layout)

        # Features Scroll Area
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 12, 0)
        scroll_layout.setSpacing(16)

        # Feature Sections
        self.add_feature_section(scroll_layout, "Navigation",
                                ["Keyboard-first navigation design",
                                 "Focus indicators for interactive elements",
                                 "Semantic HTML structure support"])
                                 
        self.add_feature_section(scroll_layout, "Visual Adjustments",
                                ["Dynamic text scaling (Ctrl + Mouse Wheel)",
                                 "High contrast color schemes",
                                 "Reduced motion preferences"])
                                 
        self.add_feature_section(scroll_layout, "Compatibility",
                                ["Screen reader optimized (NVDA, JAWS, VoiceOver)",
                                 "Braille display support",
                                 "Keyboard navigation profiles"])

        self.add_shortcut_section(scroll_layout)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
    
    def create_toggle(self, text, icon_path):
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(12, 8, 12, 8)
        
        icon = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(icon_path).scaled(24, 24, 
                    QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        icon.setPixmap(pixmap)
        
        label = QtWidgets.QLabel(text)
        label.setStyleSheet("font-size: 15px; color: #212529;")
        
        toggle = StyledCheckBox()
        toggle.setStyleSheet("""
            QCheckBox::indicator { width: 48px; height: 28px; }
            QCheckBox::indicator:unchecked { image: url(:/icons/toggle_off.svg); }
            QCheckBox::indicator:checked { image: url(:/icons/toggle_on.svg); }
        """)
        
        layout.addWidget(icon)
        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(toggle)
        
        container.setStyleSheet("""
            background-color: white;
            border-radius: 8px;
            border: 1px solid #e9ecef;
        """)
        
        return container

    def add_feature_section(self, layout, title, items):
        section = QtWidgets.QGroupBox(title)
        section.setStyleSheet("""
            QGroupBox {
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 16px;
                margin-top: 8px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
                color: #212529;
                font-weight: 600;
            }
        """)
        
        section_layout = QtWidgets.QVBoxLayout()
        for item in items:
            label = QtWidgets.QLabel(item)
            label.setProperty("type", "feature")
            section_layout.addWidget(label)
        
        section.setLayout(section_layout)
        layout.addWidget(section)
    
    def add_shortcut_section(self, layout):
        section = QtWidgets.QWidget()
        section.setStyleSheet("background: white; border-radius: 8px; border: 1px solid #e9ecef;")
        grid = QtWidgets.QGridLayout()
        grid.setContentsMargins(16, 16, 16, 16)
        
        shortcuts = [
            ("Ctrl + Plus", "Zoom In"),
            ("Ctrl + Minus", "Zoom Out"),
            ("Ctrl + 0", "Reset Zoom"),
            ("F11", "Fullscreen Toggle"),
            ("Alt + Shift + S", "Screen Reader Toggle"),
            ("Ctrl + Alt + D", "Developer Console")
        ]
        
        for i, (keys, desc) in enumerate(shortcuts):
            key_label = QtWidgets.QLabel(keys)
            key_label.setStyleSheet("""
                font-family: 'Courier New';
                color: #495057;
                padding: 4px 8px;
                background: #f1f3f5;
                border-radius: 4px;
            """)
            
            desc_label = QtWidgets.QLabel(desc)
            desc_label.setStyleSheet("color: #495057;")
            
            grid.addWidget(key_label, i//2, 0)
            grid.addWidget(desc_label, i//2, 1)
        
        section.setLayout(grid)
        layout.addWidget(section)
    
    def toggle_high_contrast(self, state):
        if state == QtCore.Qt.Checked:
            self.window().setStyleSheet("""
                QWidget { background-color: black; color: white; }
                QLineEdit { background-color: white; color: black; }
                QPushButton { background-color: white; color: black; }
            """)
        else:
            self.window().setStyleSheet("")
    
    def toggle_tts(self, state):
        print("Text-to-speech toggled:", state == QtCore.Qt.Checked)

    def add_section(self, layout, title, items):
        section_title = QtWidgets.QLabel(title)
        section_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(section_title)

        for item in items:
            if isinstance(item, tuple):
                label = QtWidgets.QLabel(f"<b>{item[0]}:</b> {item[1]}")
            else:
                label = QtWidgets.QLabel(item)
            label.setWordWrap(True)
            layout.addWidget(label)
        layout.addSpacing(10)



class AdBlocker(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ad_hosts = set()
        self.tracker_hosts = set()
        self.cache_file = "adblocker_cache.json"
        self.cache_duration = timedelta(days=7)
        self.load_hosts()
    
    def load_hosts(self):
        if self.is_cache_valid():
            self.load_from_cache()
        else:
            self.load_ad_hosts()
            self.load_tracker_hosts()
            self.save_to_cache()
    
    def is_cache_valid(self):
        if not os.path.exists(self.cache_file):
            return False
        try:
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
            last_updated = datetime.fromisoformat(cache['last_updated'])
            return datetime.now() - last_updated < self.cache_duration
        except (json.JSONDecodeError, KeyError, ValueError):
            # invalid cache file, return False to trigger reload
            return False

    def load_from_cache(self):
        with open(self.cache_file, 'r') as f:
            cache = json.load(f)
        self.ad_hosts = set(cache['ad_hosts'])
        self.tracker_hosts = set(cache['tracker_hosts'])
    
    def save_to_cache(self):
        cache = {
            'last_updated': datetime.now().isoformat(),
            'ad_hosts': list(self.ad_hosts),
            'tracker_hosts': list(self.tracker_hosts)
        }
        with open(self.cache_file, 'w') as f:
            json.dump(cache, f)

    def load_ad_hosts(self):
        url = "https://raw.githubusercontent.com/easylist/easylist/master/easylist/easylist_adservers.txt"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                for line in response.text.splitlines():
                    if line.startswith('||') and '^' in line:
                        domain = line.split('^')[0][2:]
                        self.ad_hosts.add(domain)
            else:
                print(f"Failed to fetch ad list. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error fetching ad list: {e}")
            self.ad_hosts.update([
                'ads.google.com',
                'googleadservices.com',
                'doubleclick.net',
            ])

    def load_tracker_hosts(self):
        url = "https://raw.githubusercontent.com/easylist/easylist/master/easyprivacy/easyprivacy_trackingservers.txt"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                for line in response.text.splitlines():
                    if line.startswith('||') and '^' in line:
                        domain = line.split('^')[0][2:]
                        self.tracker_hosts.add(domain)
            else:
                print(f"Failed to fetch tracker list. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error fetching tracker list: {e}")
            self.tracker_hosts.update([
                'analytics.google.com',
                'facebook.com',
                'tracking.example.com',
            ])

    def interceptRequest(self, info):
        url = info.requestUrl()
        if self.should_block_ad(url) or self.should_block_tracker(url):
            info.block(True)

    def should_block_ad(self, url):
        host = url.host()
        # direct lookup first (fastest)
        if host in self.ad_hosts:
            return True
        # check parent domains
        return any(host.endswith('.' + ad_host) for ad_host in self.ad_hosts)

    def should_block_tracker(self, url):
        host = url.host()
        # direct lookup first (fastest)
        if host in self.tracker_hosts:
            return True
        # check parent domains
        return any(host.endswith('.' + tracker_host) for tracker_host in self.tracker_hosts)

# TODO: This new tab overhaul is very sloppy. I don't feel like this code is super polished and there are probably some gaping holes I'm too tired to fix, or even spot. Maybe in some future version I'll go over this code again
class ScrollableTabBar(QtWidgets.QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.hovered_close_index = -1
        self.pressed_close = False
        self.close_icon = self.create_close_icon()
        self.setDrawBase(False)
        self.setElideMode(QtCore.Qt.ElideRight)
        self.setUsesScrollButtons(True)
        self.setMovable(True)
        self.setExpanding(False)
        self._min_tab_width = 120
        self._max_tab_width = 250
        self.settings = QtCore.QSettings("PyBrowse", "PyBrowse")
        self.apply_style_settings()
        self.settings.sync()
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setStyleSheet("""
            QTabBar {
                background: transparent;
                margin: 0;  /* Remove margins */
                height: 30px;  /* Fixed height */
            }
            QTabBar::tab {
                background: #e9ecef;
                border: 1px solid #dee2e6;
                border-bottom: none;
                border-radius: 4px 4px 0 0;
                padding: 8px 16px;
                margin: 0 2px;
                font-weight: 500;
                color: #495057;
            }
            QTabBar::tab:selected {
                background: #f8f9fa;
                color: #212529;
                border-bottom: 1px solid white; /* Hide lower border */
            }
            QTabBar::tab:hover {
                background: #f8f9fa;
            }
        """)
        self.shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(4)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 10))
        self.shadow.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow)
    
    def create_close_icon(self):
        pixmap = QtGui.QPixmap(16, 16)
        pixmap.fill(QtCore.Qt.transparent)
        
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        pen = QtGui.QPen(self.palette().text().color())
        pen.setWidthF(1.5)
        painter.setPen(pen)
        
        painter.drawLine(4, 4, 12, 12)
        painter.drawLine(12, 4, 4, 12)
        painter.end()
        
        return QtGui.QIcon(pixmap)

    def tabLayoutChange(self):
        super().tabLayoutChange()
        self.updateGeometry()
    
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # cache pen and color for reuse
        text_color = self.palette().text().color()
        pen = QtGui.QPen(text_color)
        pen.setWidthF(1.8)
        offset = 3
        
        for index in range(self.count()):
            rect = self.tabRect(index)
            center_y = rect.center().y()
            close_rect = QtCore.QRect(
                rect.right() - 24,  # Adjusted positioning
                center_y - 6,
                16,
                16
            )
            
            # Hover/pressed state
            if index == self.hovered_close_index:
                painter.setBrush(QtGui.QColor(0, 0, 0, 20 if not self.pressed_close else 30))
                painter.setPen(QtCore.Qt.NoPen)
                painter.drawEllipse(close_rect.center(), 8, 8)
            
            # X icon - use cached pen
            painter.setPen(pen)
            center_x = close_rect.center().x()
            center_y = close_rect.center().y()
            
            painter.drawLine(
                center_x - offset, center_y - offset,
                center_x + offset, center_y + offset
            )
            painter.drawLine(
                center_x + offset, center_y - offset,
                center_x - offset, center_y + offset
            )

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        prev_hover = self.hovered_close_index
        self.hovered_close_index = -1
        
        for index in range(self.count()):
            rect = self.tabRect(index)
            close_rect = QtCore.QRect(
                rect.right() - 24,
                rect.center().y() - 6,
                16,
                16
            )
            if close_rect.contains(event.pos()):
                self.hovered_close_index = index
                break
                
        if prev_hover != self.hovered_close_index:
            self.update()
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.pressed_close = self.hovered_close_index != -1
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        if self.pressed_close and self.hovered_close_index != -1:
            self.tabCloseRequested.emit(self.hovered_close_index)
        self.pressed_close = False
        super().mouseReleaseEvent(event)

    def apply_style_settings(self):
        experimental_style = self.settings.value("experimental/tab_style", False, bool)
    
        if experimental_style:
            self.setStyleSheet("""
            QTabBar {
                background: transparent;
                margin: 0;
            }
                
            QTabBar::tab {
                background: #f1f3f5;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                margin: 4px 2px;
                color: #495057;
                font-weight: 500;
                min-width: 120px;
                max-width: 200px;
            }
                
            QTabBar::tab:selected {
                background: #e9ecef;
                color: #212529;
            }
                
            QTabBar::tab:hover {
                background: #dee2e6;
            }
                
            QTabBar::close-button {
                image: none;
                subcontrol-origin: padding;
                subcontrol-position: right;
            }  
            """)
            self.style().unpolish(self)
            self.style().polish(self)
            self.update()
        else:
            self.setStyleSheet("")
            self.style().unpolish(self)
            self.style().polish(self)
            self.update()

    def tabSizeHint(self, index):
        # cache calculations to avoid repeated computation
        if not hasattr(self, '_cached_tab_count') or self._cached_tab_count != self.count():
            self._cached_tab_count = self.count()
            self._cached_available_width = self.width() - 20  # Account for scroll buttons
            tab_count = max(1, self._cached_tab_count)
            
            # Calculate ideal width based on available space
            ideal_width = self._cached_available_width / tab_count
            self._cached_ideal_width = max(self._min_tab_width, 
                            min(ideal_width, self._max_tab_width))
            
            # Check if we actually need scroll buttons
            self._needs_scroll = (self._cached_ideal_width * tab_count) > self._cached_available_width
        
        height = super().tabSizeHint(index).height()
        
        if not self._needs_scroll:
            # Expand tabs to fill available space
            return QtCore.QSize(
                int(self._cached_available_width / self._cached_tab_count),
                height
            )
        else:
            # Use consistent minimum width with scroll
            return QtCore.QSize(self._min_tab_width, height)
    
    def minimumTabSizeHint(self, index):
        return QtCore.QSize(self._min_tab_width, 
                          super().minimumTabSizeHint(index).height())

class TabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabBar(ScrollableTabBar(self))
        self.setMovable(True)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.overflow_menu = QtWidgets.QMenu(self)
        self.setDocumentMode(True)
        self.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                margin: 0;
                padding: 0;
            }
            
            QTabWidget::tab-bar {
                alignment: left;
            }
        """)
    
    def update_tab_style(self, key):
        if key == "experimental/tab_style":
            self.tabBar().apply_style_settings()

    def close_tab(self, index):
        if self.count() > 1:
            self.removeTab(index)

    def show_overflow_menu(self, position):
        self.overflow_menu.clear()
        for i in range(self.count()):
            action = self.overflow_menu.addAction(self.tabText(i))
            action.setData(i)
        action = self.overflow_menu.exec_(self.tab_bar().mapToGlobal(position))
        if action:
            self.setCurrentIndex(action.data())

class CustomWebEnginePage(QtWebEngineWidgets.QWebEnginePage):
    console_message = QtCore.pyqtSignal(str)

    def javaScriptConsoleMessage(self, level, message, line, source):
        self.console_message.emit(f"Console: {message} (line: {line}, source: {source})")

class BrowserTab(QWebEngineView):
    def __init__(self, url="https://www.google.com", profile=None, parent=None):
        super().__init__(parent)
        self.reader_mode_active = False
        self.original_html = None
        self.settings().setAttribute(
            QWebEngineSettings.PlaybackRequiresUserGesture, False
        )
        self.settings().setAttribute(
            QWebEngineSettings.LocalStorageEnabled, True
        )
        self.image_url = None
        self.profile = profile or QWebEngineProfile.defaultProfile()
        self.web_page = QWebEnginePage(self.profile, self)
        self.setPage(self.web_page)
        self.setUrl(QUrl(url))
        self.web_page.setLifecycleState(QWebEnginePage.LifecycleState.Active)
        self.web_page.titleChanged.connect(self.handle_title_change)
        self.page().loadFinished.connect(self.on_page_loaded)
    
    def on_load_finished(self, ok):
        if ok:
            self.page.setLifecycleState(QWebEnginePage.LifecycleState.Active)
    
    def handle_title_change(self, title):
        index = self.window().tabs.indexOf(self)
        if index != -1:
            self.window().tabs.setTabText(index, title[:20])
    
    def page_loaded(self, ok):
        if ok:
            print("Page loaded successfully")
            self._page.runJavaScript("""
                document.addEventListener('contextmenu', function(e) {
                    if (e.target.tagName.toLowerCase() === 'img') {
                        window.imageUrl = e.target.src;
                        console.log('Right-clicked on image:', window.imageUrl);
                    } else {
                        window.imageUrl = null;
                        console.log('Right-clicked, but not on image');
                    }
                });
            """)
        else:
            print("Page failed to load")
    
    def contextMenuEvent(self, event):
        local_pos = event.pos()
        global_pos = event.globalPos()
        
        # optimize js execution by minimizing string formatting
        js_code = """
            (function() {
                try {
                    var elem = document.elementFromPoint(%d, %d);
                    if (!elem) return null;
                    var img = elem.closest('img');
                    return img ? {src: img.src, x: img.getBoundingClientRect().left + window.scrollX, y: img.getBoundingClientRect().top + window.scrollY} : null;
                } catch(e) {
                    return null;
                }
            })()
        """ % (local_pos.x(), local_pos.y())
        
        def handle_result(result):
            menu = QMenu(self)
            image_found = False
            
            if result and 'src' in result:
                try:
                    img_pos = QPoint(int(result['x']), int(result['y']))
                    adjusted_global_pos = self.mapToGlobal(img_pos)
                    
                    menu.addAction(QIcon(":/icons/download.svg"), "Download Image", 
                                 lambda: self.window().download_manager.add_download(result['src']))
                    menu.addAction(QIcon(":/icons/copy.svg"), "Copy Image Address",
                                 lambda: QApplication.clipboard().setText(result['src']))
                    menu.addSeparator()
                    image_found = True
                except Exception as e:
                    print("Image action error:", e)
            
            standard_menu = self.page().createStandardContextMenu()
            for action in standard_menu.actions():
                if image_found and action.text().lower() in ["save image", "copy image"]:
                    continue
                menu.addAction(action)
            
            menu.exec(adjusted_global_pos if image_found else global_pos)

        self.page().runJavaScript(js_code, handle_result)

    def speak_text(self, text):
        if self.tts_engine is not None:
            self.thread_pool.clear()
        self.tts_engine = TextToSpeechEngine(text, self.on_tts_finished)
        self.thread_pool.start(self.tts_engine)

    def on_tts_finished(self):
        print("Text-to-speech finished")
    
    def show_context_menu(self, position):
        menu = QtWidgets.QMenu(self)
        js_code = """
            var element = document.elementFromPoint(%d, %d);
            var link = element ? element.closest('a') : null;
            link ? link.href : null;
            """ % (position.x(), position.y())
        self.page().runJavaScript(js_code, lambda link_url: self.build_context_menu(menu, position, link_url))
    
    def build_context_menu(self, menu, position, link_url):
        print("Building context menu")
        self.page().runJavaScript("window.imageUrl;", self.handle_image_context_menu)
        if self.image_url:
            download_action = QAction("Download Image", self)
            download_action.triggered.connect(self.download_image)
            menu.addAction(download_action)
        if link_url:
            menu.addAction("Open Link in New Tab", lambda: self.open_link_in_new_tab(QtCore.QUrl(link_url)))
            menu.addAction("Copy Link Address", lambda: QtWidgets.QApplication.clipboard().setText(link_url))
        menu.addSeparator()
        menu.addAction("Back", self.back)
        menu.addAction("Forward", self.forward)
        menu.addAction("Reload", self.reload)
        menu.addSeparator()
        menu.addAction("View Page Source", self.view_page_source)
        menu.addAction("Save Page", self.save_page)
        menu.exec_(self.mapToGlobal(position))
    
    def download_image(self, url):
        if url:
            self.window().download_manager.add_download(url)
    
    def handle_image_context_menu(self, image_url):
        if image_url:
            print(f"Handling image context menu, image_url: {image_url}")
            self.image_url = image_url
    
    def open_link_in_new_tab(self, url):
        main_window = self.window()
        if hasattr(main_window, 'add_new_tab'):
            main_window.add_new_tab(url.toString())
    
    def view_page_source(self):
        self.page().toHtml(self.show_source_window)
    
    def show_source_window(self, html):
        if self.source_window is None:
            self.source_window = QtWidgets.QTextEdit(None)
            self.source_window.setWindowTitle("Page Source")
            self.source_window.setReadOnly(True)
            self.source_window.resize(800, 600)
            font = QtGui.QFont("Courier", 10)
            self.source_window.setFont(font)
            self.source_window.closeEvent = lambda event: self.reset_source_window(event)
        self.source_window.setPlainText(html)
        self.source_window.show()
        self.source_window.raise_()
    
    def reset_source_window(self, event):
        self.source_window = None
        event.accept()
    
    def save_page(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        dialog.setNameFilter("Web Page, Complete (*.html)")
        if dialog.exec_() == QtWidgets.QFileDialog.Accepted:
            path = dialog.selectedFiles()[0]
            self.page().save(path, QtWebEngineWidgets.QWebEngineDownloadItem.CompleteHtmlSaveFormat)
    
    def toggle_reader_mode(self):
        if not self.reader_mode_active:
            self.activate_reader_mode()
        else:
            self.deactivate_reader_mode()
        self.reader_mode_active = not self.reader_mode_active
    
    def activate_reader_mode(self):
        js = """
        (function() {
            // Save original HTML
            window.originalHTML = document.documentElement.outerHTML;
            
            // Load Readability.js
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/readability/0.4.1/Readability.js';
            script.onload = function() {
                try {
                    const doc = new Readability(document.cloneNode(true)).parse();
                    if (doc) {
                        document.body.innerHTML = `
                            <article style="
                                max-width: 800px;
                                margin: 40px auto;
                                font-family: -apple-system, sans-serif;
                                line-height: 1.6;
                                color: #374151;
                                padding: 20px;
                            ">
                            <h1>${doc.title}</h1>
                            ${doc.content}
                            </article>
                        `;
                    }
                } catch(e) {
                    console.error('Readability error:', e);
                }
            };
            document.head.appendChild(script);
        })()
        """
        self.page().runJavaScript(js)

    def deactivate_reader_mode(self):
        if self.original_html:
            self.page().runJavaScript(f"""
                document.open();
                document.write({self.original_html!r});
                document.close();
            """)
        else:
            self.reload()
    
    def on_page_loaded(self, ok):
        if ok:
            self.reader_mode_active = False
            self.page().runJavaScript("window.originalHTML", lambda result: setattr(self, 'original_html', result))
    
    def closeEvent(self, event):
        self.web_page.deleteLater()
        self.profile.setUrlRequestInterceptor(None)
        self.web_page.setParent(None)
        self.profile.deleteLater()
        super().closeEvent(event)

class PrivateBrowserTab(BrowserTab):
    def __init__(self, url="https://www.google.com", profile=None, parent=None):
        super().__init__(url, profile, parent)
        self.profile = profile or QWebEngineProfile(None)
        self.page = QWebEnginePage(self.profile, self)
        self.web_page.settings().setAttribute(QWebEngineSettings.LocalStorageEnabled, False)
        self.web_page.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.setPage(self.page)
        self.setUrl(QUrl(url))
        self.page().setLifecycleState(QWebEnginePage.LifecycleState.Active)
    
    def page_loaded(self, ok):
        if ok:
            print("Private page loaded successfully")
            self._page.runJavaScript("""
                document.addEventListener('contextmenu', function(e) {
                    if (e.target.tagName.toLowerCase() === 'img') {
                        window.imageUrl = e.target.src;
                        console.log('Right-clicked on image (private):', window.imageUrl);
                    } else {
                        window.imageUrl = null;
                        console.log('Right-clicked, but not on image (private)');
                    }
                });
            """)
        else:
            print("Private page failed to load")
    
    def closeEvent(self, event):
        super().closeEvent(event)

class HistoryPage(QtWidgets.QWidget):
    def __init__(self, history):
        super().__init__()
        self.history_data = history
        self.empty_state = None
        self.setStyleSheet("""
            HistoryPage {
                background-color: #f8f9fa;
            }
            QListWidget {
                background: white;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 4px;
            }
            QLineEdit {
                border: 1px solid #e9ecef;
                border-radius: 20px;
                padding: 8px 16px;
                font-size: 14px;
            }
        """)
        self.init_ui()
    
    def confirm_clear_history(self):
        dialog = QtWidgets.QMessageBox(self)
        dialog.setWindowTitle("Clear History")
        dialog.setText("This will permanently remove all browsing history.")
        dialog.setInformativeText("Are you sure you want to continue?")
        dialog.setIcon(QtWidgets.QMessageBox.Warning)
        dialog.setStandardButtons(
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        dialog.setDefaultButton(QtWidgets.QMessageBox.No)
        
        if dialog.exec_() == QtWidgets.QMessageBox.Yes:
            self.history_data.clear()
            self.load_history(self.history_data)
            self.update_empty_state()
    
    def export_history(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export History", "", "CSV Files (*.csv)"
        )
        if path:
            try:
                with open(path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Timestamp', 'Title', 'URL'])
                    for entry in self.history_data:
                        writer.writerow([
                            entry.get('timestamp', ''),
                            entry.get('title', ''),
                            entry.get('url', '')
                        ])
                QtWidgets.QMessageBox.information(
                    self, "Export Successful", 
                    f"History exported to:\n{path}"
                )
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Export Error", 
                    f"Failed to export history:\n{str(e)}"
                )

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(24, 16, 24, 24)
        main_layout.setSpacing(16)

        header = QtWidgets.QLabel("Browsing History")
        header.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: #212529;
            padding-bottom: 8px;
        """)
        header.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(header)

        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("Search history...")
        self.search_bar.addAction(QtGui.QIcon(":/icons/search.svg"), QtWidgets.QLineEdit.LeadingPosition)
        self.search_bar.textChanged.connect(self.filter_history)
        main_layout.addWidget(self.search_bar)

        self.history_list = QtWidgets.QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget::item {
                border-bottom: 1px solid #e9ecef;
                padding: 4px;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
            QListWidget::item:selected {
                background-color: #e7f5ff;
                border-radius: 4px;
            }
        """)
        self.history_list.setAlternatingRowColors(True)
        main_layout.addWidget(self.history_list)

        control_layout = QtWidgets.QHBoxLayout()
        
        self.clear_btn = QtWidgets.QPushButton("Clear History")
        self.clear_btn.setIcon(QtGui.QIcon(":/icons/trash.svg"))
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background:rgb(199, 0, 0);
                border: 1px solid #dee2e6;
                color:rgb(255, 96, 96);
                padding: 8px 32px;
                min-width: 100px;
            }

            QPushButton:text {
                color:rgb(255, 255, 255);
            }

            QPushButton:hover {
                background:rgb(151, 0, 0);
            }

            QPushButton:pressed {
                background:rgb(255, 63, 63);
            }
        """)
        self.clear_btn.clicked.connect(self.confirm_clear_history)
        
        self.export_btn = QtWidgets.QPushButton("Export History")
        self.export_btn.setIcon(QtGui.QIcon(":/icons/export.svg"))
        self.export_btn.setStyleSheet("""
            QPushButton {
                background: #e9ecef;
                border: 1px solid #dee2e6;
                color: #212529;
                padding: 8px 32px;
                min-width: 100px;
            }

            QPushButton:hover {
                background: #dee2e6;
            }

            QPushButton:pressed {
                background: #ced4da;
            }
        """)
        self.export_btn.clicked.connect(self.export_history)
        
        control_layout.addWidget(self.clear_btn)
        control_layout.addWidget(self.export_btn)
        control_layout.addStretch()

        main_layout.addLayout(control_layout)

        self.empty_state = QtWidgets.QWidget()
        empty_layout = QtWidgets.QVBoxLayout()
        empty_layout.setAlignment(QtCore.Qt.AlignCenter)
        
        icon = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(":/icons/clock.svg").scaled(64, 64, 
                    QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        icon.setPixmap(pixmap)
        icon.setAlignment(QtCore.Qt.AlignCenter)
        
        text = QtWidgets.QLabel("No browsing history available")
        text.setStyleSheet("""
            font-size: 16px;
            color: #868e96;
            padding-top: 16px;
        """)
        empty_layout.addWidget(icon)
        empty_layout.addWidget(text)
        self.empty_state.setLayout(empty_layout)
        main_layout.addWidget(self.empty_state)

        self.load_history(self.history_data)

    def load_history(self, history):
        self.history_list.clear()
        # iterate in reverse without creating a copy
        for i in range(len(history) - 1, -1, -1):
            entry = history[i]
            item = QtWidgets.QListWidgetItem()
            widget = HistoryItemWidget(entry)
            item.setSizeHint(widget.sizeHint())
            self.history_list.addItem(item)
            self.history_list.setItemWidget(item, widget)
        self.update_empty_state()

    def update_empty_state(self):
        self.empty_state.setVisible(self.history_list.count() == 0)

    def filter_history(self, text):
        search_text = text.lower()
        for i in range(self.history_list.count()):
            item = self.history_list.item(i)
            widget = self.history_list.itemWidget(item)
            if widget and hasattr(widget, 'entry'):
                entry = widget.entry
                # combine checks for efficiency
                is_match = (search_text in entry.get('url', '').lower() or 
                           search_text in entry.get('title', '').lower())
                item.setHidden(not is_match)


class HistoryItemWidget(QtWidgets.QWidget):
    def __init__(self, entry):
        super().__init__()
        self.entry = entry
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(16)

        self.favicon = QtWidgets.QLabel()
        self.favicon.setFixedSize(16, 16)
        self.load_favicon()
        layout.addWidget(self.favicon)

        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setSpacing(4)
        
        title = self.entry.get('title', 'No Title')
        self.title_label = QtWidgets.QLabel()
        self.set_elided_text(self.title_label, title, QtCore.Qt.ElideRight, 250)
        
        url = self.entry.get('url', 'about:blank')
        self.url_label = QtWidgets.QLabel()
        self.set_elided_text(self.url_label, url, QtCore.Qt.ElideMiddle, 350)
        
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.url_label)
        layout.addLayout(text_layout, 1)

        self.time_label = QtWidgets.QLabel(self.format_time())
        self.time_label.setStyleSheet("color: #868e96; font-size: 13px;")
        layout.addWidget(self.time_label)

        self.setLayout(layout)

    def set_elided_text(self, label, text, mode, width):
        metrics = QtGui.QFontMetrics(label.font())
        elided = metrics.elidedText(text, mode, width)
        label.setText(elided)
        label.setToolTip(text)
        label.setStyleSheet("""
            QLabel {
                color: %s;
                font-size: %s;
                font-weight: %s;
            }
        """ % (
            "#212529" if label == self.title_label else "#868e96",
            "14px" if label == self.title_label else "13px",
            "500" if label == self.title_label else "400"
        ))

    def format_time(self):
        timestamp = self.entry.get('timestamp', '')
        try:
            dt = datetime.fromisoformat(timestamp)
            return dt.strftime("%b %d, %H:%M")
        except (ValueError, TypeError):
            return "Recent"

    def load_favicon(self):
        pixmap = QtGui.QPixmap(":/icons/globe.svg").scaled(16, 16,
                    QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.favicon.setPixmap(pixmap)

class SettingsDialog(QtWidgets.QDialog):
    settings_changed = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', sans-serif;
            }

            QGroupBox {
                border: 1px solid #dee2e6;
                border-radius: 0;
                margin-top: 20px;
                padding-top: 15px;
                font-weight: 500;
                color: #212529;
                font-size: 14px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
            }

            QLineEdit {
                border: 1px solid #dee2e6;
                border-radius: 0;
                padding: 8px 12px;
                font-size: 14px;
                background: white;
                selection-background-color: #e2e6ea;
                min-width: 300px;
            }

            QLineEdit:focus {
                border-color: #adb5bd;
            }

            QComboBox {
                border: 1px solid #dee2e6;
                border-radius: 0;
                padding: 8px 12px;
                background: white;
                min-width: 200px;
            }

            QComboBox::drop-down {
                border: 0;
                width: 20px;
            }

            QComboBox QAbstractItemView {
                border: 1px solid #dee2e6;
                selection-background-color: #f1f3f5;
                selection-color: #212529;
            }

            QCheckBox {
                spacing: 0;
            }

            QCheckBox::indicator {
                width: 0;
                height: 0;
            }

            QDialogButtonBox QPushButton {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 0;
                padding: 8px 16px;
                min-width: 80px;
            }
            
            QDialogButtonBox QPushButton:hover {
                background: #e9ecef;
            }
            
            QDialogButtonBox QPushButton:pressed {
                background: #dee2e6;
            }

            QPushButton {
                background: #e9ecef;
                border: 1px solid #dee2e6;
                color: #212529;
                padding: 8px 16px;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background: #dee2e6;
            }
            
            QPushButton:pressed {
                background: #ced4da;
            }
            
            QPushButton:focus {
                border-color: #adb5bd;
            }

            QLabel[accessibleName="section_header"] {
                font-size: 16px;
                font-weight: 600;
                color: #212529;
                margin-bottom: 12px;
            }

            QWidget#experimental_section {
                border-top: 1px solid #dee2e6;
                padding-top: 16px;
                margin-top: 16px;
            }
        """)
        self.setWindowTitle("Settings")
        self.layout = QtWidgets.QVBoxLayout(self)

        search_engine_group = QtWidgets.QGroupBox("Search Engine")
        search_engine_layout = QtWidgets.QVBoxLayout()

        self.search_engine_combo = QtWidgets.QComboBox()
        self.search_engine_combo.addItems(["Google", "Bing", "DuckDuckGo", "Yandex", "Custom"])
        search_engine_layout.addWidget(self.search_engine_combo)

        self.custom_search_engine_input = QtWidgets.QLineEdit()
        self.custom_search_engine_input.setPlaceholderText("Enter custom search URL...")
        search_engine_layout.addWidget(self.custom_search_engine_input)

        search_engine_group.setLayout(search_engine_layout)
        self.layout.addWidget(search_engine_group)

        experimental_group = QtWidgets.QGroupBox("Experiments")
        experimental_layout = QtWidgets.QVBoxLayout()

        self.tab_style_toggle = StyledCheckBox("Experimental Tab Styling")
        experimental_layout.addWidget(self.tab_style_toggle)

        experimental_group.setLayout(experimental_layout)
        self.layout.insertWidget(1, experimental_group)

        self.tab_style_toggle.toggled.connect(self.preview_tab_style)

        # Buttons
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)

        self.load_settings()
    
    def preview_tab_style(self, checked):
        example_tabbar = ScrollableTabBar()
        example_tabbar.addTab("Preview Tab")
        example_tabbar.apply_style_settings()
        
        main_window = self.parent()
        if isinstance(main_window, PyBrowse):
            main_window.tabs.tabBar().apply_style_settings()

    def load_settings(self):
        settings = QtCore.QSettings("PyBrowse", "PyBrowse")
        search_engine = settings.value("search_engine", "Google")
        custom_search = settings.value("custom_search_engine", "")
        index = self.search_engine_combo.findText(search_engine)
        self.search_engine_combo.setCurrentIndex(index)
        self.custom_search_engine_input.setText(custom_search)
        experimental_tab_style = settings.value("experimental/tab_style", False, bool)
        self.tab_style_toggle.setChecked(experimental_tab_style)

    def save_settings(self):
        settings = QtCore.QSettings("PyBrowse", "PyBrowse")
        settings.setValue("search_engine", self.search_engine_combo.currentText())
        settings.setValue("custom_search_engine", self.custom_search_engine_input.text())
        settings.setValue("experimental/tab_style", self.tab_style_toggle.isChecked())
        self.settings_changed.emit()

class PyBrowse(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.network_manager = QNetworkAccessManager(self)
        self.current_search_reply = None
        self.suppress_autocomplete = False
        self.create_menu_bar()
        self.setWindowTitle("PyBrowse")
        self.setGeometry(100, 100, 1024, 768)
        self.bookmarks_file = "bookmarks.json"
        self.history_file = "history.json"
        self.is_private_mode = False
        self.search_engine = "Google"
        self.custom_search_engine = ""
        self.bookmarks = []
        self.history = []
        self.local_urls = []  # cache for completer performance
        self.is_fullscreen = False
        self.default_profile = QWebEngineProfile.defaultProfile()
        self.default_profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
        self.private_profile = QWebEngineProfile("private")
        self.private_profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.tabs = TabWidget(self)
        self.layout.addWidget(self.tabs)
        self.completer_model = QtCore.QStringListModel()
        self.completer = QCompleter(self.completer_model, self) 
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.create_navigation_bar()
        self.layout.addWidget(self.navigation_bar)
        self.tabs.currentChanged.connect(self.activate_current_tab)
        self.url_bar.setCompleter(self.completer)
        self.url_bar.textEdited.connect(self.fetch_search_suggestions)
        self.load_bookmarks()
        self.load_history()
        self.load_user_settings()
        self.update_completer_model()
        self.download_manager = DownloadManager()
        self.add_new_tab("https://www.google.com")
        self.create_fullscreen_toggle()
        self.search_timer = QtCore.QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.fetch_search_suggestions)
        self.setStyleSheet("""
            QMainWindow {
                background: #ffffff;
                border: none;
            }
            QToolBar {
                background: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
                padding: 4px;
            }
            QLineEdit {
                border: 1px solid #dee2e6;
                border-radius: 0;
                padding: 6px 12px;
                font-size: 14px;
            }
        """)
    
    def handle_text_changes(self):
        if not self.url_bar.text():
            self.completer_model.setStringList([])
            self.url_bar.setPlaceholderText("Search or enter address")
    
    def activate_current_tab(self, index):
        widget = self.tabs.widget(index)
        if widget and isinstance(widget, BrowserTab):
            widget.web_page.setLifecycleState(QWebEnginePage.LifecycleState.Active)

    def handle_settings_change(self):
        self.load_user_settings()
        tab_bar = self.tabs.tabBar()
        if isinstance(tab_bar, ScrollableTabBar):
            tab_bar.apply_style_settings()
            tab_bar.updateGeometry()
            self.tabs.repaint()
        
    def apply_tab_style_settings(self):
        tab_bar = self.tabs.tabBar()
        if isinstance(tab_bar, ScrollableTabBar):
            tab_bar.apply_style_settings()
            tab_bar.updateGeometry()
            self.tabs.repaint()
    
    
    def update_completer_model(self):
        try:
            # use set comprehension for better performance
            url_set = {
                entry.get('url', '') 
                for entry in self.history + self.bookmarks
                if isinstance(entry, dict) and entry.get('url')
            }
            # remove empty strings and convert to sorted list
            self.local_urls = sorted([url for url in url_set if url])
            self.completer_model.setStringList(self.local_urls)
            
            # force completer refresh
            self.completer.complete()
        except Exception as e:
            print(f"Completer error: {e}")

    
    def fetch_search_suggestions(self):
        try:
            query = self.url_bar.text().strip()
            if not query:
                self.handle_text_changes()
                return
            
            self.url_bar.setPlaceholderText("Search or enter address")
            
            # optimize local search by using cached urls
            query_lower = query.lower()
            local_matches = [
                url for url in self.local_urls
                if query_lower in url.lower()
            ][:5]
            
            self.completer_model.setStringList(local_matches)
            
            if self.current_search_reply:
                self.current_search_reply.abort()
            
            url = QUrl("https://suggestqueries.google.com/complete/search")
            query_params = QUrlQuery()
            query_params.addQueryItem("client", "firefox")
            query_params.addQueryItem("q", query)
            url.setQuery(query_params)
            
            request = QNetworkRequest(url)
            self.current_search_reply = self.network_manager.get(request)
            self.current_search_reply.finished.connect(
                lambda: self.handle_online_suggestions(self.current_search_reply, query)
            )
            
        except Exception as e:
            print(f"Search error: {e}")
    
    def handle_online_suggestions(self, reply, original_query):
        try:
            if reply.error() == QNetworkReply.NoError:
                data = bytes(reply.readAll()).decode('utf-8')
                online_suggestions = json.loads(data)[1]
                
                current = self.completer_model.stringList()
                combined = list(set(current + online_suggestions))[:10]
                
                self.completer_model.setStringList(combined)
                self.completer.complete()
        except Exception as e:
            print(f"Suggestion error: {e}")
        finally:
            reply.deleteLater()
            self.current_search_reply = None

    def add_new_tab(self, url=None, is_private=False):
        self.suppress_autocomplete = True
        if url is None or isinstance(url, bool):  # handle bad parameters
            url = "about:blank"
            
        # convert to QUrl and validate
        qurl = QUrl(url)
        if not qurl.isValid():
            qurl = QUrl("https://www.google.com/search?q=" + url)
        
        if is_private:
            tab = PrivateBrowserTab(qurl.toString(), self.private_profile)
        else:
            tab = BrowserTab(qurl.toString(), self.default_profile)

        tab_index = self.tabs.addTab(tab, "Loading...")
        tab.titleChanged.connect(self.update_tab_title)
        tab.urlChanged.connect(self.on_url_changed)
        self.tabs.setCurrentIndex(tab_index)

        self.suppress_autocomplete = False
        
        # add to history after page loads
        tab.page().loadFinished.connect(
            lambda ok, url=url: self.add_to_history(url)
        )

    def on_url_changed(self, qurl):
        if not self.suppress_autocomplete:
            self.update_url_bar(qurl)

    def update_frame(self):
        self.repaint()
    
    def create_private_mode_toggle(self):
        private_mode_action = QtWidgets.QAction("Private Mode", self)
        private_mode_action.setCheckable(True)
        private_mode_action.toggled.connect(self.toggle_private_mode)
        self.navigation_bar.addAction(private_mode_action)

    def toggle_private_mode(self, enabled):
        self.is_private_mode = enabled
        if enabled:
            self.setWindowTitle("PyBrowse (Private Mode)")
        else:
            self.setWindowTitle("PyBrowse")
    
    def open_accessibility_page(self):
        accessibility_page = AccessibilityPage(self)
        i = self.tabs.addTab(accessibility_page, "Accessibility")
        self.tabs.setCurrentIndex(i)
    
    def set_application_style(self):
        QtWidgets.QApplication.setStyle(QStyleFactory.create("Fusion"))
        dark_palette = QtGui.QPalette()
        dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
        dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
        dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
        dark_palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
        QtWidgets.QApplication.setPalette(dark_palette)
        self.setStyleSheet("""
            QToolBar {
                background-color: #2b2b2b;
                border: none;
                padding: 5px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 3px;
                padding: 5px;
            }
            QToolBar QToolButton:hover {
                background-color: #3a3a3a;
            }
            QToolBar QLineEdit {
                background-color: #1e1e1e;
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                color: white;
                padding: 3px;
            }
        """)

    def create_navigation_bar(self):
        self.navigation_bar = QtWidgets.QToolBar("Main Navigation")
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.navigation_bar)
        self.navigation_bar.setMovable(False)
        self.navigation_bar.setIconSize(QtCore.QSize(24, 24))

        # Navigation controls
        controls = [
            ('back', 'Back', self.go_back, 'back.svg'),
            ('forward', 'Forward', self.go_forward, 'forward.svg'),
            ('reload', 'Reload', self.reload_page, 'reload.svg'),
            ('new_tab', 'New Tab', lambda: self.add_new_tab(), 'new_tab.svg'),
            ('private', 'Private Mode', self.toggle_private_mode, 'private.svg'),
            ('downloads', 'Downloads', self.open_download_manager, 'download.svg'),
            # The Developer Console (internally known as the Developer Tools) WILL be returning in 0.4.0. Due to the amount of problems it's causing, it's been temporarily deprecated.
            ('dev_tools', 'Developer Console', self.open_dev_tools, 'dev_tools.svg'),
            ('history', 'History', self.open_history_page, 'history.svg'),
            ('reader_mode', 'Reader Mode', self.toggle_reader_mode, 'reader.svg'),
            ('fullscreen', 'Fullscreen', self.toggle_fullscreen, 'fullscreen.svg')
        ]

        for action_id, text, handler, icon in controls:
            btn = QAction(QIcon(f":/icons/{icon}"), text, self)
            btn.triggered.connect(handler)
            if action_id == 'private':
                btn.setCheckable(True)
                self.private_mode_action = btn
            self.navigation_bar.addAction(btn)

        # URL Bar with improved search handling
        self.url_bar = QLineEdit()
        self.url_bar.textEdited.connect(self.handle_user_typing)
        self.url_bar.focusInEvent = self.url_bar_focused
        self.url_bar.setPlaceholderText("Search or enter address")
        self.url_bar.setClearButtonEnabled(True)
        self.url_bar.setMinimumWidth(400)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.navigation_bar.addWidget(self.url_bar)

        # Visual styling
        self.navigation_bar.setStyleSheet("""
            QToolBar {
                background: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
                padding: 4px 8px;
            }
            QToolButton {
                padding: 6px 8px;
                background: transparent;
                border-radius: 4px;
                transition: background 0.2s ease;
            }
            QToolButton:hover {
                background: rgba(233, 236, 239, 0.6);
            }
            QToolButton:pressed {
                background: rgba(206, 212, 218, 0.7);
            }
            QToolButton[checked="true"] {
                background: rgba(206, 212, 218, 0.5);
            }
        """)

        self.completer.popup().setStyleSheet(f"""
            QListView {{
                background: {self.url_bar.palette().base().color().name()};
                border: 1px solid {self.url_bar.palette().mid().color().name()};
                border-radius: 0;
                padding: 0;
                font: {self.url_bar.font().toString()};
                color: {self.url_bar.palette().text().color().name()};
            }}
            QListView::item {{
                padding: 8px 16px;
                margin: 0;
            }}
            QListView::item:hover {{
                background: {self.url_bar.palette().alternateBase().color().name()};
            }}
            QListView::item:selected {{
                background: {self.url_bar.palette().highlight().color().name()};
                color: {self.url_bar.palette().highlightedText().color().name()};
                border-radius: 0;
            }}
        """)
    
        self.completer = QCompleter(self.url_bar)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setModel(self.completer_model)
        self.url_bar.setCompleter(self.completer)
        self.url_bar.textChanged.connect(self.handle_text_changes)
    
    def handle_user_typing(self):
        if not self.suppress_autocomplete:
            self.start_search_timer()
    
    def start_search_timer(self):
        if self.suppress_autocomplete:
            return

    def url_bar_focused(self, event):
        QtWidgets.QLineEdit.focusInEvent(self.url_bar, event)
        if self.url_bar.text():
            self.completer.complete()
    
    def open_dev_tools(self):
        QtWidgets.QMessageBox.information(
            self,
            "Coming Soon",
            "The Developer Console is being redesigned for v0.4.0.\n"
            "Please use Chromium's DevTools (F12) for now.",
        )
    
    def open_download_manager(self):
        for i in range(self.tabs.count()):
            if isinstance(self.tabs.widget(i), DownloadManager):
                self.tabs.setCurrentIndex(i)
                return
        download_tab_index = self.tabs.addTab(self.download_manager, "Downloads")
        self.tabs.setCurrentIndex(download_tab_index)


    def go_forward(self):
        if self.tabs.count() > 0:
            self.tabs.currentWidget().forward()

    def create_fullscreen_toggle(self):
        self.fullscreen_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("F11"), self)
        self.fullscreen_shortcut.activated.connect(self.toggle_fullscreen)

    def toggle_fullscreen(self):
        if not self.is_fullscreen:
            self.showFullScreen()
            self.is_fullscreen = True
        else:
            self.showNormal()
            self.is_fullscreen = False
        self.central_widget.setGeometry(self.rect())

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction("New Window", lambda: PyBrowse().show())
        file_menu.addAction("Exit", self.close)
        settings_menu = menu_bar.addMenu("&Settings")
        settings_action = QAction("Preferences...", self)
        settings_action.triggered.connect(self.open_settings_dialog)
        settings_menu.addAction(settings_action)
        help_menu = menu_bar.addMenu("&Help")
        help_menu.addAction("About", self.show_about_dialog)
        help_menu.addAction("Accessibility", self.open_accessibility_page)
    
    def open_settings_dialog(self):
        dialog = SettingsDialog(self)
        dialog.settings_changed.connect(self.handle_settings_change)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            dialog.save_settings()
    
    def refresh_tab_styles(self):
        """Update styling for all tabs"""
        tab_bar = self.tabs.tabBar()
        if isinstance(tab_bar, ScrollableTabBar):
            tab_bar.settings.sync()
            tab_bar.apply_style_settings()
            tab_bar.updateGeometry()
            self.tabs.repaint()

    def load_user_settings(self):
        settings = QtCore.QSettings("PyBrowse", "PyBrowse")
        self.search_engine = settings.value("search_engine", "Google", str)
        self.custom_search_engine = settings.value("custom_search_engine", "", str)

    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec_()
    
    def update_tab_title(self, title):
        tab = self.sender()  # get the tab that emitted the signal
        if tab and isinstance(tab, (BrowserTab, PrivateBrowserTab)):
            index = self.tabs.indexOf(tab)
            if index != -1:
                # shorten long titles
                display_title = title[:20] + "..." if len(title) > 23 else title
                self.tabs.setTabText(index, display_title)
                self.tabs.setTabToolTip(index, title)

    def close_tab(self, index):
        """Close the tab at the given index."""
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def navigate_to_url(self):
        query = self.url_bar.text().strip()
        if not query:
            return

        if re.match(r'^https?://', query, re.IGNORECASE):
            url = QtCore.QUrl(query)
        elif '.' in query and ' ' not in query:
            url = QtCore.QUrl(f"http://{query}")
        else:
            url = QtCore.QUrl(self.get_search_url(query))
        
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, BrowserTab):
            current_tab.setUrl(url)
            self.add_to_history(url.toString())

    def get_search_url(self, query):
        if self.search_engine == "Google":
            return f"https://www.google.com/search?q={quote(query)}"
        elif self.search_engine == "Bing":
            return f"https://www.bing.com/search?q={quote(query)}"
        elif self.search_engine == "DuckDuckGo":
            return f"https://duckduckgo.com/?q={quote(query)}"
        elif self.search_engine == "Yandex":
            return f"https://yandex.com/search/?text={quote(query)}&lang=en"
        elif self.search_engine == "Custom" and self.custom_search_engine:
            return self.custom_search_engine.replace("{query}", quote(query))
        else:
            # Default to Google if no valid search engine is selected
            return f"https://www.google.com/search?q={quote(query)}"

    def update_url_bar(self, q, browser=None):
        if browser != self.tabs.currentWidget():
            return
        if isinstance(q, int):
            # This is likely an index, not a URL. Let's ignore it.
            return
        if not isinstance(q, QUrl):
            # This is essentially saying: if it's not a QUrl object, try to convert it
            # (Rough English translation, of course)
            q = QUrl(str(q))
        if q.toString() == 'about:blank':
            return
        self.url_bar.setText(q.toString())
        self.url_bar.setCursorPosition(0)

    def go_back(self):
        """Go back in the history of the current tab."""
        if self.tabs.count() > 0:
            self.tabs.currentWidget().back()

    def reload_page(self):
        """Reload the current page in the active tab."""
        if self.tabs.count() > 0:
            self.tabs.currentWidget().reload()

    def open_history_page(self):
        """Open a new tab with the browsing history."""
        history_tab = HistoryPage(self.history)
        i = self.tabs.addTab(history_tab, "History")
        self.tabs.setCurrentIndex(i)

    def add_to_history(self, url):
        if not self.is_private_mode:
            current_tab = self.tabs.currentWidget()
            title = ""
            
            if isinstance(current_tab, BrowserTab):
                title = current_tab.page().title()
            else:
                title = QUrl(url).host() or url[:50]  # use domain or first 50 chars
            
            # avoid duplicate consecutive entries
            if not self.history or self.history[-1].get('url') != url:
                self.history.append({
                    'url': url,
                    'title': title,
                    'timestamp': datetime.now().isoformat()
                })
                # trim history if it exceeds limit
                if len(self.history) > 500:
                    self.history = self.history[-500:]
                self.save_history()
                self.update_completer_model()

    def add_bookmark(self):
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, BrowserTab):
            url = current_tab.url().toString()
            title = current_tab.page().title()
            entry = {
                'url': url,
                'title': title,
                'created': datetime.now().isoformat()
            }
            if entry not in self.bookmarks:
                self.bookmarks.append(entry)
            self.save_bookmarks()
            self.update_completer_model()

    def toggle_reader_mode(self):
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, BrowserTab):
            current_tab.toggle_reader_mode()

    def load_bookmarks_menu(self):
        """Load the saved bookmarks into the Bookmarks menu."""
        actions = self.bookmarks_menu.actions()[2:]
        for action in actions:
            self.bookmarks_menu.removeAction(action)
        for bookmark in self.bookmarks:
            bookmark_action = QtWidgets.QAction(bookmark, self)
            bookmark_action.triggered.connect(lambda checked, url=bookmark: self.tabs.currentWidget().setUrl(QtCore.QUrl(url)))
            self.bookmarks_menu.addAction(bookmark_action)

    def save_bookmarks(self):
        """Save the bookmarks to a JSON file."""
        with open(self.bookmarks_file, 'w') as f:
            json.dump(self.bookmarks, f)

    def load_bookmarks(self):
        self.bookmarks = []
        if os.path.exists(self.bookmarks_file):
            with open(self.bookmarks_file, 'r') as f:
                bookmarks_data = json.load(f)
                for entry in bookmarks_data:
                    if isinstance(entry, str):
                        self.bookmarks.append({
                            'url': entry,
                            'title': entry,
                            'created': datetime.now().isoformat()
                        })
                    else:
                        self.bookmarks.append(entry)

    def save_history(self):
        """Save the history to a JSON file."""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f)

    def load_history(self):
        self.history = []
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                history_data = json.load(f)
                for entry in history_data:
                    if isinstance(entry, str):
                        self.history.append({
                            'url': entry,
                            'title': entry,
                            'timestamp': datetime.now().isoformat()
                        })
                    else:
                        self.history.append(entry)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape and self.is_fullscreen:
            self.toggle_fullscreen()
        else:
            super().keyPressEvent(event)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateGeometry()
        self.update()
    
    def create_tts_toggle(self):
        self.tts_action = QAction("Enable Text-to-Speech", self)
        self.tts_action.setCheckable(True)
        self.tts_action.toggled.connect(self.toggle_tts)
        self.navigation_bar.addAction(self.tts_action)

    def toggle_tts(self, enabled):
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if isinstance(tab, BrowserTab):
                tab.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu if enabled else QtCore.Qt.NoContextMenu)
    
    # To also prevent memory leaks and such 
    def closeEvent(self, event):
        while self.tabs.count() > 0:
            widget = self.tabs.widget(0)
            self.tabs.removeTab(0)
            if hasattr(widget, 'close'):
                widget.close()
            widget.deleteLater()
        if hasattr(self, 'download_manager'):
            self.download_manager.close()
            self.download_manager.deleteLater()
        event.accept()

    def start_cleanup(self):
        while self.tabs.count() > 0:
            tab = self.tabs.widget(0)
            self.tabs.removeTab(0)
            if isinstance(tab, BrowserTab):
                tab.close()
                tab.deleteLater()
        QTimer.singleShot(100, self.delayed_cleanup)

    def delayed_cleanup(self):
        self.tabs.deleteLater()
        self.close()
    


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    QtCore.QCoreApplication.setOrganizationName("PyBrowse")
    QtCore.QCoreApplication.setOrganizationDomain("pybrowse.example.com")
    QtCore.QCoreApplication.setApplicationName("PyBrowse")
    window = PyBrowse()
    window.show()
    sys.exit(app.exec_())