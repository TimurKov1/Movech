import sys
import hashlib
import sqlite3
import requests
import asyncio
import aiohttp
import datetime as dt
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5.Qt import QImage, pyqtSignal
from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QToolButton,
)
from PyQt5.QtGui import QCursor, QPixmap, QColor, QPainter, QBrush


ID = 0
images = []


def avatar():
    result = cur.execute(f"""SELECT * FROM Users WHERE id = ?""", (ID,)).fetchall()[0]
    if result[5] == None:
        image = Image.open("./images/user.png")
    else:
        image = Image.open(result[5])
    return image


def init(self):
    image = avatar()
    image = image.resize((71, 71))
    new_image = ImageQt(image)

    self.sidebar_logo.setPixmap(QPixmap(QImage(new_image)))
    self.all_films.setCursor(QCursor(QtCore.Qt.PointingHandCursor))


def update_id():
    global ID
    file = open('ID.txt', 'r', encoding='UTF-8')
    ID = int(file.read())
    file.close()


con = sqlite3.connect("Movech.db")
cur = con.cursor()


class ClickedLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, film_id, image):
        super().__init__()
        self.film_id = film_id
        self.image = image

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)

        self.clicked.emit()


class Registration(QMainWindow):
    def __init__(self, x, y):
        super().__init__()
        self.setGeometry(x, y, 1300, 764)
        self.initUI()

    def initUI(self):
        uic.loadUi("./ui/movech_registration.ui", self)
        self.login_button.clicked.connect(self.update_login)
        self.result_registration.clicked.connect(self.create_user)
        self.login_button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.result_registration.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

    def update_login(self):
        self.login_window = Login(self.x(), self.y())
        self.login_window.show()
        self.hide()

    def create_user(self):
        alhabet = "йцукенгшщзхъфывапролджэёячсмитьбю"

        result = cur.execute(
            f"""SELECT * FROM Users WHERE login = ?""", (self.login.text(),)
        ).fetchall()

        if len(result) == 0:
            if (
                self.name.text() == ""
                or self.surname.text() == ""
                or self.login.text() == ""
                or self.password.text() == ""
            ):
                self.error.setText("Заполните все поля")
            elif len(self.password.text()) < 8:
                self.error.setText("Пароль должен иметь длину не менее 8 символов")
            elif (
                self.password.text().isdigit()
                or self.password.text().isalpha()
                or len(set(list(self.password.text())) & set(alhabet)) != 0
            ):
                self.error.setText(
                    "Пароль должен состоять из цифр и букв латинского алфавита"
                )
            else:
                cur.execute(
                    f"""INSERT INTO Users(name, surname, login, password, date) VALUES(?, ?, ?, ?, ?)""",
                    (
                        self.name.text(),
                        self.surname.text(),
                        self.login.text(),
                        hashlib.md5(
                            str(self.password.text()).encode("utf-8")
                        ).hexdigest(),
                        dt.datetime.now().date(),
                    ),
                ).fetchall()
                con.commit()
                file = open('ID.txt', 'w', encoding='UTF-8')
                new_id = int(
                    cur.execute(
                        f"""SELECT id FROM Users WHERE login = ?""",
                        (self.login.text(),),
                    ).fetchall()[0][0]
                )
                file.write(str(new_id))
                file.close()

                self.main_window = MainWindow(self.x(), self.y())
                self.main_window.show()
                self.hide()
        else:
            self.error.setText("Такой логин уже существует")


class Login(QMainWindow):
    def __init__(self, x, y):
        super().__init__()
        self.setGeometry(x, y, 1300, 764)
        self.initUI()

    def initUI(self):
        uic.loadUi("./ui/movech_login.ui", self)
        self.registration_button.clicked.connect(self.update_registration)
        self.result_login.clicked.connect(self.check_user)
        self.registration_button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.result_login.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

    def update_registration(self):
        self.registration_window = Registration(self.x(), self.y())
        self.registration_window.show()
        self.hide()

    def check_user(self):
        result = cur.execute(
            f"""SELECT password FROM Users WHERE login = ?""", (self.login.text(),)
        ).fetchall()

        if len(result) != 0:
            password = result[0][0]
            current_password = hashlib.md5(
                str(self.password.text()).encode("utf-8")
            ).hexdigest()

            if password == current_password:
                file = open('ID.txt', 'w', encoding='UTF-8')
                new_id = int(
                    cur.execute(
                        f"""SELECT id FROM Users WHERE login = ?""",
                        (self.login.text(),),
                    ).fetchall()[0][0]
                )
                file.write(str(new_id))
                file.close()

                self.main_window = MainWindow(self.x(), self.y())
                self.main_window.show()
                self.hide()
            else:
                self.error.setText("Неверный пароль")
        else:
            self.error.setText("Такого пользователя не существует")


