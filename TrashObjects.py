#!/usr/bin/python3

from PyQt5.QtCore import QBasicTimer, QObject


class TrashObjects(QObject):
    """Класс предназначен для хранения объектов, ожидающих завершения потока обмена данных с сервером.

    Если контейнер пуст, то при добавлении объекта запускается таймер.
    По таймеру циклически проверяется поле is_closed у каждого объекта в контейнере.
    Ссылки на объекты, у которых is_closed=True, удаляются из контейнера.
    Если контейнер пуст, таймер останавливается до добавления новых объектов.

    """

    def __init__(self):
        super().__init__()
        self.obj_set = set()
        self.timer = QBasicTimer()

    def add(self, obj):
        self.obj_set.add(obj)
        if not self.timer.isActive():
            self.timer.start(1000, self)

    def timerEvent(self, timer_event):
        if len(self.obj_set) > 0:
            self.obj_set = set([obj for obj in self.obj_set if (hasattr(obj, "is_closed") and obj.is_closed is False)])
        else:
            self.timer.stop()

