from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QStatusBar, \
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QComboBox, \
    QToolBar, QGridLayout, QMessageBox
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
import sys
import sqlite3
import qdarktheme


class DatabaseConnection:
    def __init__(self, database_file="database.db"):
        self.database_file = database_file

    def connect(self):
        connection = sqlite3.connect(self.database_file)
        return connection


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
        about_action.triggered.connect(self.about)
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

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.status_bar.removeWidget(child)

        self.status_bar.addWidget(edit_button)
        self.status_bar.addWidget(delete_button)

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()

    def load_data(self):
        connection = DatabaseConnection().connect()
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


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """This app was created during a self study course to practice my skills with object oriented programming and SQLite. Thanks for your interest!"""
        self.setText(content)


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Team Member Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        index = team_manager.table.currentRow()

        self.member_id = team_manager.table.item(index, 0).text()

        c_member_name = team_manager.table.item(index, 1).text()
        self.member_name = QLineEdit(c_member_name)
        self.member_name.setPlaceholderText("Name")
        layout.addWidget(self.member_name)

        c_team_name = team_manager.table.item(index, 2).text()
        self.team_name = QComboBox()
        teams = ["HR", "Marketing", "Sales", "IT", "Engineering"]
        self.team_name.addItems(teams)
        self.team_name.setCurrentText(c_team_name)
        layout.addWidget(self.team_name)

        c_email = team_manager.table.item(index, 3).text()
        self.email = QLineEdit(c_email)
        self.email.setPlaceholderText("Email")
        layout.addWidget(self.email)

        c_phone = team_manager.table.item(index, 4).text()
        self.phone = QLineEdit(c_phone)
        self.phone.setPlaceholderText("Phone")
        layout.addWidget(self.phone)

        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.update)
        layout.addWidget(submit_button)
        self.setLayout(layout)

    def update(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE members SET name = ?, team = ?, email = ?, phone = ? WHERE id = ?",
                       (self.member_name.text(), self.team_name.itemText(self.team_name.currentIndex()),
                        self.email.text(), self.phone.text(), self.member_id))
        connection.commit()
        cursor.close()
        connection.close()
        team_manager.load_data()

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was successfully edited!")
        confirmation_widget.exec()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Team Member Data")

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete this data?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_member)

    def delete_member(self):
        index = team_manager.table.currentRow()
        member_id = team_manager.table.item(index, 0).text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE from members WHERE id = ?", (member_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        team_manager.load_data()

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was successfully deleted!")
        confirmation_widget.exec()

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
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO members (name, team, email, phone) VALUES (?, ?, ?, ?)",
                       (name, team, email, phone))
        connection.commit()
        cursor.close()
        connection.close()
        team_manager.load_data()

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("Member successfully added!")
        confirmation_widget.exec()


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
        connection = DatabaseConnection().connect()
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
qdarktheme.setup_theme()
team_manager = MainWindow()
team_manager.show()
team_manager.load_data()
sys.exit(app.exec())