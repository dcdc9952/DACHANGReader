# 大昌阅读器 - DaChang Reader
# A modern, colorful ebook reader with beautiful rounded UI

import sys
import os
import re
import math
import sqlite3
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QListWidget,
    QListWidgetItem, QLineEdit, QSlider, QScrollArea, QFrame,
    QToolBar, QStatusBar, QMenuBar, QMenu, QAction, QDialog,
    QProgressBar, QComboBox, QFontComboBox, QColorDialog, QSplitter,
    QScrollBar, QGraphicsDropShadowEffect, QSizePolicy, QShortcut,
    QKeySequenceEdit, QMessageBox, QInputDialog, QToolButton, QStackedWidget
)
from PyQt5.QtCore import (
    Qt, QSize, QRect, QTimer, QPropertyAnimation, QEasingCurve,
    QSettings, QDir, QUrl, QFileInfo
)
from PyQt5.QtGui import (
    QColor, QPalette, QFont, QIcon, QKeySequence, QTextCursor,
    QTextCharFormat, QTextBlockFormat, QPixmap, QImage, QPainter,
    QLinearGradient, QGradient, QPen, QBrush, QScreen
)
# Qt WebEngine imports removed (requires separate installation)

# Try importing ebook libraries, gracefully handle if not available
TXT_MODE = True

# Books folder - default location for storing imported books
def get_books_folder():
    """Get the books folder path, create if not exists"""
    # Use same directory as exe or script for books storage
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    books_folder = os.path.join(base_dir, "books")
    if not os.path.exists(books_folder):
        try:
            os.makedirs(books_folder)
        except:
            books_folder = os.path.join(os.path.expanduser("~"), "Documents", "大昌阅读器书籍")
            if not os.path.exists(books_folder):
                os.makedirs(books_folder)
    return books_folder
try:
    import ebooklib
    from ebooklib import epub
    EPUB_AVAILABLE = True
except ImportError:
    EPUB_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


BOOKS_FOLDER = ""  # Will be set on first use

def get_default_books_folder():
    """Get the default books folder path"""
    global BOOKS_FOLDER
    if not BOOKS_FOLDER:
        BOOKS_FOLDER = get_books_folder()
    return BOOKS_FOLDER


def set_books_folder(path):
    """Set the books folder path"""
    global BOOKS_FOLDER
    BOOKS_FOLDER = path
    if not os.path.exists(path):
        os.makedirs(path)


def get_books_folder_setting():
    """Get current books folder, create if needed"""
    return get_default_books_folder()


class Book:
    """Represents a book in the library"""
    def __init__(self, filepath, title="", author="", format="txt", last_position=0, total_pages=1, added_date=None):
        self.filepath = filepath
        self.title = title or os.path.splitext(os.path.basename(filepath))[0]
        self.author = author or "未知作者"
        self.format = format.lower()
        self.last_position = last_position
        self.total_pages = total_pages
        self.added_date = added_date or datetime.now().isoformat()
        self.content = ""
        self.bookmarks = []
        self.annotations = []

    def to_dict(self):
        return {
            'filepath': self.filepath,
            'title': self.title,
            'author': self.author,
            'format': self.format,
            'last_position': self.last_position,
            'total_pages': self.total_pages,
            'added_date': self.added_date,
            'bookmarks': self.bookmarks,
            'annotations': self.annotations
        }

    @classmethod
    def from_dict(cls, d):
        book = cls(d['filepath'], d.get('title', ''), d.get('author', ''),
                   d.get('format', 'txt'), d.get('last_position', 0),
                   d.get('total_pages', 1), d.get('added_date'))
        book.bookmarks = d.get('bookmarks', [])
        book.annotations = d.get('annotations', [])
        return book


