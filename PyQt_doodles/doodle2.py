#!/usr/bin/python3


import os
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


BG = os.path.join(os.path.dirname(__file__), 'bg.png')
EXIT_PNG = os.path.join(os.path.dirname(__file__), 'exit2.png')
ICO = os.path.join(os.path.dirname(__file__), '32x32.ico')


MENU_BUTTONS_STYLE = 'QPushButton {background-color: rgba(0, 125, 0, 0); color: #ffffff;}'
STATUS_STYLE = 'QStatusBar {background-color: rgba(0, 125, 0, 0); color: #bfc4bf }' ##ffffff;}'
MENUBAR_STYLE = 'QMenuBar {background-color: rgba(61, 73, 61, 100); color: #ffffff;}'


class WindowLabel(QLabel):

    def __init__(self, window, text, style, fontsize,
                 posX, posY, bold=False, act_label=False):
        super().__init__(text, window)
        self.setStyleSheet(style)
        if act_label:
            self.setMinimumSize(QSize(500, 20))
        if bold:
            self.setFont(QFont("", fontsize, QFont.Bold, True))
        else:
            self.setFont(QFont("", fontsize, True))
        self.move(posX, posY)


class WindowButton(QPushButton):

    def __init__(self, window, text, style, qsizeA, qsizeB,
                 posX, posY, func, flat=False, fontsize=0):
        super().__init__("", window)
        self.setText(text)
        self.setStyleSheet(style)
        self.resize(QSize(qsizeA, qsizeB))
        self.move(posX, posY)
        self.clicked.connect(func)
        if flat:
            self.setFlat(True)
        if fontsize:
            self.setFont(QFont("", fontsize, QFont.Bold, True))


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.palette = QPalette()
        self.__clickPos = QPoint()

        self.create_main_window()
        self.create_actions()
        self.create_menubar()
        self.create_statusbar()
        self.create_buttons()
        self.create_progressbar

        self.show()

    def create_main_window(self):
        self.palette.setBrush(QPalette.Background, QBrush(QPixmap(BG)))
        self.setPalette(self.palette)
        self.setWindowIcon(QIcon(ICO))
        self.setFixedSize(430, 350)
        self.setWindowTitle('Main Window')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMouseTracking(True)

    def create_actions(self):
        self.exit_action = QAction(QIcon(EXIT_PNG), '&Quit', self)
        self.exit_action.setShortcut('Ctrl-Q')
        self.exit_action.setStatusTip('Exit application')
        self.exit_action.triggered.connect(qApp.quit)

        self.open_action = QAction('&Open', self)
        self.open_action.setShortcut('Ctrl-O')
        self.open_action.setStatusTip('Open file')
        self.open_action.triggered.connect(self.get_file)

    def create_menubar(self):
        self.menuBar()
        self.menuBar().setStyleSheet(MENUBAR_STYLE)
        self.file_menu = self.menuBar().addMenu('&File')
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.exit_action)

    def create_statusbar(self):
        self.statusBar()
        self.statusBar().setStyleSheet(STATUS_STYLE)
        self.statusBar().showMessage('')

    def create_buttons(self):
        self.quit_btn = WindowButton(self, '[X]', MENU_BUTTONS_STYLE,
                                    18, 17, 412, 0, QCoreApplication.instance().quit, True)
        self.minize_btn = WindowButton(self, '[_]', MENU_BUTTONS_STYLE,
                                      18, 17, 395, 0, self.showMinimized, True)

    def create_progressbar(self):
        self.progress_br = QProgressBar(self)
        self.progress_br.setGeometry(200, 80, 250, 20)
        self.progress_br.show()

    def get_file(self):
        pass





if __name__ == '__main__':
    app = QApplication([])
    ModelRunner = MainWindow()
    sys.exit(app.exec())

