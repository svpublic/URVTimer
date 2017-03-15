#!/usr/bin/python3

from PyQt5.QtWidgets import QGridLayout, QLabel, QPushButton, QDialog, QFormLayout, QDialogButtonBox, QTimeEdit, QFrame
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTime

from RelativeTime import RelativeTime


class TodayPlanWidget(QFrame):
    def __init__(self):
        super().__init__()

        # устанавливаем табличный layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)
        self.layout.setColumnStretch(3, 1)
        self.layout.setColumnMinimumWidth(0, 150)

        # создаём поле для храниения значения плана
        self.plan_value = RelativeTime()

        # создаём поле для хранения отработанного времени
        self.today_time = RelativeTime()

        # заполняем первую строку
        # добавляем заголовок строки
        plan_header = QLabel("План на сегодня")
        self.layout.addWidget(plan_header, 0, 0)
        # добавляем label для вывода значения плана
        self.plan_value_lbl = QLabel()
        self.layout.addWidget(self.plan_value_lbl, 0, 1)
        # добавляем кнопку редактирования плана
        self.edit_plan_btn = QPushButton()
        self.edit_plan_btn.setMaximumWidth(50)
        pixmap = QPixmap("edit_icon.png")
        edit_icon = QIcon(pixmap)
        self.edit_plan_btn.setIcon(edit_icon)
        self.edit_plan_btn.pressed.connect(self.edit_plan)
        self.layout.addWidget(self.edit_plan_btn, 0, 2)

        # заполняем вторую строку
        # добавляем заголовок строки
        left_time_header = QLabel("Осталось отработать")
        self.layout.addWidget(left_time_header, 1, 0)
        # добавляем label для вывода оставшегося времени
        self.left_time_lbl = QLabel()
        self.layout.addWidget(self.left_time_lbl, 1, 1)

        # заполняем третью строку
        # добавляем заголовок строки
        exit_time_header = QLabel("Время выхода")
        self.layout.addWidget(exit_time_header, 2, 0)
        # добавляем label для вывода расчётного времени ухода
        self.exit_time_lbl = QLabel()
        self.layout.addWidget(self.exit_time_lbl, 2, 1)

        self.show()

    def edit_plan(self):
        time_dialog = TimeDialog(QTime(self.plan_value.hours, self.plan_value.minutes))
        time_dialog.setWindowTitle("Запланировать")
        result, qtime = time_dialog.exec()
        if result:
            self.set_plan_value(qtime.hour(), qtime.minute())

    def set_plan_value(self, hours, minutes):
        self.plan_value = RelativeTime(hours=hours, minutes=minutes)
        self.plan_value_lbl.setText(self.plan_value.format("hh:mm"))
        self.update_left_time_lbl()
        self.update_exit_time_lbl()

    def update_today_time(self, today_seconds):
        self.today_time = RelativeTime(total_seconds=today_seconds)
        self.update_left_time_lbl()
        self.update_exit_time_lbl()

    def update_left_time_lbl(self):
        left_time = self.plan_value - self.today_time
        if left_time.total_seconds < 0:
            left_time = RelativeTime(total_seconds=0)
        if left_time.seconds > 0:
            left_time = RelativeTime(
                weeks=left_time.weeks,
                days=left_time.days,
                hours=left_time.hours,
                minutes=left_time.minutes+1
            )
        self.left_time_lbl.setText(left_time.format("hh:mm"))

    def update_exit_time_lbl(self):
        current_time = QTime().currentTime()
        current_time = RelativeTime(
            hours=current_time.hour(),
            minutes=current_time.minute(),
            seconds=current_time.second()
        )
        exit_time = current_time + self.plan_value - self.today_time
        if exit_time.seconds > 0:
            exit_time = RelativeTime(
                weeks=exit_time.weeks,
                days=exit_time.days,
                hours=exit_time.hours,
                minutes=exit_time.minutes+1
            )
        self.exit_time_lbl.setText(exit_time.format("hh:mm"))


class TimeDialog(QDialog):
    def __init__(self, default_time):
        super().__init__()
        main_layout = QFormLayout(self)
        set_time_lbl = QLabel("Задайте время")
        self.time_edit = QTimeEdit(default_time)
        main_layout.addRow(set_time_lbl, self.time_edit)

        button_box = QDialogButtonBox(Qt.Horizontal, self)
        button_box.addButton(QDialogButtonBox.Cancel)
        button_box.addButton(QDialogButtonBox.Ok)
        button_box.accepted.connect(super().accept)
        button_box.rejected.connect(super().reject)
        main_layout.addRow(button_box)

    def exec(self):
        return super().exec(), self.time_edit.time()
