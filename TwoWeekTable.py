#!/usr/bin/python3

from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal
from PyQt5.QtGui import QColor

from URVConnect import URVConnect
from RelativeTime import RelativeTime


class TwoWeekTable(QTableWidget):
    """Виджет выводит в форме таблицы отработанное время за текущую и прошлую недели."""

    today_time_received = pyqtSignal(int)
    week_time_received = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setColumnCount(8)
        self.setRowCount(4)
        self.setFixedHeight(150)
        self.setMinimumWidth(400)
        self.last_update_status = ""
        self.setHorizontalHeaderLabels(["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс", chr(8721)])
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setFocusPolicy(Qt.NoFocus)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.last_week_days = self.get_week_days(-1)
        self.today_time = RelativeTime()

        # вписываем в таблицу даты
        for i in range(len(self.last_week_days)):
            self.setItem(0, i, QTableWidgetItem(self.last_week_days[i].toString("dd MMM")))
        self.current_week_days = self.get_week_days()
        for i in range(len(self.current_week_days)):
            self.setItem(2, i, QTableWidgetItem(self.current_week_days[i].toString("dd MMM")))
        # добавляем ячейки для данных
        for col_id in range(self.columnCount()):
            for row_id in [1, 3]:
                self.setItem(row_id, col_id, QTableWidgetItem(), color=QColor(146, 236, 236))

    def setItem(self, row_number, cell_number, item, color=None):
        item.setTextAlignment(Qt.AlignCenter)
        if color is not None:
            item.setBackground(color)
        super().setItem(row_number, cell_number, item)

    @staticmethod
    def table_time_format(relative_time):
        time_values = relative_time.convert(relative_time.HOUR)
        return "{0}:{1}".format(time_values[0], time_values[1])

    def request_days_data(self):
        # значение last_update_status циклически запрашивается главным виджетом
        self.last_update_status = "updating"

        # массив периодов, которые будут запрошены
        periods = []

        # добавляем в массив дни прошлой недели
        for day in self.last_week_days:
            periods.append((day, day))
        periods.append((self.last_week_days[0], self.last_week_days[-1]))

        # добавляем в массив дни текущей недели
        for day in self.current_week_days:
            periods.append((day, day))
        periods.append((self.current_week_days[0], self.current_week_days[-1]))

        # создаём объект для общения с сервером
        self.urv_connect = URVConnect()
        # чтобы не заморачиваться с передачей периодов через сигналы, просто прописываем их в поле объекта
        self.urv_connect.requested_periods = periods

        # переносим общение с сервером в отдельный поток
        self.new_thread = QThread()
        self.urv_connect.moveToThread(self.new_thread)

        # назначаем слоты для сигналов
        self.new_thread.started.connect(self.urv_connect.get_urv)
        self.urv_connect.finished.connect(self.new_thread.quit)
        self.urv_connect.days_data_ready.connect(self.on_data_received)
        self.urv_connect.failed.connect(self.on_connection_failed)

        # отправляем запрос на сервер
        self.new_thread.start()

    def on_data_received(self, urv_data):
        # первые 7 элементов списка содержат время по дням прошлой недели
        for i in range(7):
            relative_time = RelativeTime(total_seconds=urv_data[i])
            self.item(1, i).setText(relative_time.format("hh:mm"))
        # 8й элемент списка содержит сумму за прошлую неделю
        relative_time = RelativeTime(total_seconds=urv_data[7])
        self.item(1, 7).setText(relative_time.format("hh:mm"))

        # элементы с 9 по 15й содержат время по дням текущей недели недели
        for i in range(7):
            relative_time = RelativeTime(total_seconds=urv_data[i + 8])
            self.item(3, i).setText(relative_time.format("hh:mm"))
        # 16й элемент списка содержит сумму за текущую неделю
        relative_time = RelativeTime(total_seconds=urv_data[15])
        self.item(3, 7).setText(relative_time.format("hh:mm"))

        self.today_time_received.emit(urv_data[QDate.currentDate().dayOfWeek() + 7])
        self.week_time_received.emit(urv_data[15])

        self.last_update_status = "OK"

    def on_connection_failed(self, reason):
        self.last_update_status = reason

    @staticmethod
    def get_first_day_of_current_week():
        current_date = QDate.currentDate()
        day_of_week = current_date.dayOfWeek()
        if day_of_week == 1:
            first_day = current_date
        else:
            first_day = current_date.addDays(1 - day_of_week)
        return first_day

    @staticmethod
    def get_week_days(week_number=0):
        days = []
        first_day = TwoWeekTable.get_first_day_of_current_week().addDays(week_number * 7)
        days.append(first_day)
        for i in range(1, 7):
            next_day = first_day.addDays(i)
            days.append(next_day)
        return days


