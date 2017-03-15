from PyQt5.QtWidgets import QWidget, QHBoxLayout, QDateEdit, QPushButton, QLabel
from PyQt5.QtCore import QDate, QThread

from URVConnect import URVConnect
from RelativeTime import RelativeTime


class PeriodWidget(QWidget):
    """Виджет предназначен для получения УРВ за выбранный период"""
    def __init__(self):
        super().__init__()

        # задаём горизонтальный layout
        layout = QHBoxLayout()
        self.setLayout(layout)

        # виджет выбора начальной даты
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True)

        # виджет выбора конечной даты
        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)

        # кнопка отправки запроса
        self.get_button = QPushButton("Получить")
        self.get_button.pressed.connect(self.urv_request_period)
        self.get_button.pressed.connect(self.enable_disable_btn)
        self.get_button.setMaximumWidth(100)

        # label, выводящий результат запроса
        self.time_label = QLabel("")

        # добавляем виджеты в layout
        layout.addWidget(self.start_date_edit)
        layout.addWidget(self.end_date_edit)
        layout.addWidget(self.get_button)
        layout.addWidget(self.time_label)
        layout.addStretch()

        # убираем отступы
        layout.setContentsMargins(0, 0, 0, 0)

    def urv_request_period(self):
        """Запрос УРВ за выбранный период"""

        # забираем из виджетов начальную и конечную даты
        start_date = self.start_date_edit.date()
        end_date = self.end_date_edit.date()

        # создаём отдельный поток
        self.new_thread = QThread()

        # Создаём объект URVConnect для выплонения запроса к серверу и переносим его в отдельный поток
        self.urv_connect = URVConnect()
        self.urv_connect.moveToThread(self.new_thread)

        # Сохраняем выбранный период в специальное поле объекта URVConnect
        self.urv_connect.requested_periods = [(start_date, end_date)]

        # Регистрируем слоты для сигналов
        self.urv_connect.days_data_ready.connect(self.on_data_received)
        self.urv_connect.failed.connect(self.on_connection_failed)
        self.urv_connect.finished.connect(self.new_thread.quit)
        self.urv_connect.finished.connect(self.enable_disable_btn)
        self.new_thread.started.connect(self.urv_connect.get_urv)

        # Запускаем поток
        self.new_thread.start()

    def on_data_received(self, urv_data):
        """Метод вызывается при получении запрошенного времени от сервера и выводит его на label"""
        time = RelativeTime(total_seconds=urv_data[0])
        time_values = time.convert(time.HOUR)
        label_text = "{0} ч  {1} мин  {2} сек".format(time_values[0], time_values[1], time_values[2])
        self.time_label.setText(label_text)

    def on_connection_failed(self, reason):
        """Метод вызывается при неудачном соединении с сервером и выводит причину"""
        self.time_label.setText(reason)

    def enable_disable_btn(self):
        """Метод предназначен для активации/деактивации кнопки выполнения запроса"""
        self.get_button.setDisabled(
            self.get_button.isEnabled()
        )
