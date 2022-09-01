import sys
import login

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
from styles.main_window import *
from datetime import datetime
from modules.cpf_validator import valida_CPF
from modules.email_reserva import reserv_email
from modules.utils import conectar, desconectar, find_cep, verificar_email

class Main_Page(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.setFixedSize(1114,650)
        self.dt = datetime.now()

        # Setar Visibilidade de Labels para False:
        self.set_labels()

        # Criação das tabelas iniciais:
        self.conn = conectar()
        self.curs_or = self.conn.cursor()

        self.curs_or.execute('CREATE TABLE IF NOT EXISTS usuarios ('
                        'id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,'
                        'usuario VARCHAR(50) NOT NULL,'
                        'senha VARCHAR(50) NOT NULL'
                        ')')
        self.curs_or.execute('CREATE TABLE IF NOT EXISTS clientes ('
                        'id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,' 
                        'nome VARCHAR(50) NOT NULL,'
                        'cpf VARCHAR(50) NOT NULL,'
                        'sobrenome VARCHAR(50) NOT NULL,'
                        'nascimento DATE NOT NULL,'
                        'endereço VARCHAR(50) NOT NULL,'
                        'numero VARCHAR(10) NOT NULL,'
                        'bairro VARCHAR(50) NOT NULL,'
                        'cidade VARCHAR(50) NOT NULL,'
                        'cep VARCHAR(50) NOT NULL,'
                        'uf VARCHAR(50) NOT NULL,'
                        'email VARCHAR(50) NOT NULL,'
                        'contato VARCHAR(50) NOT NULL,'
                        'complemento VARCHAR(100) NOT NULL'
                        ')')
        self.curs_or.execute('CREATE TABLE IF NOT EXISTS reservas (' 
                        'id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,' 
                        'adultos INT NOT NULL,'
                        'crianças INT NOT NULL,'
                        'diarias INT NOT NULL,'
                        'data_reserva DATE NOT NULL,'
                        'forma_pagamento VARCHAR(50) NOT NULL,'
                        'obs VARCHAR(200) NOT NULL,'
                        'id_cliente INT NULL,'
                        'FOREIGN KEY (id_cliente) REFERENCES clientes(id)'
                        ')')
        # self.curs_or.execute()
        # self.curs_or.execute()

        desconectar(self.conn)

        # Setar Default Date (Guia Reservas e Clientes)
        self.date_entrada.setDate(self.dt)
        self.date_saida.setDate(self.dt)
        self.date_birth.setDate(self.dt)

        # Botões Gerais 
        self.btn_home.clicked.connect(lambda: self.seleciona_tab(0, 0))
        self.btn_cliente.clicked.connect(lambda: self.seleciona_tab(1, 0))
        self.btn_reservas.clicked.connect(lambda: self.seleciona_tab(2, 0))
        self.btn_cadastro_h.clicked.connect(lambda: self.seleciona_tab(3, 0))
        self.btn_quartos.clicked.connect(lambda: self.seleciona_tab(4, 0))
        self.btn_checkin.clicked.connect(lambda: self.seleciona_tab(5, 0))
        self.btn_checkout.clicked.connect(lambda: self.seleciona_tab(6, 0))
        self.data_edit.setText(self.dt.strftime('%d/%m/%Y'))
        self.time_edit.setText(self.dt.strftime('%H:%M:%S'))

        self.btn_refresh_tab1.clicked.connect(lambda: self.temp_atualiza_banco())
        self.btn_pesq_client.clicked.connect(lambda: self.verifica_banco_r(3))

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

        # Setar tela inicial para guia de clientes
        self.tabWidget.setCurrentIndex(1)
        if self.tabWidget.currentIndex() == 1:
            self.table_clients.repaint()
            self.consulta_banco()

    def go_login(self):
        login.iniciar()

    def keyPressEvent(self, event): # Corrigir Bug: - Enter quando apertado sem preencher trás o primeiro nome do banco
        if (event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return) and self.tabWidget.currentIndex() == 2:
            self.verifica_banco_r(1)
        elif (event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return) and self.tabWidget.currentIndex() == 5:
            self.verifica_banco_r(2)
        elif (event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return) and self.tabWidget.currentIndex() == 1:
            self.verifica_banco_r(3)
        elif (event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return) and self.tabWidget.currentIndex() == 3:
            try: 
                adress = find_cep(self.line_cep.text())
                self.set_adress(adress)
            except:
                self.show_popup(4)

    def show_popup(self, mode):
        msg = QMessageBox()
        if mode == 1:
            msg.setWindowTitle('Erro!')
            msg.setText('Todos os campos devem ser preenchidos!')
            msg.setIcon(QMessageBox.Warning)
        elif mode == 2:
            msg.setWindowTitle('Atenção')
            msg.setText('CPF ou Reserva não encontrado!')
            msg.setIcon(QMessageBox.Information)
        elif mode == 3:
            msg.setWindowTitle('Informação')
            msg.setText('Cliente cadastrado com sucesso!')
            msg.setIcon(QMessageBox.Information)
        elif mode == 4:
            msg.setWindowTitle('Erro')
            msg.setText('CEP não encontrado ou incorreto!')
            msg.setIcon(QMessageBox.Warning)
        elif mode == 5:
            msg.setWindowTitle('Atenção')
            msg.setText('CPF inválido ou já em uso!')
            msg.setIcon(QMessageBox.Information)
        elif mode == 6:
            msg.setWindowTitle('Atenção')
            msg.setText('Email inválido ou já em uso!')
            msg.setIcon(QMessageBox.Information)
        elif mode == 7:
            msg.setWindowTitle('Atenção')
            msg.setText('Telefone para contato inválido ou já em uso !')
            msg.setIcon(QMessageBox.Information)
        elif mode == 8:
            msg.setWindowTitle('Atenção')
            msg.setText('Já existe uma reserva para o cliente informado!')
            msg.setIcon(QMessageBox.Information)
        msg.exec_()

    def set_labels(self):
        labels = [self.test_cpf, self.test_contato, self.test_cep]
        for c in labels:
            c.setVisible(False)

    def seleciona_tab(self, value: int, mode: int):
        self.tabWidget.setCurrentIndex(value)
        if mode == 0:
            pass
        elif mode == 1:
            pass
            
    def table_click(self):
        self.conn = conectar()
        self.curs_or = self.conn.cursor()

        index = (self.table_clients.selectionModel().currentIndex())
        value1 = index.sibling(index.row(),0).data()
        value2 = index.sibling(index.row(),1).data()
        value3 = index.sibling(index.row(),2).data()

        consulta2 = f'SELECT * FROM clientes WHERE id={value1} and nome="{value2}" and cpf="{value3}"'
        self.curs_or.execute(consulta2)
        dados = self.curs_or.fetchall()

        self.line_c_name.setText(dados[0][1])   
        self.line_c_cpf.setText(dados[0][2])   
        self.line_c_lastname.setText(dados[0][3])   
        self.line_c_bithd.setText(str(dados[0][4]))   
        self.line_c_adress.setText(dados[0][5])
        self.line_c_adress_number.setText(dados[0][6])   
        self.line_c_district.setText(dados[0][7])   
        self.line_c_city.setText(dados[0][8])   
        self.line_c_cep.setText(dados[0][9])   
        self.line_c_uf.setText(dados[0][10])   
        self.line_c_email.setText(dados[0][11])   
        self.line_c_phone.setText(dados[0][12])   
        self.line_c_complement.setText(dados[0][13])
        
        desconectar(self.conn)

    def set_adress(self, dados):
        self.line_adress.setText(dados["logradouro"])
        self.line_district.setText(dados["bairro"])
        self.line_city.setText(dados["cidade"])
        self.combo_uf.setCurrentText(dados["uf"])
        self.line_complement.setText(dados["complemento"])

    def temp_atualiza_banco(self):
            self.table_clients.repaint()
            self.consulta_banco()

            self.line_proc_client.clear()

    def consulta_banco(self):
        self.conn = conectar()
        self.curs_or = self.conn.cursor()

        consulta = 'SELECT * FROM clientes'
        self.curs_or.execute(consulta)
        dados = self.curs_or.fetchall()

        self.table_clients.setRowCount(len(dados))
        self.table_clients.setColumnCount(3)

        for c in range(0, len(dados)):
            for c1 in range(0,3):
                self.table_clients.setItem(c, c1, QTableWidgetItem(str(dados[c][c1])))

        self.conn.commit()
        desconectar(self.conn)

    def verifica_banco_r(self, mode): # Bug: Bloquear programa quando não encontra CPF
        self.conn = conectar()
        self.curs_or = self.conn.cursor()

        if mode == 1:
            if self.line_r_cpf.text() != '':
                consulta = f'SELECT * FROM clientes WHERE cpf="{self.line_r_cpf.text()}"'
                self.curs_or.execute(consulta)
                dados = self.curs_or.fetchall()

                self.line_r_name.setText(dados[0][1])
                self.line_r_lastname.setText(dados[0][3])
                self.line_r_email.setText(dados[0][11])
                self.line_r_contato.setText(dados[0][12])
            else: pass

        elif mode == 2:
            if self.line_checkin_cpf.text() != '':
                consulta = f'SELECT * FROM reservas WHERE cpf="{self.line_checkin_cpf.text()}" ORDER BY num_reserva DESC '
                self.curs_or.execute(consulta)
                dados = self.curs_or.fetchall()

                if dados == []:
                    self.show_popup(2)
                else:
                    self.line_checkin_number.setText(str(dados[0][0]))
            elif self.line_checkin_number.text() != '':
                consulta = f'SELECT * FROM reservas WHERE num_reserva={self.line_checkin_number.text()} ORDER BY num_reserva DESC '
                self.curs_or.execute(consulta)
                dados = self.curs_or.fetchall()

                if dados == []:
                    self.show_popup(2)
                else:
                    self.line_checkin_cpf.setText(str(dados[0][8]))
            else: self.show_popup(2)
        
        elif mode == 3:
            if self.line_proc_client.text() != '':
                busca = self.line_proc_client.text()
                nome = ""
                sobrenome = ""

                if len(busca.split()) > 1:
                    nome = busca.split()[0].upper()
                    sobrenome = busca.split()[1].upper()

                consulta = f'SELECT * FROM clientes WHERE id="{busca}" or cpf="{busca}" or (nome="{nome}" and sobrenome="{sobrenome}")'
                self.curs_or.execute(consulta)
                dados = self.curs_or.fetchall()

                self.table_clients.setRowCount(len(dados))
                self.table_clients.setColumnCount(3)

                for c in range(0, len(dados)):
                    for c1 in range(0,3):
                        self.table_clients.setItem(c, c1, QTableWidgetItem(str(dados[c][c1])))
            else: pass   
 
        self.conn.commit()
        desconectar(self.conn)

    def do_checkin(self):
        self.conn = conectar()
        self.curs_or = self.conn.cursor()
        
        self.conn.commit()
        self.desconectar(self.conn)

    def limpa_campos_reservas(self):
        campos = [self.line_r_name, self.line_r_lastname, self.line_r_cpf, self.line_r_email, 
        self.line_r_contato, self.line_obs]

        self.combo_payment.setCurrentIndex(0)
        self.spin_r_totald.setValue(0)
        self.spin_adults.setValue(0)
        self.date_reserve.setDate(self.dt)
        for c2 in campos:
            c2.clear()

    def insert_reserva(self): # Bug: PopUp não verifica caixa de spin
        self.conn = conectar()
        self.curs_or = self.conn.cursor()

        # Definição do campo id_cliente
        self.curs_or.execute(f'SELECT id FROM clientes WHERE cpf="{self.line_r_cpf.text()}"')
        id_data = self.curs_or.fetchall()

        # Teste de campos
        show = False
        campos = [self.line_r_name, self.line_r_lastname, self.line_r_cpf, self.line_r_email, self.line_r_contato]

        date_re = self.date_entrada.dateTime().toString(Qt.ISODate).replace('T', ' ')
        date_sa = self.date_saida.dateTime().toString(Qt.ISODate).replace('T', ' ')

        # Checagens:
            # Campos em Branco 
        for c in campos:
            if (c.text() == ''):
                show = True

        if show:
            self.show_popup(1)
            return

            # Se o cliente já tem reserva em seu nome
        consulta = self.curs_or.execute(f"SELECT * FROM reservas WHERE id_cliente='{id_data[0][0]}'")
        if consulta > 0:
            self.show_popup(8)
            return

        self.curs_or.execute('INSERT INTO reservas ('
            'qtde_pessoas, data_entrada, data_saida, forma_pagamento, obs, id_cliente)' 
            'VALUES (' 
            f'"{self.spin_adults.value()}",'
            f'"{date_re}",' 
            f'"{date_sa}",' 
            f'"{self.combo_payment.currentText()}",' 
            f'"{self.line_obs.text()}",'
            f'"{id_data[0][0]}"'
            ')'
            )

            # Envia E-mail
            # consulta = 'SELECT * FROM reservas WHERE cpf like ?'
            # linha = self.curs_or.execute(consulta, (f'%{self.line_r_cpf.text()}%', ))

            # dados = [linha for linha in self.curs_or.fetchall()]
            # reserv_email(f'{dados[0][6]} {dados[0][7]}',dados[0][0])

        self.conn.commit()
        desconectar(self.conn)

    def limpa_campos_clientes(self):
        campos = [self.line_name, self.line_lastname, self.line_cpf, self.line_adress, self.line_adress_number,
        self.line_district, self.line_city, self.line_cep, self.line_email, self.line_tel]

        self.date_birth.setDate(self.dt)
        self.combo_uf.setCurrentIndex(0)
        for c1 in campos:
            c1.clear()

    def insert_client(self):
        self.conn = conectar()
        self.curs_or = self.conn.cursor()

        if valida_CPF(self.line_cpf.text()) == True:
            self.test_cpf.setVisible(False)
        else:
            self.show_popup(5)
            self.test_cpf.setVisible(True)
            return

        if len(self.line_cep.text()) == 8:
            self.test_cep.setVisible(False)
        else:
            self.show_popup(4)
            self.test_cep.setVisible(True)
            return

        # Teste de campos
        show = False
        campos = [self.line_name, self.line_lastname, self.line_cpf, self.line_adress,
            self.line_district,self.line_city, self.line_cep, self.line_email,
            self.line_tel, self.line_adress_number]

        date_bir = self.date_birth.date().toString(Qt.ISODate)

        # Checagens:
            # Campos em Branco
        for c in campos:
            if (c.text() == '') or (date_bir == self.dt):
                show = True
        
        if show:
            self.show_popup(1)
            return

            # Se o cliente já está cadastrado 
        consulta = self.curs_or.execute(f"SELECT * FROM clientes WHERE cpf='{self.line_cpf.text()}'")
        if consulta > 0:
            self.show_popup(5)
            return

            # Se email já está em uso ou é inválido
        consulta = self.curs_or.execute(f"SELECT * FROM clientes WHERE email='{self.line_email.text()}'")
        if consulta > 0:
            self.show_popup(6)
            return
        if verificar_email(self.line_email.text()) == False:
            self.show_popup(6)
            return

            # Se contato já está em uso ou é inválido
        consulta = self.curs_or.execute(f"SELECT * FROM clientes WHERE contato='{self.line_tel.text()}'")
        if consulta > 0:
            self.show_popup(7)
            return
        if len(self.line_tel.text()) < 10 or len(self.line_tel.text()) > 11:
            self.show_popup(7)
            return

        self.curs_or.execute('INSERT INTO clientes ('
            'nome, sobrenome, nascimento, cpf, endereço, numero, bairro, cidade, cep, uf, email, contato, complemento)' 
            'VALUES ('
            f'"{self.line_name.text().upper()}",' 
            f'"{self.line_lastname.text().upper()}",' 
            f'"{date_bir}",' 
            f'"{self.line_cpf.text()}",'
            f'"{self.line_adress.text()}",'
            f'"{self.line_adress_number.text()}",'
            f'"{self.line_district.text()}",' 
            f'"{self.line_city.text()}",' 
            f'"{self.line_cep.text()}",'
            f'"{self.combo_uf.currentText()}",'
            f'"{self.line_email.text()}",'
            f'"{self.line_tel.text()}",'
            f'"{self.line_complement.text()}"'
            ')'
        )

        self.show_popup(3)
        self.limpa_campos_clientes()
        self.set_labels()
   
        self.conn.commit()
        desconectar(self.conn)


if __name__ == '__main__':
    main_page = Main_Page()
    main_page.go_login()
    if login.log_page.aut == True:
        app = QApplication(sys.argv)  
        main_page.show()
        app.exec_() 

