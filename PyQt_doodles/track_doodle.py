#!/usr/bin/python3


import os
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


BG = os.path.join(os.path.dirname(__file__), 'bg.png')
EXIT_PNG = os.path.join(os.path.dirname(__file__), 'exit2.png')
ICO = os.path.join(os.path.dirname(__file__), '32x32.ico')

MENU_BUTTONS_STYLE = 'QPushButton {background-color: rgba(0, 125, 0, 0); color: #ffffff;}'
STATUS_STYLE = 'QStatusBar {background-color: rgba(0, 125, 0, 10); color: #bfc4bf }' ##ffffff;}'
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
        self.create_main_window()
        self.create_menubar_actions()
        self.create_menubar()
        self.create_statusbar()
        self.create_buttons()
        self.__clickPos = QPoint()

        self.show()

    def create_main_window(self):
        self.palette.setBrush(QPalette.Background, QBrush(QPixmap(BG)))
        self.setPalette(self.palette)
        self.setWindowIcon(QIcon(ICO))
        self.setFixedSize(430, 350)
        self.setWindowTitle('Main Window')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMouseTracking(True)

    def create_menubar_actions(self):
        self.exitAction = QAction(QIcon(EXIT_PNG), '&Exit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(qApp.quit)

        self.openAction = QAction('&Open', self)
        self.openAction.setShortcut('Ctrl+O')
        self.openAction.setStatusTip('Open dataset')
        self.openAction.triggered.connect(self.get_dataset)

    def create_menubar(self):
        self.menubar = self.menuBar()
        self.menubar.setStyleSheet(MENUBAR_STYLE)
        self.fileMenu = self.menubar.addMenu('&File')
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.exitAction)

    def create_statusbar(self):
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet(STATUS_STYLE)
        self.status_bar.showMessage('')

    def create_buttons(self):
        self.quit_btn = WindowButton(self, '[X]', MENU_BUTTONS_STYLE,
                                    18, 17, 412, 0, QCoreApplication.instance().quit, True)
        self.minize_btn = WindowButton(self, '[_]', MENU_BUTTONS_STYLE,
                                      18, 17, 395, 0, self.showMinimized, True)

    def mousePressEvent(self, e):
        self.__clickPos = e.pos()

    def mouseReleaseEvent(self, e):
        self.move(e.globalPos() - self.__clickPos)

    def get_dataset(self):
        filename = QFileDialog.getOpenFileName(self, 'Open valid dataset',
                                               os.getenv('HOME')) # , filter='.csv')
        if filename[0]:
            self.status_bar.showMessage('Dataset {} loaded. '
                                        'Choose the model to run.'.format(
                                            os.path.split(filename[0])[1]))
        else:
            self.handle_error(filename[0])

    def handle_error(self, error_msg):
        self.status_bar.showMessage('Error: {:<.66}'.format(error_msg))


if __name__ == '__main__':
    app = QApplication([])
    main_window = MainWindow()
    sys.exit(app.exec())