class RoundedButton(QPushButton):
    """Custom rounded button with colorful styling"""
    def __init__(self, text="", color="#5B8DEF", parent=None):
        super().__init__(text, parent)
        self.setColor(color)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(40)
        self.setFont(QFont("Microsoft YaHei", 10))
        
    def setColor(self, color):
        self.base_color = color
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 8px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(color, 20)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 10)};
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
            }}
        """)
        
    @staticmethod
    def lighten_color(hex_color, percent):
        rgb = QColor(hex_color).toRgb()
        r = min(255, rgb.red() + int((255 - rgb.red()) * percent / 100))
        g = min(255, rgb.green() + int((255 - rgb.green()) * percent / 100))
        b = min(255, rgb.blue() + int((255 - rgb.blue()) * percent / 100))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @staticmethod
    def darken_color(hex_color, percent):
        rgb = QColor(hex_color).toRgb()
        r = max(0, rgb.red() - int(rgb.red() * percent / 100))
        g = max(0, rgb.green() - int(rgb.green() * percent / 100))
        b = max(0, rgb.blue() - int(rgb.blue() * percent / 100))
        return f"#{r:02x}{g:02x}{b:02x}"


class ColorfulIconButton(QPushButton):
    """Icon button with subtle color accent"""
    def __init__(self, icon_char="", color="#6C5CE7", parent=None):
        super().__init__(parent)
        self.icon_char = icon_char
        self.accent_color = color
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(44, 44)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 12px;
                color: #555;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {color}22;
                color: {color};
            }}
            QPushButton:pressed {{
                background-color: {color}44;
            }}
        """)


class BookCard(QWidget):
    """Book card widget for library view"""
    def __init__(self, book, parent=None):
        super().__init__(parent)
        self.book = book
        self.setup_ui()
        
    def setup_ui(self):
        colors = ["#5B8DEF", "#A29BFE", "#00CEC9", "#FD79A8", "#FDCB6E", "#6C5CE7", "#00B894", "#E17055"]
        self.card_color = colors[hash(self.book.title) % len(colors)]
        
        self.setFixedSize(200, 260)
        self.setCursor(Qt.PointingHandCursor)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Card frame
        self.card_frame = QFrame()
        self.card_frame.setFixedSize(200, 260)
        self.card_frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 16px;
                border: 1px solid #e0e0e0;
            }}
        """)
        
        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)
        
        # Color banner
        banner = QFrame()
        banner.setFixedHeight(100)
        banner.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.card_color},
                    stop:1 {RoundedButton.lighten_color(self.card_color, 30)});
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
            }}
        """)
        banner_layout = QVBoxLayout(banner)
        banner_layout.setContentsMargins(15, 10, 15, 10)
        
        # Format badge
        format_label = QLabel(self.book.format.upper())
        format_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255,255,255,200);
                color: #333;
                border-radius: 8px;
                padding: 2px 8px;
                font-size: 10px;
                font-weight: bold;
            }
        """)
        format_label.setFixedWidth(40)
        banner_layout.addWidget(format_label, 0, Qt.AlignLeft)
        
        # Book icon
        icon_label = QLabel("📖")
        icon_label.setStyleSheet("font-size: 40px; color: white;")
        icon_label.setAlignment(Qt.AlignCenter)
        banner_layout.addWidget(icon_label)
        
        card_layout.addWidget(banner)
        
        # Info section
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(12, 12, 12, 12)
        info_layout.setSpacing(5)
        
        title_label = QLabel(self.book.title)
        title_label.setStyleSheet("color: #333; font-size: 14px; font-weight: bold;")
        title_label.setWordWrap(True)
        title_label.setFixedHeight(40)
        info_layout.addWidget(title_label)
        
        author_label = QLabel(self.book.author)
        author_label.setStyleSheet("color: #888; font-size: 12px;")
        info_layout.addWidget(author_label)
        
        # Progress
        progress = self.book.last_position / max(1, self.book.total_pages)
        progress_label = QLabel(f"阅读进度: {int(progress*100)}%")
        progress_label.setStyleSheet("color: #aaa; font-size: 11px;")
        info_layout.addWidget(progress_label)
        
        progress_bar = QProgressBar()
        progress_bar.setFixedHeight(4)
        progress_bar.setTextVisible(False)
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #eee;
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {self.card_color};
                border-radius: 2px;
            }}
        """)
        progress_bar.setValue(int(progress * 100))
        info_layout.addWidget(progress_bar)
        
        card_layout.addWidget(info_widget)
        
        layout.addWidget(self.card_frame)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.card_frame.setGraphicsEffect(shadow)
        
        self.setAttribute(Qt.WA_Hover)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.card_frame.move(2, 2)
            self.card_frame.setStyleSheet(self.card_frame.styleSheet().replace("border: 1px solid #e0e0e0;", "border: 2px solid " + self.card_color + ";"))
    
    def mouseReleaseEvent(self, event):
        self.card_frame.move(0, 0)
        self.card_frame.setStyleSheet(self.card_frame.styleSheet().replace("border: 2px solid " + self.card_color + ";", "border: 1px solid #e0e0e0;"))


