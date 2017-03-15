#!/usr/bin/python3

from PyQt5.QtWidgets import QDesktopWidget, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QTabWidget, QFrame
from PyQt5.QtCore import QBasicTimer, pyqtSignal, QEvent

from TwoWeekTable import TwoWeekTable
from Settings import LOGIN, TODAY_PLAN_HOURS, TODAY_PLAN_MINUTES, REFRESH_DELAY, WEEK_PLAN_HOURS, WEEK_PLAN_MINUTES
from TodayPlanWidget import TodayPlanWidget
from PeriodWidget import PeriodWidget
from WeekPlanWidget import WeekPlanWidget


class TimerMainWindow(QMainWindow):
    """Главное окно приложения"""

    closed = pyqtSignal()
    minimize_pressed = False
    is_closed = False

    def __init__(self):
        super().__init__()

        # устанавливаем центральный виджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # устанавливаем вертикальный корневой layout
        v_layout = QVBoxLayout()
        main_widget.setLayout(v_layout)

        # добавляем таблицу статистики за 2 недели
        self.weeks_table = TwoWeekTable()
        v_layout.addWidget(self.weeks_table)

        # добавляем виджет получения урв за выбранный период
        period_widget = PeriodWidget()
        v_layout.addWidget(period_widget)

        # панель вкладок для плана на сегодня/неделю
        plan_tabs = QTabWidget()
        today_tab_frame = QFrame()
        today_tab_layout = QVBoxLayout()
        today_tab_layout.setContentsMargins(0, 0, 0, 0)
        today_tab_frame.setLayout(today_tab_layout)
        plan_tabs.addTab(today_tab_frame, "Сегодня")
        week_tab_frame = QFrame()
        week_tab_layout = QVBoxLayout()
        week_tab_layout.setContentsMargins(0, 0, 0, 0)
        week_tab_frame.setLayout(week_tab_layout)
        plan_tabs.addTab(week_tab_frame, "Неделя")
        plan_tabs_layout = QHBoxLayout()
        plan_tabs_layout.addWidget(plan_tabs)
        plan_tabs_layout.addStretch()
        v_layout.addLayout(plan_tabs_layout)

        # добавляем виджет, выводящий расчётное время окончания работы за сегодня
        self.today_plan_widget = TodayPlanWidget()
        self.today_plan_widget.set_plan_value(hours=TODAY_PLAN_HOURS, minutes=TODAY_PLAN_MINUTES)
        today_tab_layout.addWidget(self.today_plan_widget)
        today_tab_layout.addStretch()
        self.weeks_table.today_time_received.connect(self.today_plan_widget.update_today_time)

        # добавляем виджет плана на неделю
        self.week_plan_widget = WeekPlanWidget()
        self.week_plan_widget.set_plan_value(hours=WEEK_PLAN_HOURS, minutes=WEEK_PLAN_MINUTES)
        week_tab_layout.addWidget(self.week_plan_widget)
        week_tab_layout.addStretch()
        self.weeks_table.week_time_received.connect(self.week_plan_widget.update_week_time)

        v_layout.addStretch()

        # добляем таймер обновления данных
        self.table_refresh_timer = QBasicTimer()
        self.table_refresh_delay = REFRESH_DELAY * 1000
        self.table_refresh_time = 0
        self.table_refresh_timer.start(1000, self)

        self.setWindowTitle("URV Timer - {0}".format(LOGIN))
        self.center()

        self.close_emitted = False

    def timerEvent(self, timer_event):
        """выводим в статусную строку статус последнего запроса к серверу и таймер следующего обновления"""
        if self.table_refresh_time > 0:
            self.table_refresh_time -= 1000
        else:
            self.weeks_table.request_days_data()
            self.table_refresh_time = self.table_refresh_delay
        self.statusBar().showMessage(
            "Update status: {0}  (next update in {1} seconds)".format(
                self.weeks_table.last_update_status, int(self.table_refresh_time / 1000)
            )
        )

    def center(self):
        widget_geometry = self.frameGeometry()
        screen_central_point = QDesktopWidget().availableGeometry().center()
        widget_geometry.moveCenter(screen_central_point)
        self.move(widget_geometry.topLeft())

    def closeEvent(self, event):
        self.table_refresh_timer.stop()
        # посылаем в WindowsManager сигнал о закрытии
        if not self.close_emitted:
            self.closed.emit()
            self.close_emitted = True
        # если поток обмена данными с сервером ещё существует, то отменяем закрытие виджета и просто скрываем его
        if hasattr(self.weeks_table, "new_thread") and self.weeks_table.new_thread.isRunning():
            event.ignore()
            # когда поток наконец будет закрыт, метод close будет вызван повторно
            self.weeks_table.new_thread.finished.connect(self.close)
            self.setVisible(False)
        # если поток остановлен, закрываем виджет и устанавливаем флаг is_closed, чтобы контейнер TrashObjects
        # удалил ссылку на виджет
        else:
            event.accept()
            self.is_closed = True

    def changeEvent(self, event):
        event = QEvent(event)
        if event.type() == QEvent.WindowStateChange and self.isMinimized():
            self.minimize_pressed = True
            self.close()

