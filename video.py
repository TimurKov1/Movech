import sys

from PyQt5.QtCore import QUrl, Qt, pyqtSlot
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineSettings, QWebEngineView


popups = []


class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = QWebEngineView()
        lay = QVBoxLayout(self)
        lay.addWidget(self.view)
        self.resize(640, 480)


class WebEnginePage(QWebEnginePage):
    def createWindow(self, _type):
        w = Widget()
        w.show()
        popups.append(w)
        return w.view.page()


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=None)

        self.setWindowTitle("My Awesome App")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        label = QLabel("This is a PyQt5 window!", alignment=Qt.AlignCenter)

        self.webview = QWebEngineView()
        self.page = WebEnginePage()
        self.webview.setPage(self.page)
        self.webview.settings().setAttribute(
            QWebEngineSettings.FullScreenSupportEnabled, True
        )

        self.webview.load(
            QUrl("https://vkvd113.mycdn.me/expires/1672234522703/clientType/13/srcIp/194.147.111.70/type/2/mid/2158795958382/id/2623654005480/ms/185.226.53.157/zs/11/srcAg/SAFARI_MAC/ct/28/sig/bwn30tClCdQ/ondemand/hls2_2623654005480.CO7QkJLqPjjLtZ3BAUjuwvnZAVAoWA06Qjb_YUrLoA==.m3u8")
        )

        lay = QVBoxLayout(central_widget)
        lay.addWidget(label)
        lay.addWidget(self.webview)


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()


if __name__ == "__main__":
    main()