#!/usr/bin/python3

from PyQt5.QtWidgets import QGridLayout, QLabel, QFrame

from RelativeTime import RelativeTime


class WeekPlanWidget(QFrame):
    def __init__(self):
        super().__init__()

        # устанавливаем табличный layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)
        self.layout.setColumnStretch(2, 1)
        self.layout.setColumnMinimumWidth(0, 150)

        # создаём поле для храниения значения плана
        self.plan_value = RelativeTime()

        # создаём поле для хранения отработанного времени
        self.time_worked = RelativeTime()

        # заполняем первую строку
        # добавляем заголовок строки
        plan_header = QLabel("План на неделю")
        self.layout.addWidget(plan_header, 0, 0)
        # добавляем label для вывода значения плана
        self.plan_value_lbl = QLabel()
        self.layout.addWidget(self.plan_value_lbl, 0, 1)

        # заполняем вторую строку
        # добавляем заголовок строки
        left_time_header = QLabel("Осталось отработать")
        self.layout.addWidget(left_time_header, 1, 0)
        # добавляем label для вывода оставшегося времени
        self.left_time_lbl = QLabel()
        self.layout.addWidget(self.left_time_lbl, 1, 1)

        self.show()

    def update_week_time(self, week_seconds):
        self.time_worked = RelativeTime(total_seconds=week_seconds)
        self.update_left_time_lbl()

    def set_plan_value(self, hours, minutes):
        self.plan_value = RelativeTime(hours=hours, minutes=minutes)
        self.plan_value_lbl.setText(self.plan_value.format("hh:mm"))
        self.update_left_time_lbl()

    def update_left_time_lbl(self):
        left_time = self.plan_value - self.time_worked
        if left_time.total_seconds < 0:
            left_time = RelativeTime(total_seconds=0)
        if left_time.seconds > 0:
            left_time = RelativeTime(
                weeks=left_time.weeks,
                days=left_time.days,
                hours=left_time.hours,
                minutes=left_time.minutes + 1
            )
        self.left_time_lbl.setText(left_time.format("hh:mm"))
