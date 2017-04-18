#!/usr/env python

# version 0.9
# developed by Artur Zych
# 06.2016, updated 10.2016

import time
import sys
import pyodbc
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


MAIN_WINDOW_TITLE = "CBRE Time Tracker"
COMPANY = 'CBRE'
TOOL_NAME = 'Time Tracker'
ACTIVITY_SELECTION_CAPTION = 'Select an activity:'

MENU_BUTTONS_STYLE = 'QPushButton {background-color: rgba(0, 125, 0, 0); color: #ffffff;}'
MAIN_WINDOW_LABEL_STYLE = 'QLabel {color: #ffffff;}'
STOP_BUTTON_STYLE = 'QPushButton {border-style: outset; border-width: 1px; background-color: #860927;' \
                    'border-color: #fdfdfd; color: rgb(252, 252, 252);}'
START_BUTTON_STYLE = 'QPushButton {border-style: outset; border-width: 1px; background-color: #50c752;' \
                     'border-color: #fdfdfd; color: rgb(252, 252, 252);}'
INACTIVE_STYLE = 'QPushButton {border-style: outset; border-width: 1px; background-color: #959596;' \
                 'border-color: #fdfdfd; color: rgb(252, 252, 252);}'
ACTIVITIES_STYLE = 'QComboBox {border-style: outset; border-width: 1px; ' \
                   'border-color: rgb(80, 199, 82); color: rgb(80, 199, 82);}'

BG = 'bg2.jpg'
ICO = '32x32.ico'

START_TIME = ''
STOP_TIME = ''
DATE = ''

DB_PATH = r'''Y:\12 Analyst\HACKATHON\MySQL2.accdb'''
DB_CONN_STRING = "DRIVER={Microsoft Access Driver (*.mdb, *.accdb)}; " \
                 "DBQ=%s; UID=%s;, autocommit=True" % (DB_PATH, 'azych')

GET_GROUP_ID = 'SELECT * FROM Users WHERE Name_Users=?'
GET_ACTIVITY_ID = 'SELECT ID_Activities FROM Activities WHERE Name_Activities=?'
GET_USER_ID = 'SELECT ID_Users FROM Users WHERE Name_Users=?'
GET_CLIENT_NAMES = 'SELECT Name_Clients FROM Clients WHERE ID_Users=?'
GET_ACTIVITIES = 'SELECT Name_Activities FROM Activities WHERE ID_Groups=?'
GET_PROJECT_ID = 'SELECT ID_Projects FROM Project WHERE Name_Projects=?'
GET_CLIENT_ID = 'SELECT ID_Clients FROM Clients WHERE Name_Clients=?'


def get_sql_single_data(key_value, sql_query):
    db_connection = pyodbc.connect(DB_CONN_STRING)
    db_cursor = db_connection.cursor()
    db_cursor.execute(sql_query, key_value)
    return_value = db_cursor.fetchall()[0][0]
    db_connection.close()
    return return_value


def get_sql_list_data(key_value, sql_query):
    db_connection = pyodbc.connect(DB_CONN_STRING)
    db_cursor = db_connection.cursor()
    db_cursor.execute(sql_query, key_value)
    return_list = [i[0] for i in db_cursor.fetchall()]
    db_connection.close()
    return return_list


saved_flag = True


class WindowLabel(QLabel):
    def __init__(self, window, text, style, fontsize, posX, posY, bold=False, act_label=False):
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
    def __init__(self, window, text, style, qsizeA, qsizeB, posX, posY, func, flat=False, fontsize=0):
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


class Activities_list(QComboBox):
    def __init__(self, window, list, posX, posY, width):
        super().__init__(window)
        self.addItems(list)
        self.move(posX, posY)
        self.setFixedWidth(width)


class Activity():
    def __init__(self, start_time='', activity_name='', username='', end_time='', days_date='',
                 client='', project_name=''):
        self.start_time = start_time
        self.end_time = end_time
        self.activity_name = activity_name
        self.username = username
        self.user_id = 0.0
        self.group_id = 0.0
        self.date = days_date
        self.full_start_date = ''
        self.full_end_date = ''
        self.project = ''
        self.client_id = 0.0
        self.project_name = project_name
        self.client = client

    def save(self):
        self.end_time = time.strftime("%H" + ":" + "%M" + ":" + "%S")
        self.date = time.strftime('%d/%m/%Y')
        self.user_id = float(get_sql_single_data(self.username, GET_USER_ID))
        self.activity_name = float(get_sql_single_data(self.activity_name, GET_ACTIVITY_ID))
        self.group_id = float(get_sql_single_data(self.username, GET_GROUP_ID))
        self.full_start_date = str(self.date + ' ' + self.start_time)
        self.full_end_date = str(self.date + ' ' + self.end_time)
        self.project = str(get_sql_single_data(self.project_name, GET_PROJECT_ID))
        self.client_id = float(get_sql_single_data(self.client, GET_CLIENT_ID))

        db_connection = pyodbc.connect(DB_CONN_STRING)
        db_cursor = db_connection.cursor()
        db_cursor.execute('INSERT into User_Activities (ID_Users, ID_Activities, Start_UA, End_UA, '
                          'ID_Clients, Comments_UA, ID_Group, Project) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                          (self.user_id, self.activity_name, self.full_start_date, self.full_end_date,
                           self.client_id, '', self.group_id, self.project))
        db_connection.commit()
        db_connection.close()