class ColorfulSlider(QSlider):
    """Colorful slider for settings"""
    def __init__(self, color="#5B8DEF", orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.slider_color = color
        self.setStyleSheet(f"""
            QSlider {{
                background: transparent;
            }}
            QSlider::groove:horizontal {{
                border: none;
                height: 6px;
                background: #e0e0e0;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {color};
                width: 20px;
                height: 20px;
                margin: -7px 0;
                border-radius: 10px;
            }}
            QSlider::sub-page:horizontal {{
                background: {color};
                border-radius: 3px;
            }}
        """)


class ReadingView(QFrame):
    """Main reading area with page turning"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_book = None
        self.current_page = 0
        self.total_pages = 1
        self.font_size = 18
        self.line_height = 1.8
        self.bg_color = QColor(255, 248, 240)  # Warm paper
        self.text_color = QColor(50, 50, 50)
        self.setup_ui()
        
    def setup_ui(self):
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet("background-color: #FFF8F0;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Scroll area for content
        self.scroll_area = QScrollArea()
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #FFF8F0;
                border: none;
            }
            QScrollBar:vertical {
                background: #e0d5c8;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #b0a090;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Text content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(60, 40, 60, 40)
        self.content_layout.setSpacing(int(self.font_size * self.line_height))
        
        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setTextFormat(Qt.RichText)
        self.content_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.update_text_style()
        
        self.content_layout.addWidget(self.content_label)
        
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)
        
        # Page navigation buttons
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(20, 10, 20, 10)
        
        self.prev_btn = RoundedButton("◀ 上一页", "#6C5CE7")
        self.prev_btn.setFixedWidth(120)
        self.prev_btn.clicked.connect(self.prev_page)
        
        self.next_btn = RoundedButton("下一页 ▶", "#5B8DEF")
        self.next_btn.setFixedWidth(120)
        self.next_btn.clicked.connect(self.next_page)
        
        self.page_label = QLabel("第 1 / 1 页")
        self.page_label.setStyleSheet("color: #888; font-size: 14px;")
        self.page_label.setAlignment(Qt.AlignCenter)
        
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.page_label)
        nav_layout.addWidget(self.next_btn)
        
        layout.addLayout(nav_layout)
        
    def update_text_style(self):
        self.content_label.setStyleSheet(f"""
            QLabel {{
                color: #{self.text_color.name()[1:]};
                font-size: {self.font_size}px;
                line-height: {self.line_height};
                font-family: 'Microsoft YaHei', 'SimSun', serif;
            }}
        """)
        
    def load_book(self, book):
        self.current_book = book
        self.current_page = book.last_position
        self.total_pages = book.total_pages if book.total_pages > 0 else 1
        self.update_page()
        
    def update_page(self):
        if not self.current_book:
            return
        
        content = self.current_book.content
        if not content:
            self.content_label.setText("<p style='text-align:center;color:#aaa;'>空书籍或无法加载内容</p>")
            return
        
        # Split content into pages
        pages = self.split_into_pages(content)
        self.total_pages = len(pages)
        
        if 0 <= self.current_page < len(pages):
            self.content_label.setText(pages[self.current_page])
        else:
            self.current_page = 0
            if pages:
                self.content_label.setText(pages[0])
        
        self.page_label.setText(f"第 {self.current_page + 1} / {self.total_pages} 页")
        self.scroll_area.verticalScrollBar().setValue(0)
        
    def split_into_pages(self, content):
        """Split content into pages based on visible height"""
        pages = []
        chars_per_page = 2000  # Approximate
        
        lines = content.split('\n')
        current_page = []
        current_chars = 0
        
        for line in lines:
            line_chars = len(line)
            if current_chars + line_chars > chars_per_page:
                if current_page:
                    pages.append('<br>'.join(current_page))
                    current_page = []
                    current_chars = 0
            current_page.append(line)
            current_chars += line_chars + 1
        
        if current_page:
            pages.append('<br>'.join(current_page))
        
        return pages if pages else [content]
    
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_page()
            if self.current_book:
                self.current_book.last_position = self.current_page
    
    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_page()
            if self.current_book:
                self.current_book.last_position = self.current_page
    
    def set_font_size(self, size):
        self.font_size = size
        self.update_text_style()
        self.update_page()
    
    def set_line_height(self, height):
        self.line_height = height
        self.update_text_style()
        self.update_page()
    
    def set_theme(self, theme):
        themes = {
            'day': {'bg': '#FFF8F0', 'text': '#323232'},
            'sepia': {'bg': '#F4ECD8', 'text': '#5B4636'},
            'night': {'bg': '#1A1A2E', 'text': '#E0E0E0'},
            'forest': {'bg': '#E8F5E9', 'text': '#2E4A2E'},
        }
        if theme in themes:
            self.bg_color = QColor(themes[theme]['bg'])
            self.text_color = QColor(themes[theme]['text'])
            self.setStyleSheet(f"background-color: {themes[theme]['bg']};")
            self.scroll_area.setStyleSheet(f"""
                QScrollArea {{
                    background-color: {themes[theme]['bg']};
                    border: none;
                }}
                QScrollBar:vertical {{
                    background: #e0d5c8;
                    width: 10px;
                    border-radius: 5px;
                }}
                QScrollBar::handle:vertical {{
                    background: #b0a090;
                    border-radius: 5px;
                    min-height: 30px;
                }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    height: 0px;
                }}
            """)
            self.update_text_style()
            self.update_page()


class SettingsDialog(QDialog):
    """Settings dialog with colorful design"""
    def __init__(self, parent=None, reading_view=None):
        super().__init__(parent)
        self.reading_view = reading_view
        self.setWindowTitle("设置")
        self.setFixedSize(500, 450)
        self.setStyleSheet("background-color: #f8f9fa;")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("阅读设置")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        
        # Font size
        font_group = self.create_group("字体大小")
        font_layout = QHBoxLayout()
        self.font_slider = ColorfulSlider("#5B8DEF")
        self.font_slider.setMinimum(14)
        self.font_slider.setMaximum(32)
        self.font_slider.setValue(self.reading_view.font_size if self.reading_view else 18)
        self.font_slider.valueChanged.connect(self.on_font_size_changed)
        self.font_label = QLabel(f"{self.font_slider.value()} px")
        self.font_label.setStyleSheet("color: #666; min-width: 50px;")
        font_layout.addWidget(self.font_slider)
        font_layout.addWidget(self.font_label)
        font_group.layout().addLayout(font_layout)
        layout.addWidget(font_group)
        
        # Line height
        line_group = self.create_group("行间距")
        line_layout = QHBoxLayout()
        self.line_slider = ColorfulSlider("#A29BFE")
        self.line_slider.setMinimum(10)
        self.line_slider.setMaximum(30)
        self.line_slider.setValue(int(self.reading_view.line_height * 10 if self.reading_view else 18))
        self.line_slider.valueChanged.connect(self.on_line_height_changed)
        self.line_label = QLabel(f"{self.line_slider.value()/10:.1f}")
        self.line_label.setStyleSheet("color: #666; min-width: 50px;")
        line_layout.addWidget(self.line_slider)
        line_layout.addWidget(self.line_label)
        line_group.layout().addLayout(line_layout)
        layout.addWidget(line_group)
        
        # Theme
        theme_group = self.create_group("阅读主题")
        theme_layout = QHBoxLayout()
        themes = [("日光", "day"), ("羊皮纸", "sepia"), ("夜间", "night"), ("护眼", "forest")]
        for name, theme in themes:
            btn = RoundedButton(name, self.get_theme_color(theme))
            btn.setFixedWidth(80)
            btn.clicked.connect(lambda checked, t=theme: self.set_theme(t))
            theme_layout.addWidget(btn)
        theme_group.layout().addLayout(theme_layout)
        layout.addWidget(theme_group)
        
        layout.addStretch()
        
        # Close button
        close_btn = RoundedButton("关闭", "#6C5CE7")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
    def create_group(self, title):
        group = QFrame()
        group.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        label = QLabel(title)
        label.setStyleSheet("font-weight: bold; color: #333; font-size: 14px;")
        layout.addWidget(label)
        
        return group
    
    def get_theme_color(self, theme):
        colors = {'day': '#5B8DEF', 'sepia': '#FDCB6E', 'night': '#6C5CE7', 'forest': '#00B894'}
        return colors.get(theme, '#5B8DEF')
    
    def on_font_size_changed(self, value):
        self.font_label.setText(f"{value} px")
        if self.reading_view:
            self.reading_view.set_font_size(value)
    
    def on_line_height_changed(self, value):
        self.line_label.setText(f"{value/10:.1f}")
        if self.reading_view:
            self.reading_view.set_line_height(value/10)
    
    def set_theme(self, theme):
        if self.reading_view:
            self.reading_view.set_theme(theme)


class AboutDialog(QDialog):
    """About dialog"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于")
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #f8f9fa;")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.addAlignment(Qt.AlignCenter)
        
        # Icon
        icon_label = QLabel("📚")
        icon_label.setStyleSheet("font-size: 60px;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Title
        title = QLabel("大昌阅读器")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #333;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Version
        version = QLabel("版本 1.0.0")
        version.setStyleSheet("color: #888; font-size: 14px;")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)
        
        # Description
        desc = QLabel("一款简洁美观的电子书阅读器\n支持 TXT、EPUB、PDF 等格式")
        desc.setStyleSheet("color: #666; font-size: 13px; line-height: 1.8;")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)
        
        layout.addStretch()
        
        # Close button
        close_btn = RoundedButton("关闭", "#5B8DEF")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)


