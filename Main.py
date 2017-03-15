#!/usr/bin/python3

import sys
from PyQt5.QtWidgets import QApplication, qApp
from PyQt5.QtGui import QIcon

from TimerMainWindow import TimerMainWindow
from SmallTimeWidget import SmallTimeWidget
from TrashObjects import TrashObjects


class WindowsManager(QApplication):
    """Класс для управления окнами приложения, создания виджетов главного окна и таймера и хранения ссылок на них"""

    def __init__(self, list_of_str):
        super().__init__(list_of_str)

        # Отключаем выход из приложения при закрытии всех окон
        self.setQuitOnLastWindowClosed(False)

        # Показываем основное окно приложения с таблицей за 2 недели
        self.main_window = TimerMainWindow()
        self.main_window.closed.connect(self.on_main_window_closed)
        self.main_window.show()

        # создаём поле для хранения ссылки на маленький таймер
        self.small_timer = None

        # Перед закрытием виджета необходимо дождаться завершения потока обмена данными с сервером
        # Каждый скрытый с экрана виджет переносится в контейнер trash_objects, где дожидается закрытия
        self.trash_objects = TrashObjects()

    def on_main_window_closed(self):
        """Метод вызывается при закрытии или сворачивании главного окна.

        Если главное окно было закрыто через кнопку "крестик", то выполняется выход из приложения.
        Если главное окно было закрыто через кнопку "свернуть", то создаётся и выводится таймер.
        Ссылка на старый таймер переносится в trash_objects.

        """

        if not self.main_window.minimize_pressed:
            qApp.quit()
        else:
            self.trash_objects.add(self.small_timer)
            self.small_timer = SmallTimeWidget()
            self.small_timer.clicked.connect(self.on_small_timer_clicked)
            self.small_timer.show()

    def on_small_timer_clicked(self):
        """Метод вызывается при двойном клике по таймеру.

        Ссылка на виджет старого главного окна переносится в trash_objects.
        Создаётся и выводится новый виджет главного окна.

        """

        self.trash_objects.add(self.main_window)
        self.main_window = TimerMainWindow()
        self.main_window.show()
        self.main_window.closed.connect(self.on_main_window_closed)

if __name__ == "__main__":
    app = WindowsManager(sys.argv)
    app.setWindowIcon(QIcon("clock-icon.png"))
    sys.exit(app.exec())
