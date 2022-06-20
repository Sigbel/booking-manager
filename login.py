import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QCoreApplication
from PyQt5.Qt import Qt

from login_window import *
import main
from time import sleep

class LoginPage(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self._aut = False

        self.setFixedSize(689,473)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.conn = sqlite3.connect('data.db')
        self.curs_or = self.conn.cursor()
        self.btn_login.clicked.connect(self.go_mainpage)


    @property
    def aut(self):
        return self._aut


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter:
            self.go_mainpage()


    def go_mainpage(self):
        usuario = self.scr_usuario.text()
        senha = self.scr_senha.text()

        self.curs_or.execute('SELECT * FROM usuarios')
        
        for linha in self.curs_or.fetchall():
            if usuario not in linha:
                print('Usuário ou Senha Incorretos.')
            elif senha not in linha:
                print('Usuário ou Senha Incorretos.')
            else:
                self._aut = True
                print('Login-Bem-Sucedido')
                self.curs_or.close()
                self.conn.close()
                QCoreApplication.quit()


qt = QApplication(sys.argv)
log_page = LoginPage()

def iniciar():
    log_page.show()
    qt.exec_()
    log_page.close()

# def finalizar():
#     if log_page.aut_login == True:
#         sys.exit(qt.exec_())
        
# def finalizar():
#     sys.exit(.exec_())