class LibraryWidget(QWidget):
    """Book library grid view"""
    book_selected = None
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.books = []
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header = QHBoxLayout()
        
        title = QLabel("📚 我的书库")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        header.addWidget(title)
        
        header.addStretch()
        
        # Import button
        import_btn = RoundedButton("+ 导入书籍", "#00B894")
        import_btn.setFixedWidth(120)
        import_btn.clicked.connect(self.parent().import_book)
        header.addWidget(import_btn)
        
        layout.addLayout(header)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索书名或作者...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                padding: 10px 15px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #5B8DEF;
            }
        """)
        self.search_input.textChanged.connect(self.filter_books)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Books grid scroll area
        scroll = QScrollArea()
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:horizontal {
                height: 0px;
            }
        """)
        
        self.books_container = QWidget()
        self.books_grid = QVBoxLayout(self.books_container)
        self.books_grid.setContentsMargins(0, 0, 0, 0)
        self.books_grid.setSpacing(20)
        self.books_grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        scroll.setWidget(self.books_container)
        layout.addWidget(scroll)
        
    def add_book_card(self, book):
        card = BookCard(book)
        card.mousePressEvent = lambda e: self.select_book(book, card)
        self.books.append((book, card))
        self.update_grid()
    
    def select_book(self, book, card):
        if self.book_selected:
            self.book_selected.setStyleSheet(self.book_selected.styleSheet().replace("border: 2px solid #5B8DEF;", "border: 1px solid #e0e0e0;"))
        card.setStyleSheet(card.styleSheet().replace("border: 1px solid #e0e0e0;", "border: 2px solid #5B8DEF;"))
        self.book_selected = card
        if self.parent() and hasattr(self.parent(), 'open_book'):
            self.parent().open_book(book)
    
    def filter_books(self, text):
        for book, card in self.books:
            visible = text.lower() in book.title.lower() or text.lower() in book.author.lower()
            card.setVisible(visible)
    
    def update_grid(self):
        # Clear and re-add in rows of 4
        while self.books_grid.count():
            child = self.books_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        row = None
        for i, (book, card) in enumerate(self.books):
            if i % 4 == 0:
                row = QHBoxLayout()
                row.setSpacing(20)
                self.books_grid.addLayout(row)
            row.addWidget(card)
        
        # Add stretch if needed
        if row and row.count() < 4:
            row.addStretch()


