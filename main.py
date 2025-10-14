import sys
import csv
import re
import requests
from urllib.parse import quote
import json
import os
import icons_rc
import pyttsx3
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEnginePage, QWebEngineProfile, QWebEngineSettings, QWebEngineDownloadRequest
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QTimer, QFileInfo, QDir, pyqtSignal, QThread, Qt, QRunnable, QThreadPool, QEasingCurve, QPropertyAnimation, QPoint, QUrlQuery, QDateTime
from PyQt6.QtWidgets import QWidget, QCompleter, QMainWindow, QTabWidget, QLabel, QFileDialog, QStyleFactory, QListWidgetItem, QProgressBar, QMenu, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QGridLayout, QApplication
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt6.QtGui import QIcon, QCursor, QAction, QPalette
from datetime import datetime, timedelta
from functools import partial

# Modern Design System
class DesignSystem:
    """Modern design tokens for PyBrowse"""
    
    @staticmethod
    def is_dark_mode():
        """Detect system dark mode"""
        app = QApplication.instance()
        if app:
            palette = app.palette()
            bg_color = palette.color(QPalette.ColorRole.Window)
            # If background is darker than midpoint, it's dark mode
            return bg_color.lightness() < 128
        return False
    
    @staticmethod
    def get_theme():
        """Get current theme colors based on system preference"""
        is_dark = DesignSystem.is_dark_mode()
        
        if is_dark:
            return {
                # Dark theme
                'background': '#1a1a1a',
                'surface': '#252525',
                'surface_variant': '#2d2d2d',
                'surface_elevated': '#333333',
                'text_primary': '#e8e8e8',
                'text_secondary': '#a8a8a8',
                'text_tertiary': '#787878',
                'border': '#404040',
                'border_subtle': '#2d2d2d',
                'accent': '#4a9eff',
                'accent_hover': '#6db3ff',
                'accent_pressed': '#2e8aff',
                'success': '#48c774',
                'warning': '#ffdd57',
                'error': '#f14668',
                'overlay': 'rgba(0, 0, 0, 0.6)',
                'tab_bg': '#2d2d2d',
                'tab_active': '#3d3d3d',
                'tab_hover': '#353535',
                'input_bg': '#2d2d2d',
                'input_border': '#404040',
                'toolbar_bg': '#1f1f1f',
                'statusbar_bg': '#1f1f1f',
                'tooltip_bg': '#3d3d3d',
                'shadow': 'rgba(0, 0, 0, 0.4)',
            }
        else:
            return {
                # Light theme
                'background': '#f5f7fa',
                'surface': '#ffffff',
                'surface_variant': '#f8f9fa',
                'surface_elevated': '#ffffff',
                'text_primary': '#1a1a1a',
                'text_secondary': '#4a4a4a',
                'text_tertiary': '#787878',
                'border': '#e0e0e0',
                'border_subtle': '#f0f0f0',
                'accent': '#0066ff',
                'accent_hover': '#0052cc',
                'accent_pressed': '#003d99',
                'success': '#00c851',
                'warning': '#ffbb33',
                'error': '#ff4444',
                'overlay': 'rgba(0, 0, 0, 0.3)',
                'tab_bg': '#e9ecef',
                'tab_active': '#ffffff',
                'tab_hover': '#f1f3f5',
                'input_bg': '#ffffff',
                'input_border': '#dee2e6',
                'toolbar_bg': '#fafbfc',
                'statusbar_bg': '#fafbfc',
                'tooltip_bg': '#3d3d3d',
                'shadow': 'rgba(0, 0, 0, 0.1)',
            }
    
    @staticmethod
    def get_stylesheet():
        """Generate complete stylesheet based on current theme"""
        theme = DesignSystem.get_theme()
        
        return f"""
            /* Main Window */
            QMainWindow {{
                background: {theme['background']};
            }}
            
            /* Toolbar */
            QToolBar {{
                background: {theme['toolbar_bg']};
                border: none;
                border-bottom: 1px solid {theme['border']};
                padding: 8px 12px;
                spacing: 8px;
            }}
            
            QToolBar QToolButton {{
                background: transparent;
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 6px;
                color: {theme['text_primary']};
            }}
            
            QToolBar QToolButton:hover {{
                background: {theme['surface_variant']};
                border-color: {theme['border_subtle']};
            }}
            
            QToolBar QToolButton:pressed {{
                background: {theme['surface']};
            }}
            
            QToolBar QToolButton:checked {{
                background: {theme['accent']};
                color: white;
                border-color: {theme['accent']};
            }}
            
            /* Tab Widget */
            QTabWidget {{
                background: transparent;
                border: none;
            }}
            
            QTabWidget::pane {{
                background: {theme['surface']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                margin: 0;
                padding: 0;
            }}
            
            QTabBar {{
                background: transparent;
            }}
            
            QTabBar::tab {{
                background: {theme['tab_bg']};
                border: 1px solid {theme['border']};
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 10px 20px;
                margin: 0 2px;
                color: {theme['text_secondary']};
                font-weight: 500;
                min-width: 120px;
                max-width: 250px;
            }}
            
            QTabBar::tab:selected {{
                background: {theme['tab_active']};
                color: {theme['text_primary']};
                border-bottom: 2px solid {theme['accent']};
            }}
            
            QTabBar::tab:hover:!selected {{
                background: {theme['tab_hover']};
            }}
            
            /* Line Edit (URL Bar) */
            QLineEdit {{
                background: {theme['input_bg']};
                border: 1px solid {theme['input_border']};
                border-radius: 8px;
                padding: 10px 16px;
                color: {theme['text_primary']};
                font-size: 14px;
                selection-background-color: {theme['accent']};
            }}
            
            QLineEdit:focus {{
                border-color: {theme['accent']};
                background: {theme['surface']};
            }}
            
            /* Buttons */
            QPushButton {{
                background: {theme['accent']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 13px;
            }}
            
            QPushButton:hover {{
                background: {theme['accent_hover']};
            }}
            
            QPushButton:pressed {{
                background: {theme['accent_pressed']};
            }}
            
            QPushButton:disabled {{
                background: {theme['surface_variant']};
                color: {theme['text_tertiary']};
            }}
            
            /* Status Bar */
            QStatusBar {{
                background: {theme['statusbar_bg']};
                border-top: 1px solid {theme['border']};
                color: {theme['text_secondary']};
                padding: 4px 12px;
            }}
            
            QStatusBar QLabel {{
                color: {theme['text_secondary']};
                padding: 4px 8px;
            }}
            
            /* Progress Bar */
            QProgressBar {{
                background: {theme['surface_variant']};
                border: 1px solid {theme['border']};
                border-radius: 4px;
                height: 6px;
                text-align: center;
            }}
            
            QProgressBar::chunk {{
                background: {theme['accent']};
                border-radius: 3px;
            }}
            
            /* Scroll Bars */
            QScrollBar:vertical {{
                background: {theme['surface']};
                width: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {theme['border']};
                border-radius: 6px;
                min-height: 30px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {theme['text_tertiary']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                background: {theme['surface']};
                height: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:horizontal {{
                background: {theme['border']};
                border-radius: 6px;
                min-width: 30px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background: {theme['text_tertiary']};
            }}
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            
            /* List Widget */
            QListWidget {{
                background: {theme['surface']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                padding: 4px;
                color: {theme['text_primary']};
            }}
            
            QListWidget::item {{
                border-radius: 6px;
                padding: 8px 12px;
                margin: 2px;
            }}
            
            QListWidget::item:hover {{
                background: {theme['surface_variant']};
            }}
            
            QListWidget::item:selected {{
                background: {theme['accent']};
                color: white;
            }}
            
            /* Completer Popup */
            QCompleter {{
                background: {theme['surface_elevated']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
            }}
            
            /* Menu */
            QMenu {{
                background: {theme['surface_elevated']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                padding: 6px;
                color: {theme['text_primary']};
            }}
            
            QMenu::item {{
                padding: 8px 24px 8px 12px;
                border-radius: 6px;
            }}
            
            QMenu::item:selected {{
                background: {theme['surface_variant']};
            }}
            
            QMenu::separator {{
                height: 1px;
                background: {theme['border']};
                margin: 4px 8px;
            }}
            
            /* Tooltip */
            QToolTip {{
                background: {theme['tooltip_bg']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
            }}
        """

