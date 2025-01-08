import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QTabWidget, QToolBar, QLabel, QMenu, QAction, QDialog, QVBoxLayout, QTextEdit, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile
from PyQt5.QtCore import QUrl, Qt, pyqtSignal, pyqtSlot
from pytube import YouTube
from pytube.exceptions import VideoUnavailable
from PyQt5.QtWidgets import QCompleter
from datetime import datetime
from PyQt5.QtWidgets import QMenu, QAction
from instaloader import Instaloader, Post
from facebook_scraper import get_posts
import requests
import os
import nltk
from textblob import TextBlob
from PyQt5.QtWidgets import QMessageBox
import nltk
from textblob import TextBlob
from PyQt5.QtWidgets import QMessageBox, QCompleter, QMenu, QAction
from instaloader import Instaloader, Post
from facebook_scraper import get_posts
import requests
import os
from PyQt5.QtWidgets import QMenu, QAction

# Download NLTK data
nltk.download('vader_lexicon')
class AdBlocker(QWebEnginePage):
    link_hovered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWebChannel(None)
        self.ad_domains = self.load_ad_domains()

    def load_ad_domains(self):
        return [
            "doubleclick.net",
            "googlesyndication.com",
            "googleadservices.com",
            "google-analytics.com",
            "adsafeprotected.com",
            "adnxs.com",
            "adsrvr.org",
            "adtech.de",
            "advertising.com",
            "atdmt.com",
            "exelator.com",
            "eyeota.net",
            "lijit.com",
            "media.net",
            "openx.net",
            "pubmatic.com",
            "quantserve.com",
            "scorecardresearch.com",
            "serving-sys.com",
            "taboola.com",
            "zedo.com"
        ]

    def acceptNavigationRequest(self, url, navType, isMainFrame):
        if self.is_ad_url(url):
            return False
        return super().acceptNavigationRequest(url, navType, isMainFrame)

    def is_ad_url(self, url):
        for domain in self.ad_domains:
            if domain in url.toString():
                return True
        return False

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        if message.startswith("hovered_link:"):
            link = message.split("hovered_link:", 1)[1]
            self.link_hovered.emit(link)
    
    def inject_youtube_ad_blocker(self):
        js_code = """
        // Function to remove YouTube ads
        function removeYouTubeAds() {
            var adSelectors = [
                '.video-ads', 
                '.ytp-ad-module', 
                '.ytp-ad-player-overlay',
                '.ytp-ad-overlay-container',
                '.ytp-ad-skip-button-slot',
                '.ytp-ad-skip-button-text',
                '.ytp-ad-image-overlay',
                '.ytp-ad-preview-container',
                '.ytp-ad-overlay-slot',
                '.ytp-ad-player-overlay-instream-info'
            ];
            adSelectors.forEach(function(selector) {
                var ads = document.querySelectorAll(selector);
                ads.forEach(function(ad) {
                    ad.style.display = 'none';
                });
            });
        }

        // Function to detect and handle anti-adblock messages
        function handleAntiAdblock() {
            const SELECTORS = [
                'ytd-watch-flexy:not([hidden]) ytd-enforcement-message-view-model > div.ytd-enforcement-message-view-model',
                'yt-playability-error-supported-renderers#error-screen ytd-enforcement-message-view-model',
                'tp-yt-paper-dialog .ytd-enforcement-message-view-model',
            ];

            function detectWall(cb) {
                let timeout = null;

                const observer = new MutationObserver(() => {
                    if (timeout) return;

                    timeout = setTimeout(() => {
                        if (document.querySelector(SELECTORS.join(','))?.clientHeight > 0) {
                            try {
                                cb();
                            } catch {
                                /* ignore */
                            }
                        } else {
                            timeout = null;
                        }
                    }, 1000);
                });

                document.addEventListener('yt-navigate-start', () => {
                    clearTimeout(timeout);
                    timeout = null;
                });

                observer.observe(document.body, {
                    childList: true,
                    subtree: true,
                    attributeFilter: ['src', 'style'],
                });
            }

            detectWall(() => {
                console.log('Anti-adblock message detected and removed');
                // Add your code to handle the detected anti-adblock message here
            });
        }

        // Create a MutationObserver to continuously remove ads and handle anti-adblock messages
        var observer = new MutationObserver(function(mutations) {
            removeYouTubeAds();
            handleAntiAdblock();
        });

        // Start observing the document for changes
        observer.observe(document, { childList: true, subtree: true });

        // Initial call to remove ads and handle anti-adblock messages
        removeYouTubeAds();
        handleAntiAdblock();
        """
        self.runJavaScript(js_code)

class DeveloperToolsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Developer Tools")
        self.setGeometry(100, 100, 600, 400)
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

    def update_info(self, info):
        self.text_edit.setPlainText(info)

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Web Browser")
        self.setGeometry(100, 100, 1200, 800)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.toolbar.addWidget(self.url_bar)

        # Initialize common URLs and completer
        self.common_urls = [
            "http://www.google.com",
            "http://www.youtube.com",
            "http://www.facebook.com",
            "http://www.twitter.com",
            "http://www.instagram.com",
            "http://www.duckduckgo.com",
            "http://www.reddit.com",
            "http://www.linkedin.com",
            "http://www.github.com"
        ]
        self.completer = QCompleter(self.common_urls)
        self.url_bar.setCompleter(self.completer)

        self.add_new_tab_btn = QPushButton("+")
        self.add_new_tab_btn.clicked.connect(self.add_new_tab)
        self.toolbar.addWidget(self.add_new_tab_btn)

        self.bookmark_btn = QPushButton("Bookmark")
        self.bookmark_btn.clicked.connect(self.add_bookmark)
        self.toolbar.addWidget(self.bookmark_btn)

        self.clear_history_btn = QPushButton("Clear History")
        self.clear_history_btn.clicked.connect(self.clear_history)
        self.toolbar.addWidget(self.clear_history_btn)

        self.clear_cache_btn = QPushButton("Clear Cache")
        self.clear_cache_btn.clicked.connect(self.clear_cache)
        self.toolbar.addWidget(self.clear_cache_btn)

        self.clear_cookies_btn = QPushButton("Clear Cookies")
        self.clear_cookies_btn.clicked.connect(self.clear_cookies)
        self.toolbar.addWidget(self.clear_cookies_btn)

        # Create a download menu
        self.download_menu = QMenu("Download", self)
        self.toolbar.addAction(self.download_menu.menuAction())

        # Add actions to the download menu
        download_pinterest_action = QAction("Download Pinterest Video", self)
        download_pinterest_action.triggered.connect(self.download_pinterest)
        self.download_menu.addAction(download_pinterest_action)

        download_linkedin_action = QAction("Download LinkedIn Video", self)
        download_linkedin_action.triggered.connect(self.download_linkedin)
        self.download_menu.addAction(download_linkedin_action)

        download_facebook_action = QAction("Download Facebook Video", self)
        download_facebook_action.triggered.connect(self.download_facebook)
        self.download_menu.addAction(download_facebook_action)

        download_instagram_action = QAction("Download Instagram Video", self)
        download_instagram_action.triggered.connect(self.download_instagram)
        self.download_menu.addAction(download_instagram_action)

        self.tab_widget.currentChanged.connect(self.update_url_bar)
        self.tab_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tab_widget.customContextMenuRequested.connect(self.show_tab_context_menu)

        self.bookmarks = []
        self.load_bookmarks()

        # Initialize basic and advanced analytics
        self.dev_tools_click_count = 0
        self.advanced_analytics = []

         # Initialize recently visited websites and recommendations
        self.recently_visited = []
        self.recommendations = []

        self.hover_label = QLabel("", self)
        self.hover_label.setStyleSheet("background-color: white; border: 1px solid black;")
        self.hover_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.hover_label.setFixedWidth(400)
        self.hover_label.setFixedHeight(20)
        self.hover_label.move(self.width() - self.hover_label.width(), self.height() - self.hover_label.height())
        self.hover_label.show()

        self.add_new_tab()

    def download_pinterest(self):
        url = self.url_bar.text()
        if "pinterest.com" in url:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    html_content = response.text
                    # Extract the video URL from the HTML content
                    video_url = self.extract_pinterest_video_url(html_content)
                    if video_url:
                        self.download_file(video_url, "pinterest_video.mp4")
                        print("Pinterest video downloaded successfully.")
                    else:
                        print("Unable to find video URL.")
                else:
                    print(f"Failed to retrieve Pinterest page: {response.status_code}")
            except Exception as e:
                print(f"Error downloading Pinterest video: {e}")

    def extract_pinterest_video_url(self, html_content):
        # Implement logic to extract video URL from Pinterest HTML content
        pass

    def download_linkedin(self):
        url = self.url_bar.text()
        if "linkedin.com" in url:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    html_content = response.text
                    # Extract the video URL from the HTML content
                    video_url = self.extract_linkedin_video_url(html_content)
                    if video_url:
                        self.download_file(video_url, "linkedin_video.mp4")
                        print("LinkedIn video downloaded successfully.")
                    else:
                        print("Unable to find video URL.")
                else:
                    print(f"Failed to retrieve LinkedIn page: {response.status_code}")
            except Exception as e:
                print(f"Error downloading LinkedIn video: {e}")

    def extract_linkedin_video_url(self, html_content):
        # Implement logic to extract video URL from LinkedIn HTML content
        pass

    def download_facebook(self):
        url = self.url_bar.text()
        if "facebook.com" in url:
            try:
                for post in get_posts(url, pages=1):
                    if 'video' in post:
                        video_url = post['video']
                        self.download_file(video_url, "facebook_video.mp4")
                        print("Facebook video downloaded successfully.")
                        break
            except Exception as e:
                print(f"Error downloading Facebook video: {e}")

    def download_instagram(self):
        url = self.url_bar.text()
        if "instagram.com" in url:
            try:
                loader = Instaloader()
                post = Post.from_shortcode(loader.context, url.split("/")[-2])
                video_url = post.video_url
                self.download_file(video_url, "instagram_video.mp4")
                print("Instagram video downloaded successfully.")
            except Exception as e:
                print(f"Error downloading Instagram video: {e}")

    def download_file(self, url, filename):
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Downloaded {filename} successfully.")
        else:
            print(f"Failed to download file: {response.status_code}")

    def show_tab_context_menu(self, point):
        tab_index = self.tab_widget.tabBar().tabAt(point)
        if tab_index != -1:
            context_menu = QMenu(self)
            close_tab_action = QAction("Close Tab", self)
            close_tab_action.triggered.connect(lambda: self.close_tab(tab_index))
            context_menu.addAction(close_tab_action)
            context_menu.exec_(self.tab_widget.mapToGlobal(point))
    def add_new_tab(self):
        new_browser = QWebEngineView()
        page = AdBlocker(new_browser)
        new_browser.setPage(page)
        new_browser.setUrl(QUrl("about:blank"))
        new_browser.urlChanged.connect(self.update_url_bar)
        new_browser.titleChanged.connect(self.update_tab_title)
        new_browser.setContextMenuPolicy(Qt.CustomContextMenu)
        new_browser.customContextMenuRequested.connect(self.show_context_menu)
        page.loadFinished.connect(self.inject_js)
        page.link_hovered.connect(self.update_hover_label)
        i = self.tab_widget.addTab(new_browser, "New Tab")
        self.tab_widget.setCurrentIndex(i)

        # Display home page content
        home_html = self.create_home_page()
        new_browser.setHtml(home_html)

    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
    def inject_js(self):
        js_code = """
        document.addEventListener('mouseover', function(event) {
            if (event.target.tagName === 'A') {
                console.log('hovered_link:' + event.target.href);
            } else {
                console.log('hovered_link:');
            }
        });
        """
        current_browser = self.tab_widget.currentWidget()
        current_browser.page().runJavaScript(js_code)
        current_browser.page().inject_youtube_ad_blocker()

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            if " " in url:  # Check if the input is a search query
                url = "https://duckduckgo.com/?q=" + url.replace(" ", "+")
            else:
                url = "http://" + url
        current_browser = self.tab_widget.currentWidget()
        current_browser.setUrl(QUrl(url))

        # Track recently visited websites
        if url not in self.recently_visited:
            self.recently_visited.append(url)
            if len(self.recently_visited) > 10:  # Keep only the last 10 visited websites
                self.recently_visited.pop(0)

        # Generate recommendations based on recently visited websites
        self.generate_recommendations()

        # Analyze the content of the article
        current_browser.page().toPlainText(self.analyze_article_content)

    def update_url_bar(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            self.url_bar.setText(current_browser.url().toString())

    def update_tab_title(self, title):
        current_index = self.tab_widget.currentIndex()
        self.tab_widget.setTabText(current_index, title)

    def generate_recommendations(self):
        self.recommendations = []  # Clear previous recommendations

        # Simple recommendation logic based on keywords
        for url in self.recently_visited:
            if "google" in url:
                self.recommendations.append("http://www.gmail.com")
            elif "youtube" in url:
                self.recommendations.append("http://www.vimeo.com")
            elif "facebook" in url:
                self.recommendations.append("http://www.instagram.com")
            # Add more recommendation rules as needed

        # Keep recommendations unique
        self.recommendations = list(set(self.recommendations))

    @pyqtSlot(str)
    def update_hover_label(self, link):
        self.hover_label.setText(link)

    def add_bookmark(self):
        current_browser = self.tab_widget.currentWidget()
        url = current_browser.url().toString()
        self.bookmarks.append(url)
        self.save_bookmarks()

    def save_bookmarks(self):
        with open("bookmarks.json", "w") as f:
            json.dump(self.bookmarks, f)

    def load_bookmarks(self):
        try:
            with open("bookmarks.json", "r") as f:
                self.bookmarks = json.load(f)
        except FileNotFoundError:
            self.bookmarks = []

    def clear_history(self):
        profile = QWebEngineProfile.defaultProfile()
        profile.clearHttpCache()
        profile.clearAllVisitedLinks()
        print("Browser history cleared.")

    def clear_cache(self):
        profile = QWebEngineProfile.defaultProfile()
        profile.clearHttpCache()
        print("Browser cache cleared.")

    def clear_cookies(self):
        profile = QWebEngineProfile.defaultProfile()
        profile.cookieStore().deleteAllCookies()
        print("Browser cookies cleared.")

    def download_video(self):
        current_browser = self.tab_widget.currentWidget()
        url = current_browser.url().toString()
        if "youtube.com/watch" in url:
            try:
                yt = YouTube(url)
                stream = yt.streams.get_highest_resolution()
                save_path = QFileDialog.getSaveFileName(self, "Save Video", "", "MP4 Files (*.mp4)")[0]
                if save_path:
                    stream.download(output_path=save_path.rsplit('/', 1)[0], filename=save_path.rsplit('/', 1)[1])
                    print("Video downloaded successfully.")
            except VideoUnavailable:
                print("Video is unavailable.")
            except Exception as e:
                print(f"Error downloading video: {e}")
        else:
            print("Not a valid YouTube video URL.")

    def show_context_menu(self, point):
        context_menu = QMenu(self)
        dev_tools_action = QAction("Developer Tools", self)
        dev_tools_action.triggered.connect(self.show_developer_tools)
        context_menu.addAction(dev_tools_action)
        context_menu.exec_(self.mapToGlobal(point))

        check_self_esteem_action = QAction("Check Self-Esteem", self)
        check_self_esteem_action.triggered.connect(self.check_self_esteem)
        context_menu.addAction(check_self_esteem_action)
        
        context_menu.exec_(self.mapToGlobal(point))

    def show_developer_tools(self):
            current_browser = self.tab_widget.currentWidget()
            if current_browser:
                # Basic Analytics: Increment the click count
                self.dev_tools_click_count += 1

                # Advanced Analytics: Log timestamp, URL, and other details
                analytics_entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "url": current_browser.url().toString(),
                    "title": current_browser.title(),
                    "tab_index": self.tab_widget.currentIndex()
                }
                self.advanced_analytics.append(analytics_entry)

                dev_tools_dialog = DeveloperToolsDialog(self)
                info = f"URL: {current_browser.url().toString()}\n"
                info += f"Title: {current_browser.title()}\n"
                info += f"Frame Size: {current_browser.size().width()} x {current_browser.size().height()}\n"
                # Add more details like network bandwidth if needed
                dev_tools_dialog.update_info(info)
                dev_tools_dialog.exec_()

    def print_analytics(self):
        print(f"Developer Tools Clicked: {self.dev_tools_click_count} times")
        print("Advanced Analytics:")
        for entry in self.advanced_analytics:
            print(entry)

    def create_home_page(self):
        home_html = """
        <html>
        <head>
            <title>Home Page</title>
        </head>
        <body>
            <h1>Recently Visited Websites</h1>
            <ul>
        """
        for url in self.recently_visited:
            home_html += f"<li><a href='{url}'>{url}</a></li>"
        
        home_html += """
            </ul>
            <h1>Recommended Websites</h1>
            <ul>
        """
        for url in self.recommendations:
            home_html += f"<li><a href='{url}'>{url}</a></li>"

        home_html += """
            </ul>
        </body>
        </html>
        """
        return home_html
    def analyze_article_content(self, content):
    # Define keywords for low and high self-esteem
        low_self_esteem_keywords = ["worthless", "useless", "inadequate", "inferior", "failure"]
        high_self_esteem_keywords = ["confident", "worthy", "capable", "valuable", "successful"]

        # Perform sentiment analysis
        blob = TextBlob(content)
        sentiment = blob.sentiment.polarity

        # Check for keywords
        low_self_esteem_detected = any(keyword in content.lower() for keyword in low_self_esteem_keywords)
        high_self_esteem_detected = any(keyword in content.lower() for keyword in high_self_esteem_keywords)

        # Determine self-esteem level
        if low_self_esteem_detected or sentiment < -0.5:
            return "Low Self-Esteem Detected: The article you are reading may contain content related to low self-esteem."
        elif high_self_esteem_detected or sentiment > 0.5:
            return "High Self-Esteem Detected: The article you are reading may contain content related to high self-esteem."
        else:
            return "Neutral Self-Esteem: The article you are reading has a neutral tone."
    
    def show_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    def check_self_esteem(self):
        current_browser = self.tab_widget.currentWidget()
        current_browser.page().toPlainText(self.display_self_esteem_message)

    def display_self_esteem_message(self, content):
        message = self.analyze_article_content(content)
        self.show_message("Self-Esteem Analysis", message)
app = QApplication(sys.argv)
window = Browser()
window.show()
sys.exit(app.exec_())