class MainWindow(QMainWindow):
    def __init__(self, x, y):
        super().__init__()
        self.setGeometry(x, y, 1300, 764)
        self.initUI()
        init(self)

    def initUI(self):
        global images
        uic.loadUi("./ui/movech_allfilms.ui", self)
        update_id()
        print(ID)
        result = cur.execute(f"""SELECT * FROM Users WHERE id = ?""", (ID,)).fetchall()[0]

        self.sidebar_name.setText(result[1])
        self.sidebar_surname.setText(result[2].upper())

        data = cur.execute(f"""SELECT * FROM Films""").fetchall()
        print(data)
        height = 0

        if len(data) % 4 == 0:
            height = len(data) // 4 * 330
        else:
            height = (len(data) // 4 + 1) * 330

        self.block.resize(930, height)
        if len(images) == 0:
            images = asyncio.run(self.show_images(data))
        count = 0

        for i in images:
            if count == 0:
                self.layout = QHBoxLayout(self)
            elif count % 4 == 0:
                self.films.addLayout(self.layout)
                self.layout = QHBoxLayout(self)

            image = QImage()
            image.loadFromData(i)

            pixmap = QPixmap(image)
            pixmap = pixmap.scaled(224, 322)

            label = ClickedLabel(film_id=data[count][0], image=image)
            label.resize(150, 300)
            label.setPixmap(pixmap)
            label.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
            label.clicked.connect(self.show_film)

            self.layout.addWidget(label)
            count += 1

        self.films.addLayout(self.layout)
        self.header_button.clicked.connect(self.search)

    async def show_images(self, data):
        async with aiohttp.ClientSession() as session:
            tasks = []

            for i in range(len(data)):
                tasks.append(asyncio.create_task(session.get(data[i][-1], ssl=False)))

            responces = await asyncio.gather(*tasks)
            return [await i.content.read() for i in responces]

    def show_film(self):
        self.film = Film(self.x(), self.y(), self.sender().film_id, self.sender().image)
        self.film.show()
        self.hide()

    def search(self):
        text = self.header_search.text().lower()
        result = cur.execute(
            f"""SELECT * FROM Films WHERE title_lower LIKE ?""",
            (f"%{text}%",),
        ).fetchall()

        self.search_window = Search(self.x(), self.y(), result, 0, images=False)
        self.search_window.show()
        self.hide()


class Search(QMainWindow):
    def __init__(self, x, y, data, index, images=False):
        super().__init__()
        self.setGeometry(x, y, 1300, 764)
        self.data = data
        self.index = index
        if images == False:
            self.images = asyncio.run(self.show_images(data))
        else:
            self.images = images
        self.initUI()
        print(self.index)
        init(self)

    def initUI(self):
        uic.loadUi("./ui/movech_search.ui", self)

        if len(self.data[self.index:]) == 0:
            self.label = QLabel(self.main)
            self.label.setGeometry(QtCore.QRect(25, 230, 691, 91))
            self.label.setStyleSheet(
                "color: rgb(239, 239, 239);" 
                "font-size: 20px"
            )
            self.label.setTextFormat(QtCore.Qt.AutoText)
            self.label.setScaledContents(False)
            self.label.setWordWrap(True)
            self.label.setObjectName("label")
            self.label.setText("Нет результатов")
            self.all_films.clicked.connect(self.return_main)
            return 0

        self.prev = QPushButton('назад', self.main)
        self.prev.setGeometry(300, 1100, 150, 60)
        self.prev.setStyleSheet(
            "border: none;"
            "background-color: #224369;"
            "color: #fff;"
            "font-size: 28px;"
            "border-radius: 15px;"
        )

        self.next = QPushButton('вперед', self.main)
        self.next.setGeometry(500, 1100, 150, 60)
        self.next.setStyleSheet(
            "border: none;"
            "background-color: #224369;"
            "color: #fff;"
            "font-size: 28px;"
            "border-radius: 15px;"
        )
        self.next.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.next.clicked.connect(self.swipe_next)
        self.prev.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.prev.clicked.connect(self.swipe_prev)

        for i in range(len(self.data[self.index:(self.index + 3)])):
            film = self.data[self.index + i]

            image = QImage()
            image.loadFromData(self.images[self.index + i])

            pixmap = QPixmap(image)
            pixmap = pixmap.scaled(131, 191)

            self.block_content_item = QWidget(self)
            self.block_content_item.setGeometry(0, 0, 500, 500)

            self.block_img = QLabel(self.block_content_item)
            self.block_img.setGeometry(QtCore.QRect(10, 10, 131, 191))
            self.block_img.setPixmap(pixmap)
            self.block_img.setObjectName("block_img{count}")

            self.block_info = QWidget(self.block_content_item)
            self.block_info.setGeometry(QtCore.QRect(160, 28, 691, 141))
            self.block_info.setStyleSheet("border: none;")
            self.block_info.setObjectName("block_info")

            self.info_title = QLabel(self.block_info)
            self.info_title.setGeometry(QtCore.QRect(10, 0, 700, 51))
            self.info_title.setStyleSheet(
                "color: #fff;" 
                "font-size: 30px;" 
                "font-weight: bold;"
            )
            self.info_title.setTextFormat(QtCore.Qt.PlainText)
            self.info_title.setObjectName("info_title")
            self.info_title.setText(f"{film[1]}")

            self.label = QLabel(self.block_info)
            self.label.setGeometry(QtCore.QRect(10, 60, 691, 91))
            self.label.setStyleSheet(
                "color: rgb(239, 239, 239);" 
                "font-size: 20px"
            )
            self.label.setTextFormat(QtCore.Qt.AutoText)
            self.label.setScaledContents(False)
            self.label.setWordWrap(True)
            self.label.setObjectName("label")
            self.label.setText(f"{film[3][:170]}...")

            self.block_content_layout.addWidget(self.block_content_item)
        self.all_films.clicked.connect(self.return_main)

    async def show_images(self, data):
        async with aiohttp.ClientSession() as session:
            tasks = []

            for i in range(len(data)):
                tasks.append(asyncio.create_task(session.get(data[i][-1], ssl=False)))

            responces = await asyncio.gather(*tasks)
            return [await i.content.read() for i in responces]

    def swipe_next(self):
        self.search_window = Search(self.x(), self.y(), self.data, self.index + 3, images=self.images)
        self.search_window.show()
        self.hide()

    def swipe_prev(self):
        self.search_window = Search(self.x(), self.y(), self.data, self.index - 3, images=self.images)
        self.search_window.show()
        self.hide()

    def return_main(self):
        self.main = MainWindow(self.x(), self.y())
        self.main.show()
        self.hide()


class Film(QMainWindow):
    def __init__(self, x, y, film_id, image):
        super().__init__()
        self.setGeometry(x, y, 1300, 764)
        self.film_id = film_id
        self.image = image
        self.initUI()
        init(self)

    def initUI(self):
        uic.loadUi("./ui/movech_film.ui", self)
        result = cur.execute(
            f"""SELECT * FROM Films WHERE id={self.film_id} """
        ).fetchall()[0]
        self.title.setText(f"{result[1]} ({result[4]})")
        self.year.setText(f"{result[4]}")
        self.country.setText(f"{result[5]}")
        self.genre.setText(f"{result[6]}")
        self.director.setText(f"{result[7]}")
        if result[8] != "":
            self.budget.setText(f"${result[8]}")
        else:
            self.budget.setText(f"Нет данных")
        self.description.setText(f"{result[3]}")
        pixmap = QPixmap(self.image)
        pixmap = pixmap.scaled(191, 281)
        self.block_img.setPixmap(pixmap)
        self.all_films.clicked.connect(self.return_main)

    def return_main(self):
        self.main = MainWindow(self.x(), self.y())
        self.main.show()
        self.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Login(0, 0)
    ex.show()
    sys.exit(app.exec())
