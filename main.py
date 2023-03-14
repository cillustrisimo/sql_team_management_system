from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget, QGridLayout, \
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QComboBox, QToolBar
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt

import sys
import sqlite3


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Team Management System")
        self.setMinimumSize(500, 300)
        file_menu = self.menuBar().addMenu("&File")
        help_menu = self.menuBar().addMenu("&Help")
        edit_menu = self.menuBar().addMenu("&Edit")

        add_member_action = QAction(QIcon("icons/add.png"), "Add Member", self)
        add_member_action.triggered.connect(self.insert)
        file_menu.addAction(add_member_action)

        about_action = QAction(QIcon("icons/about.png"), "About", self)
        help_menu.addAction(about_action)

        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_action.triggered.connect(self.search)
        edit_menu.addAction(search_action)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Team", "Email", "Phone"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_member_action)
        toolbar.addAction(search_action)

    def load_data(self):
        connection = sqlite3.connect("database.db")
        result = connection.execute("SELECT * FROM members")
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        query = Query()
        query.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Team Member Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.member_name = QLineEdit()
        self.member_name.setPlaceholderText("Name")
        layout.addWidget(self.member_name)

        self.team_name = QComboBox()
        teams = ["HR", "Marketing", "Sales", "IT", "Engineering"]
        self.team_name.addItems(teams)
        layout.addWidget(self.team_name)

        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")
        layout.addWidget(self.email)

        self.phone = QLineEdit()
        self.phone.setPlaceholderText("Phone")
        layout.addWidget(self.phone)

        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.add_member)
        layout.addWidget(submit_button)
        self.setLayout(layout)

    def add_member(self):
        name = self.member_name.text()
        team = self.team_name.itemText(self.team_name.currentIndex())
        email = self.email.text()
        phone = self.phone.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO members (name, team, email, phone) VALUES (?, ?, ?, ?)",
                       (name, team, email, phone))
        connection.commit()
        cursor.close()
        connection.close()
        team_manager.load_data()


class Query(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search for Team Member")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Enter name of member")
        layout.addWidget(self.search_bar)

        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search)
        layout.addWidget(search_button)
        self.setLayout(layout)

    def search(self):
        name = self.search_bar.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM members WHERE name = ?", (name, ))
        rows = list(result)
        print(rows)
        items = team_manager.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            team_manager.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


app = QApplication(sys.argv)
team_manager = MainWindow()
team_manager.show()
team_manager.load_data()
sys.exit(app.exec())