class ClockR(object):
    def __init__(self, label, totalTime):
        self.label = label
        self.totalTime = totalTime
        self.timer = QTimer(interval=1000)
        self.timer.timeout.connect(self.update_timer)

    def update_timer(self):
        self.totalTime += 1
        self.count()

    def start(self):
        self.timer.start()

    def count(self):
        self.label.setStyleSheet(MAIN_WINDOW_LABEL_STYLE)
        self.label.setText(time.strftime("%H" + ":" + "%M" + ":" + "%S"))


def main():

    new_activity = Activity()


    def save_and_quit():
        global new_activity
        global saved_flag
        app_instance.quit()
        # if saved_flag:
        #     app_instance.quit()
        # else:
        #     new_activity.save()
        #     app_instance.quit()


    def start_activity():
        global new_activity
        global saved_flag
        new_activity = Activity(start_time=time.strftime("%H" + ":" + "%M" + ":" + "%S"),
                                activity_name=activities_list.currentText(),
                                username=os.getlogin(),
                                client=clients_list.currentText(),
                                project_name=project_list.currentText())
        start_button.setEnabled(False)
        start_button.setStyleSheet(INACTIVE_STYLE)
        stop_button.setEnabled(True)
        stop_button.setStyleSheet(STOP_BUTTON_STYLE)
        saved_flag = False
        current_activity_label.move(18, 245)
        current_activity_label.setText('\tCurrent: {} | {} | '
                                       '{} started: {}'.format(
                                        new_activity.client, new_activity.project_name,
                                        new_activity.activity_name, new_activity.start_time))


    def stop_activity():
        global new_activity
        start_button.setEnabled(True)
        start_button.setStyleSheet(START_BUTTON_STYLE)
        stop_button.setEnabled(False)
        stop_button.setStyleSheet(INACTIVE_STYLE)
        new_activity.save()
        saved_flag = True
        current_activity_label.move(100, 245)
        current_activity_label.setText('Current: {0} | {0} | {0} started: {0}'.format('N/A'))


    group_id = str(get_sql_single_data(os.getlogin().lower(), GET_GROUP_ID))
    user_id = float(get_sql_single_data(os.getlogin().lower(), GET_USER_ID))
    data = get_sql_list_data(group_id, GET_ACTIVITIES)
    client_names = (get_sql_list_data(user_id, GET_CLIENT_NAMES))
    projects = ['proj ' + str(i) for i in range(1, 16)]


    app = QApplication(sys.argv)
    app_instance = QCoreApplication.instance()
    main_window = QWidget()
    palette = QPalette()


    palette.setBrush(QPalette.Background, QBrush(QPixmap(BG)))
    main_window.setPalette(palette)
    main_window.setWindowIcon(QIcon(ICO))
    main_window.setFixedSize(430, 350)
    main_window.setWindowTitle(MAIN_WINDOW_TITLE)
    main_window.setWindowFlags(Qt.FramelessWindowHint)
    main_window.manual_window = None


    label_company = WindowLabel(main_window, COMPANY, MAIN_WINDOW_LABEL_STYLE, 28, 150, 5, True)
    label_tool_name = WindowLabel(main_window, TOOL_NAME, MAIN_WINDOW_LABEL_STYLE, 20, 127, 45)
    client_label = WindowLabel(main_window, 'Client: ', MAIN_WINDOW_LABEL_STYLE, 10, 90, 144, False)
    proj_label = WindowLabel(main_window, 'Project: ', MAIN_WINDOW_LABEL_STYLE, 10, 90, 168, False)
    activity_label = WindowLabel(main_window, 'Activity: ', MAIN_WINDOW_LABEL_STYLE, 10, 90, 192, False)
    quit_button = WindowButton(main_window, '[X]', MENU_BUTTONS_STYLE,
                               18, 17, 2, 0, save_and_quit, True)
    minimize_button = WindowButton(main_window, '[_]', MENU_BUTTONS_STYLE,
                                   18, 17, 412, 0, main_window.showMinimized, True)
    start_button = WindowButton(main_window, 'START', START_BUTTON_STYLE, 14, 30, 20, 285, start_activity, True)
    start_button.setFixedSize(120, 35)
    stop_button = WindowButton(main_window, 'STOP', STOP_BUTTON_STYLE, 14, 30, 290, 285, stop_activity, True)
    stop_button.setFixedSize(120, 35)
    stop_button.setEnabled(False)
    stop_button.setStyleSheet(INACTIVE_STYLE)
    activities_list = Activities_list(main_window, data, 20, 180, 120)
    activities_list.move(142, 190)
    clients_list = Activities_list(main_window, client_names, 20, 180, 120)
    clients_list.move(142, 142)
    project_list = Activities_list(main_window, projects, 20, 180, 120)
    project_list.move(142, 166)
    user_label = WindowLabel(main_window, '', MAIN_WINDOW_LABEL_STYLE, 10, 164, 222, act_label=True)
    user_label.setText('User: {}'.format(os.getlogin()))
    current_activity_label = WindowLabel(main_window, '', MAIN_WINDOW_LABEL_STYLE, 10, 100, 245, act_label=True)
    current_activity_label.setText('Current: {0} | {0} | {0} started: {0}'.format('N/A'))
    clock_label = WindowLabel(main_window, '', MAIN_WINDOW_LABEL_STYLE, 20, 150, 90)
    clock_label.setFixedWidth(150)


    rtm_clock = ClockR(clock_label, 0)
    rtm_clock.start()


    main_window.show()
    sys.exit(app.exec_())


main()