class ScrollableTabBar(QtWidgets.QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.hovered_close_index = -1
        self.pressed_close = False
        self.close_icon = self.create_close_icon()
        self.setDrawBase(False)
        self.setElideMode(QtCore.Qt.TextElideMode.ElideRight)
        self.setUsesScrollButtons(True)
        self.setMovable(True)
        self.setExpanding(False)
        self._min_tab_width = 120
        self._max_tab_width = 250
        self.settings = QtCore.QSettings("PyBrowse", "PyBrowse")
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self._default_tab_style = """
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
        """
        self._experimental_tab_style = """
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
        """
        self.apply_style_settings()
        self.settings.sync()
        self.shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(4)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 10))
        self.shadow.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow)

    def create_close_icon(self):
        pixmap = QtGui.QPixmap(16, 16)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
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
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        for index in range(self.count()):
            rect = self.tabRect(index)
            close_rect = QtCore.QRect(
                rect.right() - 24,  # Adjusted positioning
                rect.center().y() - 6,
                16,
                16
            )
            # Hover/pressed state
            if index == self.hovered_close_index:
                painter.setBrush(QtGui.QColor(0, 0, 0, 20 if not self.pressed_close else 30))
                painter.setPen(QtCore.Qt.PenStyle.NoPen)
                painter.drawEllipse(close_rect.center(), 8, 8)
            # X icon
            pen = QtGui.QPen(self.palette().text().color())
            pen.setWidthF(1.8)
            painter.setPen(pen)
            offset = 3
            painter.drawLine(
                close_rect.center().x() - offset,
                close_rect.center().y() - offset,
                close_rect.center().x() + offset,
                close_rect.center().y() + offset
            )
            painter.drawLine(
                close_rect.center().x() + offset,
                close_rect.center().y() - offset,
                close_rect.center().x() - offset,
                close_rect.center().y() + offset
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
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.pressed_close = self.hovered_close_index != -1
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.pressed_close and self.hovered_close_index != -1:
            self.tabCloseRequested.emit(self.hovered_close_index)
        self.pressed_close = False
        super().mouseReleaseEvent(event)

    def apply_style_settings(self):
        """Apply modern theme-aware tab styling"""
        theme = DesignSystem.get_theme()
        
        modern_tab_style = f"""
            QTabBar {{
                background: transparent;
                margin: 0;
            }}
            QTabBar::tab {{
                background: {theme['tab_bg']};
                border: 1px solid {theme['border']};
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 10px 40px 10px 16px;
                margin: 0 2px;
                font-weight: 500;
                color: {theme['text_secondary']};
                min-width: 100px;
            }}
            QTabBar::tab:selected {{
                background: {theme['tab_active']};
                color: {theme['text_primary']};
                border-bottom: 2px solid {theme['accent']};
            }}
            QTabBar::tab:hover:!selected {{
                background: {theme['tab_hover']};
            }}
        """
        
        self.setStyleSheet(modern_tab_style)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def tabSizeHint(self, index):
        available_width = self.width() - 20  # Account for scroll buttons
        tab_count = max(1, self.count())
        ideal_width = available_width / tab_count
        ideal_width = max(self._min_tab_width, min(ideal_width, self._max_tab_width))
        if (ideal_width * tab_count) <= available_width:
            return QtCore.QSize(
                int(available_width / tab_count),
                super().tabSizeHint(index).height()
            )
        else:
            return QtCore.QSize(self._min_tab_width, super().tabSizeHint(index).height())

    def minimumTabSizeHint(self, index):
        return QtCore.QSize(self._min_tab_width, super().minimumTabSizeHint(index).height())

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
                    QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
        self.icon.setPixmap(pixmap)
        layout.addWidget(self.icon)
        
        content_layout = QtWidgets.QVBoxLayout()
        content_layout.setSpacing(4)
        
        self.filename = QtWidgets.QLabel()
        self.set_elided_text(self.filename, self.download_info['file_name'], 300)

        self.status_label = QtWidgets.QLabel()
        self.status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        content_layout.addWidget(self.filename)
        content_layout.addWidget(self.status_label)
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
        self.status_label.setText(f"{progress}% • {self.format_speed(received)}")
        
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
        self.status_label.setStyleSheet(f"color: {style['color']};")

class DownloadManager(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            DownloadManager {
                background-color: #f8f9fa;
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
            font-size: 28px;
            font-weight: 800;
            color: #212529;
            padding-bottom: 12px;
            letter-spacing: 1px;
        """)
        header.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(header)

        # Responsive, grouped card area
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none; background: transparent;")
        self.cards_container = QtWidgets.QWidget()
        self.cards_layout = QtWidgets.QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(0)
        self.cards_container.setLayout(self.cards_layout)
        self.scroll_area.setWidget(self.cards_container)
        layout.addWidget(self.scroll_area)

        # Empty State
        self.empty_state = QtWidgets.QWidget()
        empty_layout = QtWidgets.QVBoxLayout()
        empty_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        icon = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(":/icons/download.svg").scaled(80, 80, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
        icon.setPixmap(pixmap)
        empty_layout.addWidget(icon)
        text = QtWidgets.QLabel("No downloads yet!\nYour downloads will appear here as beautiful cards.")
        text.setStyleSheet("font-size: 18px; color: #868e96; padding-top: 18px; font-weight: 500;")
        text.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(text)
        self.empty_state.setLayout(empty_layout)
        layout.addWidget(self.empty_state)
        self.empty_state.hide()

        # Grouping: keep track of group headers
        self.group_headers = {}
        
    def add_download(self, url):
        url = QUrl(url)
        file_info = QFileInfo(url.path())
        file_name = file_info.fileName() or "download"
        save_path, _ = QFileDialog.getSaveFileName(self, "Save File", QDir.homePath() + "/Downloads/" + file_name)
        if save_path:
            request = QNetworkRequest(url)
            reply = self.network_manager.get(request)
            download_info = {
                'file_name': file_name,
                'state': 'active',
                'received': 0,
                'total': 0,
                'speed': 0,
            }
            widget = DownloadItemWidget(download_info)
            # Grouping: Active, Completed, Error
            group = 'Active'
            self._add_card_to_group(widget, group)
            self.downloads[reply] = {
                'widget': widget,
                'file': open(save_path, 'wb'),
                'file_name': file_name,
                'info': download_info,
                'group': group
            }
            reply.downloadProgress.connect(lambda received, total, r=reply: self.update_progress(received, total, r))
            reply.readyRead.connect(lambda r=reply: self.save_data(r))
            self.update_empty_state()

    def _add_card_to_group(self, widget, group):
        # Add group header if not present
        if group not in self.group_headers:
            header = QtWidgets.QLabel(group)
            header.setStyleSheet("font-size: 20px; font-weight: 700; color: #495057; padding: 18px 0 8px 0;")
            self.cards_layout.addWidget(header)
            self.group_headers[group] = header
        self.cards_layout.addWidget(widget)
            
    def update_progress(self, received, total, reply):
        download = self.downloads.get(reply)
        if download:
            download['info']['received'] = received
            download['info']['total'] = total
            widget = download['widget']
            widget.update_progress(received, total)
            
    def save_data(self, reply):
        """Save downloaded data to file as it becomes available."""
        download = self.downloads.get(reply)
        if download:
            data = reply.readAll()
            download['file'].write(data)
            
    def download_finished(self, reply):
        download = self.downloads.get(reply)
        if download:
            download['file'].close()
            # Move card to Completed group
            widget = download['widget']
            widget.download_info['state'] = 'completed'
            widget.update_state()
            # Remove from old group and re-add to Completed
            self.cards_layout.removeWidget(widget)
            widget.setParent(None)
            self._add_card_to_group(widget, 'Completed')
            self.downloads.pop(reply)
        self.update_empty_state()

    def update_empty_state(self):
        """Update the visibility of the empty state widget based on download count."""
        has_downloads = len(self.downloads) > 0
        self.empty_state.setVisible(not has_downloads)
        self.scroll_area.setVisible(has_downloads)

class AboutDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About PyBrowse")
        self.setFixedSize(500, 400)
        
        theme = DesignSystem.get_theme()
        self.setStyleSheet(f"""
            QDialog {{
                background: {theme['background']};
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            }}

            QLabel {{
                font-size: 14px;
                color: {theme['text_secondary']};
                margin: 4px 0;
            }}

            QLabel#title {{
                font-size: 28px;
                font-weight: 600;
                color: {theme['text_primary']};
            }}

            QLabel#version {{
                font-size: 16px;
                color: {theme['text_secondary']};
            }}
            
            QLabel#links {{
                margin-top: 12px;
            }}

            QTextBrowser {{
                background: transparent;
                border: none;
                color: {theme['text_secondary']};
                font-size: 14px;
                text-align: center;
            }}

            QPushButton {{
                background: {theme['accent']};
                border: none;
                border-radius: 6px;
                color: white;
                padding: 10px 32px;
                min-width: 100px;
                font-weight: 500;
            }}

            QPushButton:hover {{
                background: {theme['accent_hover']};
            }}

            QPushButton:pressed {{
                background: {theme['accent_pressed']};
            }}

            QLabel#build_number {{
                font-size: 12px;
                color: {theme['text_tertiary']};
                padding: 8px 0;
            }}
            QFrame#separator {{
                color: {theme['border']};
            }}
        """)

        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15)

        icon = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(":/icons/app_icon.png").scaled(72, 72, 
                    QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
        icon.setPixmap(pixmap)
        icon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        title = QtWidgets.QLabel("PyBrowse")
        title.setObjectName("title")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        version = QtWidgets.QLabel("Version 0.3.1")
        version.setObjectName("version")
        version.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        desc = QtWidgets.QTextBrowser()
        desc.setPlainText(
            "A browser written in Python using the PyQt6 libraries. Part of the PySuite group of apps.\n\n"
            "© 2024 - 2025 Tay Rake\n"
            "GPL-3.0 License"
        )
        desc.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        desc.setFixedHeight(80)

        links_layout = QtWidgets.QVBoxLayout()
        links_layout.addWidget(self.create_centered_link("https://github.com/DivinityCube/PyBrowse", "GitHub Repository"))
        links_layout.setSpacing(10)

        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        separator.setObjectName("separator")
        main_layout.addWidget(separator)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.setContentsMargins(0, 10, 0, 0)

        build_number = QtWidgets.QLabel("Build 0.3.1.297 [RC 1]\n11-10-2025") # the 4th number is the browser build number; it's to keep track of the amount of changes in between releases. build number resets to 1 after every new release development build (e.g. this release, 0.3.1, will still have a build number e.g. 140 upon full release, it'll only reset in the dev build of 0.3.1)
                                                                                        # [DEV] is for development builds, [RC] is for release candidates, and nothing is for stable releases (although the build number will still be present for a full release)
        build_number.setObjectName("build_number")                                      # we'd usually have 2 release candidates on average, but it can be more or less depending on the amount of changes
        build_number.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)

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
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def create_centered_link(self, url, text):
        link = QtWidgets.QLabel(f'<a href="{url}" style="color: #0078d4; text-decoration: none;">{text}</a>')
        link.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        link.linkActivated.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(url)))
        return link

class StyledCheckBox(QtWidgets.QCheckBox):
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        
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
        painter.drawText(text_rect, QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter, text)

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
        mode_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
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
            news_label = QLabel("Latest News: PyBrowse 0.3.1 Released!")
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
        self.engine = pyttsx3.init()
        self.text = text
        self.finished_callback = finished_callback

    def run(self):
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
        self.settings = QtCore.QSettings("PyBrowse", "PyBrowse")
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(24, 16, 24, 24)
        main_layout.setSpacing(8)

        # Header Section
        header = QtWidgets.QLabel("Accessibility Settings")
        header.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("""
            font-size: 26px;
            font-weight: 700;
            color: #212529;
            padding-bottom: 16px;
        """)
        main_layout.addWidget(header)

        # Toggles Section (with labels, tooltips, and state)
        toggles_layout = QtWidgets.QFormLayout()
        toggles_layout.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        toggles_layout.setFormAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        toggles_layout.setHorizontalSpacing(24)
        toggles_layout.setVerticalSpacing(12)

        # Use QLabel with icon pixmap for the label
        contrast_icon_label = QtWidgets.QLabel()
        contrast_icon_label.setPixmap(QtGui.QPixmap(":/icons/contrast.svg").scaled(20, 20, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation))
        contrast_icon_label.setToolTip("High Contrast Mode")
        self.high_contrast_switch = StyledCheckBox("Enable High Contrast Mode")
        self.high_contrast_switch.setToolTip("Switch to a high-contrast color scheme for better visibility.")
        # Restore state from settings
        high_contrast_enabled = self.settings.value("accessibility/high_contrast", False, type=bool)
        self.high_contrast_switch.setChecked(high_contrast_enabled)
        self.high_contrast_switch.stateChanged.connect(self.toggle_high_contrast)
        toggles_layout.addRow(contrast_icon_label, self.high_contrast_switch)

        tts_icon_label = QtWidgets.QLabel()
        tts_icon_label.setPixmap(QtGui.QPixmap(":/icons/tts.svg").scaled(20, 20, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation))
        tts_icon_label.setToolTip("Text-to-Speech")
        self.tts_switch = StyledCheckBox("Enable Text-to-Speech")
        self.tts_switch.setToolTip("Read web page content aloud using text-to-speech.")
        tts_enabled = self.settings.value("accessibility/tts", False, type=bool)
        self.tts_switch.setChecked(tts_enabled)
        self.tts_switch.stateChanged.connect(self.toggle_tts)
        toggles_layout.addRow(tts_icon_label, self.tts_switch)

        # Add shortcut info for toggles
        shortcut_label = QtWidgets.QLabel("Shortcut: Alt+Shift+S (Screen Reader)")
        shortcut_label.setStyleSheet("color: #868e96; font-size: 13px;")
        toggles_layout.addRow("", shortcut_label)

        main_layout.addLayout(toggles_layout)

        # Features Scroll Area (unchanged)
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 12, 0)
        scroll_layout.setSpacing(16)

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

        # Accessibility: set tab order for keyboard navigation
        self.setTabOrder(self.high_contrast_switch, self.tts_switch)
        self.setTabOrder(self.tts_switch, self)

        # Focus first toggle by default
        self.high_contrast_switch.setFocus()

    def save_settings(self):
        self.settings.setValue("accessibility/high_contrast", self.high_contrast_switch.isChecked())
        self.settings.setValue("accessibility/tts", self.tts_switch.isChecked())
        self.settings.sync()

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)
    
    # Removed: create_toggle (replaced with direct switches and labels for clarity)

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
        if state == QtCore.Qt.CheckState.Checked:
            QtWidgets.QApplication.instance().setStyleSheet("""
                QWidget { background-color: black; color: white; }
                QLineEdit { background-color: white; color: black; }
                QPushButton { background-color: white; color: black; }
            """)
        else:
            QtWidgets.QApplication.instance().setStyleSheet("")
        self.save_settings()
    
    def toggle_tts(self, state):
        # This would enable/disable TTS globally; here we just print, but you could connect to app logic
        if state == QtCore.Qt.CheckState.Checked:
            QtWidgets.QMessageBox.information(self, "Text-to-Speech Enabled", "Text-to-Speech is now enabled. Select text and use the context menu to read aloud.")
        else:
            QtWidgets.QMessageBox.information(self, "Text-to-Speech Disabled", "Text-to-Speech is now disabled.")
        self.save_settings()

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


class AdBlocker(QtCore.QObject):
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
        with open(self.cache_file, 'r') as f:
            cache = json.load(f)
        last_updated = datetime.fromisoformat(cache['last_updated'])
        return datetime.now() - last_updated < self.cache_duration

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
            ])

    def init_ui(self):
        card = QtWidgets.QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 14px;
                border: 1.5px solid #e9ecef;
                box-shadow: 0 2px 8px rgba(0,0,0,0.04);
                margin-bottom: 8px;
            }
        """)
        card_layout = QtWidgets.QHBoxLayout(card)
        card_layout.setContentsMargins(18, 12, 18, 12)
        card_layout.setSpacing(18)

        self.icon = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(":/icons/file.svg").scaled(32, 32, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
        self.icon.setPixmap(pixmap)
        self.icon.setFixedSize(36, 36)
        card_layout.addWidget(self.icon)

        content_layout = QtWidgets.QVBoxLayout()
        content_layout.setSpacing(2)

        self.filename = QtWidgets.QLabel()
        self.filename.setStyleSheet("font-size: 16px; font-weight: 600; color: #212529;")
        self.set_elided_text(self.filename, self.download_info['file_name'], 320)

        self.status_label = QtWidgets.QLabel()
        self.status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.status_label.setStyleSheet("font-size: 13px; color: #868e96;")

        content_layout.addWidget(self.filename)
        content_layout.addWidget(self.status_label)
        card_layout.addLayout(content_layout, 2)

        self.progress = QtWidgets.QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                height: 8px;
                background: #f1f3f5;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background: #4dabf7;
                border-radius: 4px;
            }
        """)
        self.progress.setValue(0)
        self.progress.setFixedWidth(120)
        card_layout.addWidget(self.progress, 0, QtCore.Qt.AlignmentFlag.AlignVCenter)

        control_layout = QtWidgets.QHBoxLayout()
        control_layout.setSpacing(6)

        self.pause_btn = QtWidgets.QPushButton()
        self.pause_btn.setIcon(QtGui.QIcon(":/icons/pause.svg"))
        self.pause_btn.setStyleSheet("padding: 4px; border-radius: 4px; background: #f8f9fa;")
        self.pause_btn.setFixedSize(28, 28)
        self.pause_btn.clicked.connect(self.toggle_pause)

        self.cancel_btn = QtWidgets.QPushButton()
        self.cancel_btn.setIcon(QtGui.QIcon(":/icons/close.svg"))
        self.cancel_btn.setStyleSheet("padding: 4px; border-radius: 4px; background: #f8f9fa;")
        self.cancel_btn.setFixedSize(28, 28)
        self.cancel_btn.clicked.connect(self.cancel_download)

        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.cancel_btn)
        card_layout.addLayout(control_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(card)
        self.setLayout(main_layout)
        self.update_state()
    
    def create_close_icon(self):
        pixmap = QtGui.QPixmap(16, 16)
        pixmap.fill(QtCore.Qt.transparent)
        
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
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
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        
        for index in range(self.count()):
            rect = self.tabRect(index)
            close_rect = QtCore.QRect(
                rect.right() - 24,  # Adjusted positioning
                rect.center().y() - 6,
                16,
                16
            )
            
            # Hover/pressed state
            if index == self.hovered_close_index:
                painter.setBrush(QtGui.QColor(0, 0, 0, 20 if not self.pressed_close else 30))
                painter.setPen(QtCore.Qt.NoPen)
                painter.drawEllipse(close_rect.center(), 8, 8)
            
            # X icon
            pen = QtGui.QPen(self.palette().text().color())
            pen.setWidthF(1.8)
            painter.setPen(pen)
            
            offset = 3
            painter.drawLine(
                close_rect.center().x() - offset,
                close_rect.center().y() - offset,
                close_rect.center().x() + offset,
                close_rect.center().y() + offset
            )
            painter.drawLine(
                close_rect.center().x() + offset,
                close_rect.center().y() - offset,
                close_rect.center().x() - offset,
                close_rect.center().y() + offset
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
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
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
            self.setStyleSheet(self._experimental_tab_style)
        else:
            self.setStyleSheet(self._default_tab_style)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def tabSizeHint(self, index):
        # Calculate available width minus scroll buttons if needed
        available_width = self.width() - 20  # Account for scroll buttons
        tab_count = max(1, self.count())
        
        # Calculate ideal width based on available space
        ideal_width = available_width / tab_count
        ideal_width = max(self._min_tab_width, 
                        min(ideal_width, self._max_tab_width))
        
        # Check if we actually need scroll buttons
        if (ideal_width * tab_count) <= available_width:
            # Expand tabs to fill available space
            return QtCore.QSize(
                int(available_width / tab_count),
                super().tabSizeHint(index).height()
            )
        else:
            # Use consistent minimum width with scroll
            return QtCore.QSize(self._min_tab_width, 
                              super().tabSizeHint(index).height())
    
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

class CustomWebEnginePage(QWebEnginePage):
    console_message = QtCore.pyqtSignal(str)

    def javaScriptConsoleMessage(self, level, message, line, source):
        self.console_message.emit(f"Console: {message} (line: {line}, source: {source})")

class BrowserTab(QWebEngineView):
    def __init__(self, url="https://www.google.com", profile=None, parent=None):
        super().__init__(parent)
        self.reader_mode_active = False
        self.original_html = None
        self.tts_engine = None
        self.thread_pool = QThreadPool()
        self.settings().setAttribute(
            QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False
        )
        self.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalStorageEnabled, True
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

        js_code = f"""
            (function() {{
                try {{
                    var elem = document.elementFromPoint({local_pos.x()}, {local_pos.y()});
                    if (!elem) return null;
                    var img = elem.closest('img');
                    return img ? {{
                        src: img.src,
                        x: img.getBoundingClientRect().left + window.scrollX,
                        y: img.getBoundingClientRect().top + window.scrollY
                    }} : null;
                }} catch(e) {{
                    return null;
                }}
            }})()
        """

        def handle_result(result):
            menu = QMenu(self)
            image_found = False

            # Check if TTS is enabled in settings
            tts_enabled = QtCore.QSettings("PyBrowse", "PyBrowse").value("accessibility/tts", False, type=bool)
            if tts_enabled:
                # Get selected text from the page
                self.page().runJavaScript("window.getSelection().toString();", lambda selected_text: self._add_tts_action(menu, selected_text, result, global_pos))
            else:
                self._add_tts_action(menu, None, result, global_pos)

        self.page().runJavaScript(js_code, handle_result)

    def _add_tts_action(self, menu, selected_text, result, global_pos):
        image_found = False
        adjusted_global_pos = global_pos
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

        # Add TTS action if enabled and text is selected
        tts_enabled = QtCore.QSettings("PyBrowse", "PyBrowse").value("accessibility/tts", False, type=bool)
        if tts_enabled and selected_text and selected_text.strip():
            menu.addAction(QIcon(), "Read Aloud", lambda: self.speak_text(selected_text.strip()))
            menu.addSeparator()

        standard_menu = self.page().createStandardContextMenu()
        for action in standard_menu.actions():
            if image_found and action.text().lower() in ["save image", "copy image"]:
                continue
            menu.addAction(action)

        menu.exec(adjusted_global_pos if image_found else global_pos)

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
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptMode.AcceptSave)
        dialog.setNameFilter("Web Page, Complete (*.html)")
        if dialog.exec() == QtWidgets.QFileDialog.DialogCode.Accepted:
            path = dialog.selectedFiles()[0]
            self.page().save(path, QWebEngineDownloadRequest.SavePageFormat.CompleteHtmlSaveFormat)
    
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
        self.web_page.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, False)
        self.web_page.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
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
        dialog.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        dialog.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        dialog.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
        
        if dialog.exec() == QtWidgets.QMessageBox.StandardButton.Yes:
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
                    QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
        icon.setPixmap(pixmap)
        icon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
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
        for entry in reversed(history):
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
                url_match = search_text in widget.entry.get('url', '').lower()
                title_match = search_text in widget.entry.get('title', '').lower()
                item.setHidden(not (url_match or title_match))


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
                    QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
        self.favicon.setPixmap(pixmap)

class SettingsDialog(QtWidgets.QDialog):
    settings_changed = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Apply modern design system
        theme = DesignSystem.get_theme()
        self.setStyleSheet(f"""
            QDialog {{
                background: {theme['background']};
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            }}

            QGroupBox {{
                border: 1px solid {theme['border']};
                border-radius: 8px;
                margin-top: 20px;
                padding: 16px;
                font-weight: 500;
                color: {theme['text_primary']};
                font-size: 14px;
                background: {theme['surface']};
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 8px;
                background: {theme['surface']};
            }}

            QLineEdit {{
                border: 1px solid {theme['input_border']};
                border-radius: 6px;
                padding: 10px 14px;
                font-size: 14px;
                background: {theme['input_bg']};
                color: {theme['text_primary']};
                selection-background-color: {theme['accent']};
                selection-color: white;
                min-width: 300px;
            }}

            QLineEdit:focus {{
                border-color: {theme['accent']};
                background: {theme['surface']};
            }}

            QComboBox {{
                border: 1px solid {theme['input_border']};
                border-radius: 6px;
                padding: 10px 14px;
                background: {theme['input_bg']};
                color: {theme['text_primary']};
                min-width: 200px;
            }}

            QComboBox:focus {{
                border-color: {theme['accent']};
            }}

            QComboBox::drop-down {{
                border: none;
                width: 24px;
                padding-right: 4px;
            }}

            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {theme['text_secondary']};
                margin-right: 6px;
            }}

            QComboBox QAbstractItemView {{
                border: 1px solid {theme['border']};
                border-radius: 6px;
                background: {theme['surface_elevated']};
                selection-background-color: {theme['accent']};
                selection-color: white;
                padding: 4px;
                color: {theme['text_primary']};
            }}

            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                border-radius: 4px;
                min-height: 24px;
            }}

            QComboBox QAbstractItemView::item:hover {{
                background: {theme['surface_variant']};
            }}

            QCheckBox {{
                spacing: 8px;
                color: {theme['text_primary']};
            }}

            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {theme['border']};
                background: {theme['input_bg']};
            }}

            QCheckBox::indicator:hover {{
                border-color: {theme['accent']};
            }}

            QCheckBox::indicator:checked {{
                background: {theme['accent']};
                border-color: {theme['accent']};
                image: none;
            }}

            QCheckBox::indicator:checked::after {{
                content: "✓";
                color: white;
            }}

            QDialogButtonBox QPushButton {{
                background: {theme['surface_variant']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 10px 20px;
                min-width: 80px;
                color: {theme['text_primary']};
                font-weight: 500;
            }}
            
            QDialogButtonBox QPushButton:hover {{
                background: {theme['surface']};
                border-color: {theme['accent']};
            }}
            
            QDialogButtonBox QPushButton:pressed {{
                background: {theme['accent']};
                color: white;
            }}

            QDialogButtonBox QPushButton[text="OK"] {{
                background: {theme['accent']};
                color: white;
                border-color: {theme['accent']};
            }}

            QDialogButtonBox QPushButton[text="OK"]:hover {{
                background: {theme['accent_hover']};
            }}

            QDialogButtonBox QPushButton[text="OK"]:pressed {{
                background: {theme['accent_pressed']};
            }}

            QPushButton {{
                background: {theme['accent']};
                border: none;
                border-radius: 6px;
                color: white;
                padding: 10px 20px;
                min-width: 80px;
                font-weight: 500;
            }}
            
            QPushButton:hover {{
                background: {theme['accent_hover']};
            }}
            
            QPushButton:pressed {{
                background: {theme['accent_pressed']};
            }}

            QLabel {{
                color: {theme['text_primary']};
            }}

            QLabel[accessibleName="section_header"] {{
                font-size: 16px;
                font-weight: 600;
                color: {theme['text_primary']};
                margin-bottom: 12px;
            }}

            QWidget#experimental_section {{
                border-top: 1px solid {theme['border']};
                padding-top: 16px;
                margin-top: 16px;
            }}
        """)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setSpacing(16)
        self.layout.setContentsMargins(20, 20, 20, 20)

        search_engine_group = QtWidgets.QGroupBox("Search Engine")
        search_engine_layout = QtWidgets.QVBoxLayout()
        search_engine_layout.setSpacing(12)

        self.search_engine_combo = QtWidgets.QComboBox()
        self.search_engine_combo.addItems(["Google", "Bing", "DuckDuckGo", "Yandex", "Custom"])
        search_engine_layout.addWidget(self.search_engine_combo)

        self.custom_search_engine_input = QtWidgets.QLineEdit()
        self.custom_search_engine_input.setPlaceholderText("Enter custom search URL (use {query} for search term)...")
        search_engine_layout.addWidget(self.custom_search_engine_input)

        search_engine_group.setLayout(search_engine_layout)
        self.layout.addWidget(search_engine_group)

        experimental_group = QtWidgets.QGroupBox("Experiments")
        experimental_layout = QtWidgets.QVBoxLayout()
        experimental_layout.setSpacing(12)

        self.tab_style_toggle = StyledCheckBox("Experimental Tab Styling")
        experimental_layout.addWidget(self.tab_style_toggle)

        experimental_group.setLayout(experimental_layout)
        self.layout.insertWidget(1, experimental_group)

        self.tab_style_toggle.toggled.connect(self.preview_tab_style)

        # Buttons
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel,
            QtCore.Qt.Orientation.Horizontal, self)
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
        self.is_fullscreen = False
        self.default_profile = QWebEngineProfile.defaultProfile()
        self.default_profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        self.private_profile = QWebEngineProfile("private")
        self.private_profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.tabs = TabWidget(self)
        self.layout.addWidget(self.tabs)
        self.completer_model = QtCore.QStringListModel()
        self.completer = QCompleter(self.completer_model, self) 
        self.completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self.create_navigation_bar()
        self.layout.addWidget(self.navigation_bar)
        self.tabs.currentChanged.connect(self.activate_current_tab)
        self.url_bar.setCompleter(self.completer)
        self.url_bar.textEdited.connect(self.fetch_search_suggestions)
        
        # Create status bar
        self.create_status_bar()
        
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
        
        # Add keyboard shortcuts for zoom
        self.zoom_in_shortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+="), self)
        self.zoom_in_shortcut.activated.connect(lambda: self.zoom_page(0.1))
        self.zoom_out_shortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+-"), self)
        self.zoom_out_shortcut.activated.connect(lambda: self.zoom_page(-0.1))
        self.reset_zoom_shortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+0"), self)
        self.reset_zoom_shortcut.activated.connect(self.reset_zoom)
        
        # Apply modern design system
        self.apply_modern_theme()
    
    def apply_modern_theme(self):
        """Apply the modern design system theme"""
        self.setStyleSheet(DesignSystem.get_stylesheet())
    
    def eventFilter(self, obj, event):
        """Detect system theme changes"""
        if event.type() == QtCore.QEvent.Type.ApplicationPaletteChange:
            # System theme changed, reapply our theme
            QtCore.QTimer.singleShot(0, self.refresh_theme)
        return super().eventFilter(obj, event)
    
    def refresh_theme(self):
        """Refresh theme after system palette change"""
        self.apply_modern_theme()
        # Update all tab bars
        tab_bar = self.tabs.tabBar()
        if isinstance(tab_bar, ScrollableTabBar):
            tab_bar.apply_style_settings()
        # Refresh status bar with new theme
        self.refresh_status_bar_theme()
    
    def handle_text_changes(self):
        if not self.url_bar.text():
            self.completer_model.setStringList([])
            self.url_bar.setPlaceholderText("Search or enter address")
    
    def activate_current_tab(self, index):
        widget = self.tabs.widget(index)
        if widget and isinstance(widget, BrowserTab):
            widget.web_page.setLifecycleState(QWebEnginePage.LifecycleState.Active)
            self.update_zoom_display()  # Update zoom display when switching tabs

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
            # use list comprehension with explicit checks
            self.local_urls = list(set(
                entry.get('url', '') for entry in self.history + self.bookmarks
                if isinstance(entry, dict) and 'url' in entry
            ))
            self.completer_model.setStringList(self.local_urls)
            
            # Model updated, completer will show suggestions when user types
        except Exception as e:
            print(f"Completer error: {e}")

    
    def fetch_search_suggestions(self):
        try:
            query = self.url_bar.text().strip()
            if not query:
                self.handle_text_changes()
                return
            
            self.url_bar.setPlaceholderText("Search or enter address")
            
            local_matches = [
                entry['url'] for entry in self.history + self.bookmarks
                if query.lower() in entry.get('url', '').lower()
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
            if reply.error() == QNetworkReply.NetworkError.NoError:
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
        tab.setFocus()  # Set focus to the web view instead of URL bar

        # Connect loading progress
        tab.page().loadProgress.connect(self.show_loading_progress)

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
        dark_palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtCore.Qt.GlobalColor.white)
        dark_palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(25, 25, 25))
        dark_palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtCore.Qt.GlobalColor.white)
        dark_palette.setColor(QtGui.QPalette.ColorRole.ToolTipText, QtCore.Qt.GlobalColor.white)
        dark_palette.setColor(QtGui.QPalette.ColorRole.Text, QtCore.Qt.GlobalColor.white)
        dark_palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtCore.Qt.GlobalColor.white)
        dark_palette.setColor(QtGui.QPalette.ColorRole.BrightText, QtCore.Qt.GlobalColor.red)
        dark_palette.setColor(QtGui.QPalette.ColorRole.Link, QtGui.QColor(42, 130, 218))
        dark_palette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(42, 130, 218))
        dark_palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtCore.Qt.GlobalColor.black)
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
        self.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, self.navigation_bar)
        self.navigation_bar.setMovable(False)
        self.navigation_bar.setIconSize(QtCore.QSize(24, 24))

        # Navigation controls with home button
        controls = [
            ('back', 'Back', self.go_back, 'back.svg'),
            ('forward', 'Forward', self.go_forward, 'forward.svg'),
            ('reload', 'Reload', self.reload_page, 'reload.svg'),
            ('home', 'Home', self.go_home, 'home.svg'),
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

        # URL Bar with enhanced design and security indicator
        self.url_bar_container = QtWidgets.QWidget()
        self.url_bar_container.setStyleSheet("""
            QWidget {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 25px;
                padding: 2px;
                margin: 0 8px;
            }
        """)

        url_bar_layout = QtWidgets.QHBoxLayout(self.url_bar_container)
        url_bar_layout.setContentsMargins(12, 6, 12, 6)
        url_bar_layout.setSpacing(8)

        # Security indicator
        self.security_indicator = QtWidgets.QLabel()
        self.security_indicator.setFixedSize(16, 16)
        self.security_indicator.setStyleSheet("color: #6c757d;")
        url_bar_layout.addWidget(self.security_indicator)

        # URL input field
        self.url_bar = QLineEdit()
        self.url_bar.textEdited.connect(self.handle_user_typing)
        self.url_bar.focusInEvent = self.url_bar_focused
        self.url_bar.setPlaceholderText("Search or enter address")
        self.url_bar.setClearButtonEnabled(True)
        self.url_bar.setMinimumWidth(400)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setStyleSheet("""
            QLineEdit {
                border: none;
                background: transparent;
                font-size: 14px;
                padding: 4px 0;
                selection-background-color: #e2e6ea;
            }
            QLineEdit:focus {
                outline: none;
            }
        """)
        url_bar_layout.addWidget(self.url_bar, 1)

        # Loading progress indicator
        self.loading_progress = QtWidgets.QProgressBar()
        self.loading_progress.setFixedHeight(2)
        self.loading_progress.setStyleSheet("""
            QProgressBar {
                background: transparent;
                border: none;
                border-radius: 1px;
            }
            QProgressBar::chunk {
                background: #0078d4;
                border-radius: 1px;
            }
        """)
        self.loading_progress.setVisible(False)
        self.loading_progress.setRange(0, 100)
        self.loading_progress.setValue(0)

        # Container for URL bar and progress
        url_container = QtWidgets.QWidget()
        url_container_layout = QtWidgets.QVBoxLayout(url_container)
        url_container_layout.setContentsMargins(0, 0, 0, 0)
        url_container_layout.setSpacing(0)
        url_container_layout.addWidget(self.url_bar_container)
        url_container_layout.addWidget(self.loading_progress)

        self.navigation_bar.addWidget(url_container)

        # Visual styling with modern design
        self.navigation_bar.setStyleSheet("""
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 240), stop:1 rgba(248, 249, 250, 240));
                border-bottom: 1px solid #dee2e6;
                padding: 8px 16px;
                spacing: 4px;
            }
            QToolButton {
                padding: 8px;
                background: rgba(255, 255, 255, 0.7);
                border: 1px solid rgba(222, 226, 230, 0.5);
                border-radius: 8px;
                font-weight: 500;
            }
            QToolButton:hover {
                background: rgba(255, 255, 255, 0.9);
                border-color: #adb5bd;
            }
            QToolButton:pressed {
                background: #dee2e6;
            }
            QToolButton[checked="true"] {
                background: #0078d4;
                color: white;
                border-color: #005a9e;
            }
            QToolButton[checked="true"]:hover {
                background: #005a9e;
            }
        """)

        # Apply modern theme to completer popup
        theme = DesignSystem.get_theme()
        self.completer.popup().setStyleSheet(f"""
            QListView {{
                background: {theme['surface_elevated']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                padding: 4px;
                font: {self.url_bar.font().toString()};
                color: {theme['text_primary']};
            }}
            QListView::item {{
                padding: 10px 16px;
                margin: 2px 0;
                border-radius: 6px;
            }}
            QListView::item:hover {{
                background: {theme['surface_variant']};
            }}
            QListView::item:selected {{
                background: {theme['accent']};
                color: white;
                border-radius: 6px;
            }}
        """)
    
        self.completer = QCompleter(self.url_bar)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.setModel(self.completer_model)
        self.url_bar.setCompleter(self.completer)
        self.url_bar.textChanged.connect(self.handle_text_changes)
    
    def create_status_bar(self):
        """Create a modern status bar with page information."""
        theme = DesignSystem.get_theme()
        
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background: {theme['statusbar_bg']};
                border-top: 1px solid {theme['border']};
                padding: 6px 16px;
                font-size: 12px;
            }}
            QLabel {{
                color: {theme['text_secondary']};
                padding: 2px 8px;
            }}
        """)
        
        # Page info label
        self.page_info_label = QtWidgets.QLabel("Ready")
        self.page_info_label.setStyleSheet(f"color: {theme['text_secondary']}; font-weight: 500;")
        self.status_bar.addWidget(self.page_info_label)
        
        # Zoom controls
        zoom_layout = QtWidgets.QHBoxLayout()
        zoom_layout.setSpacing(6)
        
        self.zoom_out_btn = QtWidgets.QPushButton("-")
        self.zoom_out_btn.setFixedSize(28, 28)
        self.zoom_out_btn.setStyleSheet(f"""
            QPushButton {{
                background: {theme['surface_variant']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                font-weight: bold;
                color: {theme['text_primary']};
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {theme['surface']};
                border-color: {theme['accent']};
            }}
            QPushButton:pressed {{
                background: {theme['accent']};
                color: white;
            }}
        """)
        self.zoom_out_btn.clicked.connect(lambda: self.zoom_page(-0.1))
        
        self.zoom_level_label = QtWidgets.QLabel("100%")
        self.zoom_level_label.setStyleSheet(f"color: {theme['text_primary']}; font-weight: 600; min-width: 48px; font-size: 13px;")
        self.zoom_level_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        self.zoom_in_btn = QtWidgets.QPushButton("+")
        self.zoom_in_btn.setFixedSize(28, 28)
        self.zoom_in_btn.setStyleSheet(f"""
            QPushButton {{
                background: {theme['surface_variant']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                font-weight: bold;
                color: {theme['text_primary']};
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {theme['surface']};
                border-color: {theme['accent']};
            }}
            QPushButton:pressed {{
                background: {theme['accent']};
                color: white;
            }}
        """)
        self.zoom_in_btn.clicked.connect(lambda: self.zoom_page(0.1))
        
        zoom_layout.addWidget(self.zoom_out_btn)
        zoom_layout.addWidget(self.zoom_level_label)
        zoom_layout.addWidget(self.zoom_in_btn)
        
        zoom_widget = QtWidgets.QWidget()
        zoom_widget.setLayout(zoom_layout)
        self.status_bar.addPermanentWidget(zoom_widget)
        
        # Update initial zoom level
        self.update_zoom_display()
    
    def refresh_status_bar_theme(self):
        """Refresh status bar theme when system theme changes."""
        theme = DesignSystem.get_theme()
        
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background: {theme['statusbar_bg']};
                border-top: 1px solid {theme['border']};
                padding: 6px 16px;
                font-size: 12px;
            }}
            QLabel {{
                color: {theme['text_secondary']};
                padding: 2px 8px;
            }}
        """)
        
        self.page_info_label.setStyleSheet(f"color: {theme['text_secondary']}; font-weight: 500;")
        self.zoom_level_label.setStyleSheet(f"color: {theme['text_primary']}; font-weight: 600; min-width: 48px; font-size: 13px;")
        
        zoom_btn_style = f"""
            QPushButton {{
                background: {theme['surface_variant']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                font-weight: bold;
                color: {theme['text_primary']};
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {theme['surface']};
                border-color: {theme['accent']};
            }}
            QPushButton:pressed {{
                background: {theme['accent']};
                color: white;
            }}
        """
        
        self.zoom_out_btn.setStyleSheet(zoom_btn_style)
        self.zoom_in_btn.setStyleSheet(zoom_btn_style)
    
    def update_zoom_display(self):
        """Update the zoom level display in status bar."""
        try:
            current_tab = self.tabs.currentWidget()
            if isinstance(current_tab, BrowserTab):
                zoom_factor = current_tab.zoomFactor()
                zoom_percent = int(zoom_factor * 100)
                self.zoom_level_label.setText(f"{zoom_percent}%")
        except:
            self.zoom_level_label.setText("100%")
    
    def zoom_page(self, factor):
        """Zoom the current page by the given factor."""
        try:
            current_tab = self.tabs.currentWidget()
            if isinstance(current_tab, BrowserTab):
                current_zoom = current_tab.zoomFactor()
                new_zoom = max(0.25, min(5.0, current_zoom + factor))  # Limit zoom between 25% and 500%
                current_tab.setZoomFactor(new_zoom)
                self.update_zoom_display()
        except Exception as e:
            print(f"Zoom error: {e}")
    
    def update_page_info(self, message):
        """Update the page information in status bar."""
        self.page_info_label.setText(message)
    
    def handle_user_typing(self):
        if not self.suppress_autocomplete:
            self.start_search_timer()
    
    def start_search_timer(self):
        if self.suppress_autocomplete:
            return

    def url_bar_focused(self, event):
        QtWidgets.QLineEdit.focusInEvent(self.url_bar, event)
        # Don't automatically show completer on focus - only when user types
    
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
        self.fullscreen_shortcut = QtGui.QShortcut(QtGui.QKeySequence("F11"), self)
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
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
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
        dialog.exec()
    
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
        self.update_security_indicator(q)

    def update_security_indicator(self, url):
        """Update the security indicator based on URL scheme and security."""
        if isinstance(url, str):
            url = QUrl(url)

        if url.scheme() == 'https':
            self.security_indicator.setText("🔒")
            self.security_indicator.setToolTip("Secure connection (HTTPS)")
            self.security_indicator.setStyleSheet("color: #28a745;")
        elif url.scheme() == 'http':
            self.security_indicator.setText("⚠️")
            self.security_indicator.setToolTip("Insecure connection (HTTP)")
            self.security_indicator.setStyleSheet("color: #ffc107;")
        else:
            self.security_indicator.setText("ℹ️")
            self.security_indicator.setToolTip("Local or special page")
            self.security_indicator.setStyleSheet("color: #6c757d;")

    def show_loading_progress(self, progress):
        """Show loading progress in the URL bar."""
        if progress < 100:
            self.loading_progress.setVisible(True)
            self.loading_progress.setValue(progress)
        else:
            self.loading_progress.setVisible(False)
            self.loading_progress.setValue(0)

    def go_back(self):
        """Go back in the history of the current tab."""
        if self.tabs.count() > 0:
            self.tabs.currentWidget().back()

    def go_home(self):
        """Navigate to the home page."""
        if self.tabs.count() > 0:
            self.tabs.currentWidget().setUrl(QUrl("https://www.google.com"))

    def reload_page(self):
        """Reload the current page in the active tab."""
        if self.tabs.count() > 0:
            self.tabs.currentWidget().reload()

    def reset_zoom(self):
        """Reset zoom to 100%."""
        try:
            current_tab = self.tabs.currentWidget()
            if isinstance(current_tab, BrowserTab):
                current_tab.setZoomFactor(1.0)
                self.update_zoom_display()
        except Exception as e:
            print(f"Reset zoom error: {e}")

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
                
            self.history.append({
                'url': url,
                'title': title,
                'timestamp': datetime.now().isoformat()
            })
            self.history = self.history[-500:]  # keep only last 500 entries
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
        if event.key() == QtCore.Qt.Key.Key_Escape and self.is_fullscreen:
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
                tab.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.DefaultContextMenu if enabled else QtCore.Qt.ContextMenuPolicy.NoContextMenu)
    
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
    sys.exit(app.exec())