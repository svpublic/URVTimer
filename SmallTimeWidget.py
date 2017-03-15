#!/usr/bin/python3

from PyQt5.QtWidgets import QDesktopWidget, QWidget, QHBoxLayout, QLabel, QMenu, QAction, qApp
from PyQt5.QtCore import QBasicTimer, Qt, QDate, QThread, pyqtSignal
from PyQt5.QtGui import QMouseEvent

from URVConnect import URVConnect
from RelativeTime import RelativeTime
from Settings import REFRESH_DELAY, TIME_WIDGET_WIDTH, TIME_WIDGET_HEIGHT


class SmallTimeWidget(QWidget):
    """Небольшой квадратный виджет, выводящий отработанное время."""

    clicked = pyqtSignal()
    is_closed = False

    def __init__(self):
        super().__init__()

        self.thread_finished = False

        # устанавливаем корневой layout
        layout = QHBoxLayout()
        self.setLayout(layout)

        # добавляем QLabel для вывода времени
        self.time_label = QLabel()
        layout.addStretch()
        layout.addWidget(self.time_label)
        layout.addStretch()

        # убираем title bar и значёк на панели задач
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.ToolTip)

        # устанавливаем фиксированный размер и убираем отступы
        self.setFixedSize(TIME_WIDGET_WIDTH, TIME_WIDGET_HEIGHT)
        layout.setContentsMargins(0, 0, 0, 0)

        # переносим в правый верхний угол
        screen_geometry = QDesktopWidget().availableGeometry()
        self.move(screen_geometry.topRight() - self.geometry().topRight())

        # добавляем контекстное меню
        self.menu = QMenu()
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(qApp.quit)
        self.menu.addAction(exit_action)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        # запрашиваем данные с сервера
        self.request_time()

        # добавляем таймер обновления данных
        self.refresh_timer = QBasicTimer()
        self.refresh_timer.start(REFRESH_DELAY*1000, self)

    def timerEvent(self, event):
        # отправляем запрос на сервер
        self.request_time()

    def request_time(self):
        current_date = QDate.currentDate()

        self.urv_connect = URVConnect()
        self.urv_connect.requested_periods = [(current_date, current_date)]

        self.new_thread = QThread()
        self.urv_connect.moveToThread(self.new_thread)
        self.new_thread.started.connect(self.urv_connect.get_urv)
        self.urv_connect.days_data_ready.connect(self.on_data_received)
        self.urv_connect.finished.connect(self.new_thread.quit)
        self.urv_connect.failed.connect(self.on_connection_failed)

        self.new_thread.start()

    def on_data_received(self, urv_data):
        # при получении ответа от сервера обновляем время в QLabel
        time = RelativeTime(total_seconds=urv_data[0])
        two_digit = RelativeTime.two_digit
        time_str = "{0}:{1}".format(two_digit(time.hours), two_digit(time.minutes))
        self.time_label.setText(time_str)

    def mousePressEvent(self, event):
        # при нажатии ЛКМ на виджете запоминаем смещение точки нажатия относительно верхнего левого угла виджета
        event = QMouseEvent(event)
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        # перемещаем виджет вслед за мышью
        event = QMouseEvent(event)
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        # отправляем сигнал двойного клика по виджету и скрываем виджет
        self.refresh_timer.stop()
        self.clicked.emit()
        if hasattr(self, "new_thread") and self.new_thread.isRunning():
            self.setVisible(False)
            self.new_thread.finished.connect(self.close)
        else:
            self.close()

    def closeEvent(self, close_event):
        # устанавливаем флаг is_closed, чтобы контейнер TrashObjects удалил ссылку на виджет
        self.is_closed = True

    def show_context_menu(self, point):
        self.menu.popup(self.mapToGlobal(point))

    def on_connection_failed(self):
        self.time_label.setText("Error")