class DaChangReader(QMainWindow):
    """Main application window"""
    def __init__(self):
        super().__init__()
        self.books = []
        self.current_book = None
        self.current_view = "library"  # "library" or "reading"
        self.settings = QSettings("DaChang", "Reader")
        self.setup_ui()
        self.load_settings()
        self.apply_stylesheet()
        self.load_library()
        
    def setup_ui(self):
        self.setWindowTitle("大昌阅读器")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Center window
        screen = QApplication.primaryScreen()
        if screen:
            rect = screen.availableGeometry()
            self.move((rect.width() - self.width()) // 2, (rect.height() - self.height()) // 2)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Content area
        self.content_stack = QStackedWidget()
        
        # Library view
        self.library_widget = LibraryWidget()
        self.library_widget.parent = lambda: self
        self.content_stack.addWidget(self.library_widget)
        
        # Reading view
        self.reading_view = ReadingView()
        content_frame = QFrame()
        content_frame.setLayout(QVBoxLayout())
        content_frame.layout().setContentsMargins(0, 0, 0, 0)
        content_frame.layout().addWidget(self.reading_view)
        self.content_stack.addWidget(content_frame)
        
        main_layout.addWidget(self.content_stack)
        
        # Status bar
        self.statusBar().showMessage("就绪")
        
        # Keyboard shortcuts
        self.setup_shortcuts()
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: white;
                border-bottom: 1px solid #e0e0e0;
                padding: 5px;
            }
            QMenuBar::item {
                padding: 5px 15px;
                border-radius: 5px;
            }
            QMenuBar::item:selected {
                background-color: #f0f0f0;
            }
            QMenu {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QMenu::item {
                padding: 8px 20px;
            }
            QMenu::item:selected {
                background-color: #5B8DEF22;
            }
        """)
        
        # File menu
        file_menu = menubar.addMenu("文件")
        import_action = QAction("导入书籍...", self)
        import_action.setShortcut("Ctrl+O")
        import_action.triggered.connect(self.import_book)
        file_menu.addAction(import_action)
        
        export_action = QAction("导出笔记...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_notes)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("视图")
        library_action = QAction("书库", self)
        library_action.setShortcut("Ctrl+L")
        library_action.triggered.connect(lambda: self.switch_view("library"))
        view_menu.addAction(library_action)
        
        fullscreen_action = QAction("全屏阅读", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("工具")
        settings_action = QAction("设置...", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.open_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("帮助")
        about_action = QAction("关于...", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        shortcuts_action = QAction("快捷键...", self)
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)
        
    def create_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setFixedHeight(60)
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: white;
                border-bottom: 1px solid #e0e0e0;
                spacing: 10px;
                padding: 5px 15px;
            }
        """)
        
        # Logo/Title
        logo_label = QLabel("📚 大昌阅读器")
        logo_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #5B8DEF; padding: 0 20px 0 0;")
        toolbar.addWidget(logo_label)
        
        toolbar.addSeparator()
        
        # Navigation buttons
        self.nav_library_btn = ColorfulIconButton("📚", "#5B8DEF")
        self.nav_library_btn.setToolTip("书库 (Ctrl+L)")
        self.nav_library_btn.clicked.connect(lambda: self.switch_view("library"))
        toolbar.addWidget(self.nav_library_btn)
        
        self.nav_reading_btn = ColorfulIconButton("📖", "#A29BFE")
        self.nav_reading_btn.setToolTip("阅读")
        self.nav_reading_btn.clicked.connect(lambda: self.switch_view("reading"))
        toolbar.addWidget(self.nav_reading_btn)
        
        toolbar.addSeparator()
        
        # Import button
        import_btn = QPushButton("📥 导入")
        import_btn.setStyleSheet("""
            QPushButton {
                background-color: #00B894;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #00CEC9; }
        """)
        import_btn.clicked.connect(self.import_book)
        toolbar.addWidget(import_btn)

        # Open books folder button
        open_folder_btn = QPushButton("📂 文件夹")
        open_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #00B894;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #00CEC9; }
        """)
        open_folder_btn.clicked.connect(self.open_books_folder)
        toolbar.addWidget(open_folder_btn)

        toolbar.addSeparator()

        # Settings button
        settings_btn = QPushButton("⚙️ 设置")
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C5CE7;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #A29BFE; }
        """)
        settings_btn.clicked.connect(self.open_settings)
        toolbar.addWidget(settings_btn)
        
        self.addToolBar(toolbar)
        
    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-right: 1px solid #e0e0e0;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(15)
        
        # Quick actions header
        quick_label = QLabel("快捷操作")
        quick_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #666;")
        layout.addWidget(quick_label)
        
        # Quick buttons
        import_btn = RoundedButton("📥 导入书籍", "#00B894")
        import_btn.clicked.connect(self.import_book)
        layout.addWidget(import_btn)
        
        recent_label = QLabel("最近阅读", sidebar)
        recent_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #666; margin-top: 10px;")
        layout.addWidget(recent_label)
        
        # Recent books list
        self.recent_list = QListWidget()
        self.recent_list.setStyleSheet("""
            QListWidget {
                border: none;
                background: transparent;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 8px;
                margin: 2px 0;
            }
            QListWidget::item:selected {
                background-color: #5B8DEF22;
            }
            QListWidget::item:hover {
                background-color: #f0f0f0;
            }
        """)
        self.recent_list.itemDoubleClicked.connect(lambda item: self.open_recent_book(item))
        layout.addWidget(self.recent_list)
        
        layout.addStretch()
        
        # Bottom info
        info_label = QLabel("大昌阅读器 v1.0\n简洁·美观·高效", sidebar)
        info_label.setStyleSheet("color: #aaa; font-size: 11px;")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        return sidebar
    
    def apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
        """)
        
    def setup_shortcuts(self):
        shortcuts = [
            ("Ctrl+O", self.import_book),
            ("Ctrl+L", lambda: self.switch_view("library")),
            ("Left", self.reading_view.prev_page),
            ("Right", self.reading_view.next_page),
            ("Escape", self.exit_fullscreen),
            ("F11", self.toggle_fullscreen),
        ]
        for key, action in shortcuts:
            QShortcut(QKeySequence(key), self).activated.connect(action)
            
    def load_settings(self):
        self.resize(self.settings.value("window_size", QSize(1400, 900)))
        self.move(self.settings.value("window_pos", QApplication.primaryScreen().availableGeometry().center() - self.rect().center()))
        
    def save_settings(self):
        self.settings.setValue("window_size", self.size())
        self.settings.setValue("window_pos", self.pos())
        
    def closeEvent(self, event):
        self.save_settings()
        self.save_library()
        event.accept()

    def open_books_folder(self):
        """Open the books folder in file explorer"""
        folder = get_books_folder_setting()
        if os.path.exists(folder):
            import subprocess
            try:
                if sys.platform == 'win32':
                    os.startfile(folder)
                else:
                    subprocess.run(['xdg-open', folder])
            except:
                QMessageBox.information(self, "书籍文件夹", f"书籍文件夹位置:\n{folder}")
        else:
            QMessageBox.information(self, "书籍文件夹", f"书籍文件夹位置:\n{folder}\n\n文件夹不存在，将自动创建。")

    def import_book(self):
        filters = "电子书 (*.txt *.epub *.pdf);;TXT文件 (*.txt);;EPUB文件 (*.epub);;PDF文件 (*.pdf);;所有文件 (*.*)"
        default_dir = get_books_folder_setting()
        files, _ = QFileDialog.getOpenFileNames(self, "导入书籍", default_dir, filters)
        
        for filepath in files:
            book = self.load_book(filepath)
            if book:
                self.books.append(book)
                self.library_widget.add_book_card(book)
                self.add_to_recent(book)
                self.statusBar().showMessage(f"已导入: {book.title}", 3000)
        
        if files and not self.books:
            QMessageBox.warning(self, "提示", "未能加载任何书籍。\n请确保已安装必要的库:\n  pip install ebooklib PyMuPDF")
            
    def load_book(self, filepath):
        """Load a book from file path"""
        ext = os.path.splitext(filepath)[1].lower()
        
        try:
            if ext == '.txt':
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                book = Book(filepath, format='txt')
                book.content = content
                # Estimate pages
                book.total_pages = max(1, len(content) // 2000)
                
            elif ext == '.epub' and EPUB_AVAILABLE:
                book = self.load_epub(filepath)
                
            elif ext == '.pdf' and PDF_AVAILABLE:
                book = self.load_pdf(filepath)
                
            else:
                # Fallback to text
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                book = Book(filepath, format=ext[1:] if ext else 'txt')
                book.content = content
                book.total_pages = max(1, len(content) // 2000)
                
            return book
            
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return None
            
    def load_epub(self, filepath):
        """Load EPUB file"""
        try:
            book_epub = epub.read_epub(filepath)
            title = book_epub.get_metadata('DC', 'title')
            if title:
                title = title[0] if isinstance(title, list) else str(title)
            else:
                title = os.path.splitext(os.path.basename(filepath))[0]
                
            author = book_epub.get_metadata('DC', 'creator')
            if author:
                author = author[0] if isinstance(author, list) else str(author)
            else:
                author = "未知作者"
                
            content = ""
            for item in book_epub.get_items():
                if item.get_type() == 9:  # HTML content
                    content += item.get_content().decode('utf-8', errors='ignore')
            
            # Strip HTML tags
            content = re.sub(r'<[^>]+>', '', content)
            content = re.sub(r'\s+', ' ', content)
            
            book = Book(filepath, title, author, 'epub')
            book.content = content
            book.total_pages = max(1, len(content) // 2000)
            return book
        except Exception as e:
            print(f"EPUB error: {e}")
            return Book(filepath, format='epub')
            
    def load_pdf(self, filepath):
        """Load PDF file"""
        try:
            doc = fitz.open(filepath)
            content = ""
            for page in doc:
                content += page.get_text() + "\n\n"
            doc.close()
            
            book = Book(filepath, format='pdf')
            book.content = content
            book.total_pages = max(1, len(content) // 2000)
            return book
        except Exception as e:
            print(f"PDF error: {e}")
            return Book(filepath, format='pdf')
            
    def open_book(self, book):
        """Open a book for reading"""
        self.current_book = book
        self.reading_view.load_book(book)
        self.switch_view("reading")
        self.statusBar().showMessage(f"正在阅读: {book.title}", 3000)
        
    def open_recent_book(self, item):
        """Open a book from recent list"""
        for book in self.books:
            if item.text().startswith(book.title):
                self.open_book(book)
                break
                
    def add_to_recent(self, book):
        """Add book to recent list"""
        self.recent_list.insertItem(0, f"📖 {book.title}")
        if self.recent_list.count() > 10:
            self.recent_list.takeItem(10)
            
    def switch_view(self, view):
        """Switch between library and reading view"""
        if view == "library":
            self.content_stack.setCurrentIndex(0)
            self.nav_library_btn.setStyleSheet("""
                QPushButton {
                    background-color: #5B8DEF22;
                    border: 2px solid #5B8DEF;
                    border-radius: 12px;
                }
            """)
            self.nav_reading_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 12px;
                }
                QPushButton:hover {
                    background-color: #A29BFE22;
                }
            """)
        else:
            if self.current_book:
                self.content_stack.setCurrentIndex(1)
                self.nav_reading_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #A29BFE22;
                        border: 2px solid #A29BFE;
                        border-radius: 12px;
                    }
                """)
                self.nav_library_btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;
                        border-radius: 12px;
                    }
                    QPushButton:hover {
                        background-color: #5B8DEF22;
                    }
                """)
                
    def export_notes(self):
        """Export book notes"""
        if not self.current_book:
            QMessageBox.information(self, "提示", "请先打开一本书")
            return
        QMessageBox.information(self, "提示", "笔记导出功能开发中...")
        
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
            
    def exit_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            
    def open_settings(self):
        dialog = SettingsDialog(self, self.reading_view)
        dialog.exec_()
        
    def show_about(self):
        dialog = AboutDialog(self)
        dialog.exec_()
        
    def show_shortcuts(self):
        shortcuts_text = """
        <h3>键盘快捷键</h3>
        <table>
        <tr><td><b>Ctrl + O</b></td><td>导入书籍</td></tr>
        <tr><td><b>Ctrl + L</b></td><td>返回书库</td></tr>
        <tr><td><b>← 左方向键</b></td><td>上一页</td></tr>
        <tr><td><b>→ 右方向键</b></td><td>下一页</td></tr>
        <tr><td><b>F11</b></td><td>全屏阅读</td></tr>
        <tr><td><b>Esc</b></td><td>退出全屏</td></tr>
        </table>
        """
        QMessageBox.information(self, "快捷键", shortcuts_text)
        
    def save_library(self):
        """Save library to file"""
        try:
            import json
            library_file = os.path.join(QDir.homePath(), ".dachang_reader_library.json")
            data = [book.to_dict() for book in self.books]
            with open(library_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving library: {e}")
            
    def load_library(self):
        """Load library from file"""
        try:
            import json
            library_file = os.path.join(QDir.homePath(), ".dachang_reader_library.json")
            if os.path.exists(library_file):
                with open(library_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for item in data:
                    book = Book.from_dict(item)
                    # Try to reload content
                    if os.path.exists(book.filepath):
                        loaded = self.load_book(book.filepath)
                        if loaded:
                            book.content = loaded.content
                            book.total_pages = loaded.total_pages
                        self.books.append(book)
                        self.library_widget.add_book_card(book)
                        self.add_to_recent(book)
        except Exception as e:
            print(f"Error loading library: {e}")


def main():
    app = QApplication(sys.argv)
    
    # Set application-wide font
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    
    # Set application style
    app.setStyle("Fusion")
    
    window = DaChangReader()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()