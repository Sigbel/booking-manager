import sys
import sqlite3
import login
from PyQt5.QtWidgets import QApplication, QDateEdit, QListWidget, QMainWindow, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import QDate, QTime
from PyQt5.Qt import Qt
from styles.main_window import *
from datetime import datetime
from modules.cpf_validator import valida_CPF
from modules.email_reserva import reserv_email

class Main_Page(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.setFixedSize(1114,650)
        self.dt = datetime.now()

        # Setar Visibilidade de Labels para False:
        self.set_labels()

        # Criação das tabelas iniciais:
        self.conn = sqlite3.connect('data.db')
        self.curs_or = self.conn.cursor()
        self.curs_or.execute('CREATE TABLE IF NOT EXISTS usuarios ('
                        'id INTEGER,'
                        'usuario TEXT,'
                        'senha TEXT'
                        ')')
        self.curs_or.execute('CREATE TABLE IF NOT EXISTS clientes ('
                        'id INTEGER PRIMARY KEY AUTOINCREMENT,' 
                        'nome TEXT,'
                        'cpf TEXT,'
                        'sobrenome TEXT,'
                        'nascimento TEXT,'
                        'endereço TEXT,'
                        'bairro TEXT,'
                        'cidade TEXT,'
                        'cep TEXT,'
                        'uf TEXT,'
                        'email TEXT,'
                        'telefone TEXT,'
                        'celular TEXT'
                        ')')
        self.curs_or.execute('CREATE TABLE IF NOT EXISTS reservas ('
                        'num_reserva INTEGER PRIMARY KEY AUTOINCREMENT,' 
                        'id INTEGER,'
                        'adultos INTEGER,'
                        'crianças INTEGER,'
                        'diarias INTEGER,'
                        'data_reserva TEXT,'
                        'cliente TEXT,'
                        'sobrenome TEXT,'
                        'cpf TEXT,'
                        'email TEXT,'
                        'celular TEXT,'
                        'forma_pagamento TEXT,'
                        'obs TEXT'
                        ')')
        # self.curs_or.execute('CREATE TABLE IF NOT EXISTS checkin ('
        #                 'num_quarto INTEGER')
        # self.curs_or.execute('CREATE TABLE IF NOT EXISTS checkout ('
        #                 'num_quarto INTEGER')
        self.conn.close()


        # Setar Default Date (Guia Reservas)
        self.date_reserve.setDate(self.dt)

        # Botões Gerais 
        self.btn_home.clicked.connect(lambda: self.seleciona_tab(0))
        self.btn_cliente.clicked.connect(lambda: self.seleciona_tab(1))
        self.btn_reservas.clicked.connect(lambda: self.seleciona_tab(2))
        self.btn_cadastro_h.clicked.connect(lambda: self.seleciona_tab(3))
        self.btn_quartos.clicked.connect(lambda: self.seleciona_tab(4))
        self.btn_checkin.clicked.connect(lambda: self.seleciona_tab(5))
        self.btn_checkout.clicked.connect(lambda: self.seleciona_tab(6))
        self.data_edit.setText(self.dt.strftime('%d/%m/%Y'))
        self.time_edit.setText(self.dt.strftime('%H:%M:%S'))

        # Botões (Cadastro de Hóspedes)
        self.btn_cadastrar_c.clicked.connect(self.insert_client)
        self.btn_clear_all_c.clicked.connect(self.limpa_campos_clientes)

        # # Botões (Reservas)
        self.btn_reservar.clicked.connect(self.insert_reserva)
        self.btn_clear_all_r.clicked.connect(self.limpa_campos_reservas)

        # Botões (Clientes)
        self.table_clients.clicked.connect(self.table_click)
        
        # Botões (CheckIN)
        self.btn_visu_reserv.clicked.connect(lambda: self.verifica_banco_r(2))
        self.btn_checkin_2.clicked.connect(self.do_checkin)

        # Botões (CheckOut)
        # self.btn_saida.clicked.conncet(self.do_checkout)
        
        # Botões (Quartos)
        # Botões (Home)

        # Condições de ativação: Banco não atualiza com app aberto
        if self.tabWidget.currentIndex() == 1:
            self.table_clients.repaint()
            self.consulta_banco()

        # # self.list_q_disp = QListWidget()
        # for c in range(10, 36, 10):
        #     for c1 in range(1, 6):
        #         self.list_q_d_pq.addItem(f'Quarto {c+c1}')
        # for c in range(40, 66, 10):
        #     for c1 in range(1, 6):
        #         self.list_q_d_med.addItem(f'Quarto {c+c1}')
        # for c in range(70, 96, 10):
        #     for c1 in range(1, 6):
        #         self.list_q_d_gran.addItem(f'Quarto {c+c1}')
        # for c1 in range(101, 106):
        #         self.list_q_d_luxo.addItem(f'Quarto {c1}')

    def init_data(self):
        self.conn = sqlite3.connect('data.db')
        self.curs_or = self.conn.cursor()


    def go_login(self):
        login.iniciar()


    def show_popup(self, mode):
        if mode == 'incomp':
            msg = QMessageBox()
            msg.setWindowTitle('Erro!')
            msg.setText('Todos os campos devem ser preenchidos!')
            msg.setIcon(QMessageBox.Warning)
        if mode == 'wrong':
            msg = QMessageBox()
            msg.setWindowTitle('Atenção')
            msg.setText('CPF ou Reserva não encontrado!')
            msg.setIcon(QMessageBox.Information)
        box = msg.exec_()


    def set_labels(self):
        labels = [self.test_cpf, self.test_tel, self.test_cel, self.test_cep]
        for c in labels:
            c.setVisible(False)


    def seleciona_tab(self, value: int):
        self.tabWidget.setCurrentIndex(value)


    def table_click(self):
        self.init_data()

        index = (self.table_clients.selectionModel().currentIndex())
        value1 = index.sibling(index.row(),0).data()
        value2 = index.sibling(index.row(),1).data()
        value3 = index.sibling(index.row(),2).data()

        consulta2 = f'SELECT * FROM clientes WHERE id="{value1}" and nome="{value2}" and cpf="{value3}"'
        linha = self.curs_or.execute(consulta2)

        dados = [linha for linha in self.curs_or.fetchall()]

        self.line_c_name.setText(dados[0][1])   
        self.line_c_cpf.setText(dados[0][2])   
        self.line_c_lastname.setText(dados[0][3])   
        self.line_c_bithd.setText(dados[0][4])   
        self.line_c_adress.setText(dados[0][5])   
        self.line_c_district.setText(dados[0][6])   
        self.line_c_city.setText(dados[0][7])   
        self.line_c_cep.setText(dados[0][8])   
        self.line_c_uf.setText(dados[0][9])   
        self.line_c_email.setText(dados[0][10])   
        self.line_c_phone.setText(dados[0][11])   
        self.line_c_cellphone.setText(dados[0][12])

    def consulta_banco(self):
        self.init_data()

        consulta = 'SELECT * FROM clientes'
        linha = self.curs_or.execute(consulta)
        dados = linha.fetchall()
        self.table_clients.setRowCount(len(dados))
        self.table_clients.setColumnCount(3)

        for c in range(0, len(dados)):
            for c1 in range(0,3):
                self.table_clients.setItem(c, c1, QTableWidgetItem(str(dados[c][c1])))

        self.conn.commit()
        self.conn.close()


    def verifica_banco_r(self, mode): # Bug: Bloquear programa quando não encontra CPF
        self.init_data()

        if mode == 1:
            if self.line_r_cpf != '':
                consulta = 'SELECT * FROM clientes WHERE cpf like ?'
                linha = self.curs_or.execute(consulta, (f'%{self.line_r_cpf.text()}%', ))
                dados = [linha for linha in self.curs_or.fetchall()]

                self.line_r_id.setText(str(dados[0][0]))
                self.line_r_name.setText(dados[0][1])
                self.line_r_lastname.setText(dados[0][2])
                self.line_r_email.setText(dados[0][10])
                self.line_r_cel.setText(dados[0][12])
 

        elif mode == 2:
            if self.line_checkin_cpf.text() != '':
                consulta = 'SELECT * FROM reservas WHERE cpf like ? ORDER BY num_reserva DESC '
                linha = self.curs_or.execute(consulta, (f'%{self.line_checkin_cpf.text()}%', ))
                dados = [linha for linha in self.curs_or.fetchall()]

                if dados == []:
                    self.show_popup('wrong')
                else:
                    self.line_checkin_number.setText(str(dados[0][0]))
            elif self.line_checkin_number.text() != '':
                consulta = 'SELECT * FROM reservas WHERE num_reserva like ? ORDER BY num_reserva DESC '
                linha = self.curs_or.execute(consulta, (f'%{self.line_checkin_number.text()}%', ))
                dados = [linha for linha in self.curs_or.fetchall()]

                if dados == []:
                    self.show_popup('wrong')
                else:
                    self.line_checkin_cpf.setText(str(dados[0][8]))
            else: self.show_popup('wrong')
 
        self.conn.commit()
        self.conn.close()

    def do_checkin(self):
        self.init_data()

        


        self.conn.commit()
        self.conn.close()

    def limpa_campos_reservas(self):
        campos = [self.line_r_name, self.line_r_lastname, self.line_r_cpf, self.line_r_email, 
        self.line_r_cel, self.line_r_id, self.line_obs]

        self.combo_payment.setCurrentIndex(0)
        self.spin_r_totald.setValue(0)
        self.spin_adults.setValue(0)
        self.spin_children.setValue(0)
        self.date_reserve.setDate(self.dt)
        for c2 in campos:
            c2.clear()


    def insert_reserva(self): # Bug: PopUp não verifica caixa de spin
        self.init_data()

        show = False
        campos = [self.line_r_name, self.line_r_lastname, self.line_r_cpf, self.line_r_email, self.line_r_cel]

        date_re = str(self.date_reserve.date().toPyDate())
        for c in campos:
            if (c.text() == '') or (date_re == '3000-01-01'):
                show = True
            else:
                autentica = True
        if show:
            self.show_popup('incomp')
            show = False
            autentica = False

        if autentica:
            self.curs_or.execute('INSERT INTO reservas (id, adultos, crianças, diarias, data_reserva, cliente,'
            'sobrenome, cpf, email, celular, forma_pagamento, obs)' 
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
            (self.line_r_id.text(), self.spin_adults.value(), self.spin_children.value(), self.spin_r_totald.value(),
            str(self.date_reserve.date().toPyDate()), self.line_r_name.text(), self.line_r_lastname.text(), self.line_r_cpf.text(),
            self.line_r_email.text(), self.line_r_cel.text(), self.combo_payment.currentText(), self.line_obs.text()))
            self.conn.commit()

            # Envia E-mail
            consulta = 'SELECT * FROM reservas WHERE cpf like ?'
            linha = self.curs_or.execute(consulta, (f'%{self.line_r_cpf.text()}%', ))

            dados = [linha for linha in self.curs_or.fetchall()]
            reserv_email(f'{dados[0][6]} {dados[0][7]}',dados[0][0])

        self.conn.close()


    def limpa_campos_clientes(self):
        campos = [self.line_name, self.line_lastname, self.line_birth, self.line_cpf, self.line_adress,
        self.line_district, self.line_city, self.line_cep, self.line_email, self.line_tel,
        self.line_cellphone]

        self.combo_uf.setCurrentIndex(0)
        for c1 in campos:
            c1.clear()


    def insert_client(self): # Bug: PopUp não verifica caixa de spin
        self.init_data()

        autentica = False
        if valida_CPF(self.line_cpf.text()) == True:
            autentica = True
            self.test_cpf.setVisible(False)
        else:
            autentica = False
            self.test_cpf.setVisible(True)
        if len(self.line_tel.text()) == 10:
            autentica = True
            self.test_tel.setVisible(False)
        else:
            autentica = False
            self.test_tel.setVisible(True)
        if len(self.line_cellphone.text()) == 11:
            autentica = True
            self.test_cel.setVisible(False)
        else:
            autentica = False
            self.test_cel.setVisible(True)
        if len(self.line_cep.text()) == 8:
            autentica = True
            self.test_cep.setVisible(False)
        else:
            autentica = False
            self.test_cep.setVisible(True)

        # Teste de campos
        show = False
        campos = [self.line_name, self.line_lastname, self.line_cpf, self.line_adress,
            self.line_district,self.line_city, self.line_cep, self.line_email,
            self.line_tel, self.line_cellphone]

        date_bir = str(self.date_birth.date().toPyDate())
        for c in campos:
            if (c.text() == '') or (date_bir == '3000-01-01'):
                show = True
            else:
                autentica = True
        if show:
            self.show_popup('incomp')
            show = False
            autentica = False

        if autentica == True:
            self.curs_or.execute('INSERT INTO clientes (nome, sobrenome, nascimento,'
            'cpf, endereço, bairro, cidade, cep, uf, email, telefone, celular)' 
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
            (self.line_name.text().upper(), self.line_lastname.text().upper(), date_bir,
            self.line_cpf.text(), self.line_adress.text(),self.line_district.text(),self.line_city.text(),
            self.line_cep.text(), self.combo_uf.currentText(), self.line_email.text(),self.line_tel.text(),
            self.line_cellphone.text()))
            self.conn.commit()
   
        self.conn.commit()
        self.conn.close()


    def keyPressEvent(self, event): # Corrigir Bug: - Enter quando apertado sem preencher trás o primeiro nome do banco
        if event.key() == Qt.Key_Enter and self.tabWidget.currentIndex() == 2:
            self.verifica_banco_r(1)
        elif event.key() == Qt.Key_Enter and self.tabWidget.currentIndex() == 5:
            self.verifica_banco_r(2)


if __name__ == '__main__':
    main_page = Main_Page()
    main_page.go_login()
    if login.log_page.aut == True:
        app = QApplication(sys.argv)  
        main_page.show()
        app.exec_() 

