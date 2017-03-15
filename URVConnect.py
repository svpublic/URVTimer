#!/usr/bin/python3

import requests
import re
import json
from contextlib import contextmanager
from PyQt5.QtCore import QObject, pyqtSignal
from requests.exceptions import ConnectTimeout, ConnectionError

from Settings import SERVER_IP, LOGIN, PASSWORD

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


class URVConnect(QObject):
    finished = pyqtSignal()
    period_data_ready = pyqtSignal(int)
    days_data_ready = pyqtSignal(list)
    failed = pyqtSignal(str)
    login = LOGIN
    password = PASSWORD
    employee_id = None
    days = []
    requested_periods = []

    @contextmanager
    def get_session(self):
        url = "https://{0}/login?next=/".format(SERVER_IP)
        with requests.session() as session:
            # отправляем запрос серверу и получаем в ответ токен
            response1 = session.get(url, verify=False, timeout=5)
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://{0}/login?next=/".format(SERVER_IP),
            }
            payload = {
                "csrfmiddlewaretoken": response1.cookies["csrftoken"],
                "login": self.login,
                "password": self.password
            }
            # авторизуемся с логином, паролем и полученным токеном
            response2 = session.post(url, headers=headers, data=payload, verify=False, timeout=5)
            # извлекаем id пользователя
            user_id = self.find_user_id(response2.text)
            url = "https://{0}/api/v1/employee/?user_id={1}".format(SERVER_IP, user_id)
            # по id пользователя получаем json с данными сотрудника
            response3 = session.get(url, verify=False, timeout=5)
            user_data = json.loads(response3.text)
            # извлекаем id сотрудника
            self.employee_id = str(user_data["objects"][0]["id"])
            yield session

    def get_urv(self):
        try:
            urv_data = []
            with self.get_session() as session:
                for period in self.requested_periods:
                    first_day_str = period[0].toString("yyyy-MM-dd")
                    last_day_str = period[1].toString("yyyy-MM-dd")
                    url = "https://{0}/work_time_data/{1}/{2}%2000:00:00/{3}%2023:59:00".format(
                        SERVER_IP,
                        self.employee_id,
                        first_day_str,
                        last_day_str)
                    response = session.get(url, verify=False, timeout=5)
                    work_time_data = json.loads(response.text)
                    total_seconds = int(work_time_data["data"][self.employee_id]["total"])
                    urv_data.append(total_seconds)

            self.days_data_ready.emit(urv_data)
        except ConnectTimeout:
            self.failed.emit("ConnectTimeout")
        except ConnectionError:
            self.failed.emit("ConnectionError")
        except self.UserIdParsingError:
            self.failed.emit("UserIdParsingError")
        finally:
            self.finished.emit()

    @staticmethod
    def find_user_id(text):
        try:
            current_user_info = re.search("window\.currentUser\s?=\s?\{[.\s\S]*\};", text).group(0)
            user_id_string = re.search("id:\s?'\d+'", current_user_info).group(0)
            user_id = re.search("\d+", user_id_string).group(0)
        except AttributeError:
            raise URVConnect.UserIdParsingError
        return user_id

    class UserIdParsingError(Exception):
        pass

