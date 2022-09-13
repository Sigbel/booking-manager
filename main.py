import sys
import login

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QCheckBox
from PyQt5.QtCore import Qt
from styles.main_window import *
from datetime import date, datetime
from modules.cpf_validator import valida_CPF
from modules.email_reserva import reserv_email
from modules.utils import conectar, desconectar, find_cep, verificar_email
from pandas import date_range

class Main_Page(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.setFixedSize(1114,650)
        self.dt = datetime.now()

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
                        'qtde_pessoas INT NOT NULL,'
                        'data_entrada INT NOT NULL,'
                        'data_saida DATE NOT NULL,'
                        'forma_pagamento VARCHAR(50) NOT NULL,'
                        'obs VARCHAR(200) NOT NULL,'
                        'quarto VARCHAR (5) NOT NULL,'
                        'ativa BOOLEAN NOT NULL,'
                        'id_cliente INT NULL,'
                        'FOREIGN KEY (id_cliente) REFERENCES clientes(id)'
                        ')')

        desconectar(self.conn)
        
        # Setar Visibilidade de Labels para False:
        self.set_labels()

        # Setar Checkboxes (Guia Quartos)
        self.set_checkboxes()

        # Setar tela inicial para guia de clientes
        self.tabWidget.setCurrentIndex(1)
        if self.tabWidget.currentIndex() == 1:
            self.table_clients.repaint()
            self.consulta_banco()

        # Setar Default Date (Guia Reservas e Clientes)
        self.date_entrada.setDate(self.dt)
        self.date_saida.setDate(self.dt)
        self.date_birth.setDate(self.dt)

        # Verificar reservas sem checkin na data de entrada
        self.verifify_perm_inactive()

        # Botões Gerais 
        self.btn_home.clicked.connect(lambda: self.seleciona_tab(0, 0))
        self.btn_cliente.clicked.connect(lambda: self.seleciona_tab(1, 0))
        self.btn_reservas.clicked.connect(lambda: self.seleciona_tab(2, 0))
        self.btn_cadastro_h.clicked.connect(lambda: self.seleciona_tab(3, 0))
        self.btn_quartos.clicked.connect(lambda: self.seleciona_tab(4, 1))
        self.btn_checkin.clicked.connect(lambda: self.seleciona_tab(5, 2))
        self.btn_checkout.clicked.connect(lambda: self.seleciona_tab(6, 0))
        # self.data_edit.setText(self.dt.strftime('%d/%m/%Y'))
        # self.time_edit.setText(self.dt.strftime('%H:%M:%S'))

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
        self.btn_checkin_2.clicked.connect(self.insert_checkin)

        # Botões (CheckOut)
        self.btn_visu_reserv_2.clicked.connect(lambda: self.verifica_banco_r(4))
        self.btn_checkout_2.clicked.connect(self.insert_checkout)

        # Extras (Alterações em QLines e outros Widgets)
        self.line_checkin_cpf.textChanged.connect(lambda: self.change_button(1))
        self.line_checkin_number.textChanged.connect(lambda: self.change_button(1))
        self.line_checkout_number.textChanged.connect(lambda: self.change_active())
        self.line_checkout_cpf.textChanged.connect(lambda: self.change_active())
        self.list_q_d_pq.itemClicked.connect(lambda: self.label_room_click(1))
        self.list_q_d_med.itemClicked.connect(lambda: self.label_room_click(2))
        self.list_q_d_gran.itemClicked.connect(lambda: self.label_room_click(3))
        self.list_q_d_luxo.itemClicked.connect(lambda: self.label_room_click(4))

        # Gravação temporária do status da reserva
        self.temp_reserve_status = False
        self.diarias = 0

    def go_login(self):
        login.iniciar()

    def keyPressEvent(self, event):
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
            msg.exec_()
        elif mode == 2:
            msg.setWindowTitle('Atenção')
            msg.setText('CPF ou Reserva não encontrado!')
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
        elif mode == 3:
            msg.setWindowTitle('Informação')
            msg.setText('Cliente cadastrado com sucesso!')
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
        elif mode == 4:
            msg.setWindowTitle('Erro')
            msg.setText('CEP não encontrado ou incorreto!')
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
        elif mode == 5:
            msg.setWindowTitle('Atenção')
            msg.setText('CPF inválido ou já em uso!')
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
        elif mode == 6:
            msg.setWindowTitle('Atenção')
            msg.setText('Email inválido ou já em uso!')
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
        elif mode == 7:
            msg.setWindowTitle('Atenção')
            msg.setText('Telefone para contato inválido ou já em uso !')
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
        elif mode == 8:
            msg.setWindowTitle('Atenção')
            msg.setText('Já existe uma reserva para o cliente informado!')
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
        elif mode == 9:
            msg.setWindowTitle('Atenção')
            msg.setText('Nenhum quarto disponível para as datas informadas!')
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
        elif mode == 10:
            msg.setWindowTitle('Atenção')
            msg.setText('Número de hóspedes não pode ultrapassar 5!')
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
        elif mode == 11:
            msg.setWindowTitle('Atenção')
            msg.setText('Reserva incluída com sucesso!')
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
        elif mode == 12:
            msg.setWindowTitle('Atenção')
            msg.setText('Datas incorretas!')
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
        elif mode == 13:
            msg.setWindowTitle('Atenção')
            msg.setText('Check-in realizado com sucesso!')
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
        elif mode == 14:
            msg.setWindowTitle('Atenção')
            msg.setText('Check-in já realizado para esta reserva!')
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
        elif mode == 15:
            msg.setWindowTitle('Atenção')
            msg.setText('A data de entrada é anterior a data atual.')
            msg.setInformativeText('Deseja continuar?')
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg.setIcon(QMessageBox.Information)
            return msg.exec_()
        elif mode == 16:
            msg.setWindowTitle('Atenção')
            msg.setText('Reserva permanentemente inativa.')
            msg.setInformativeText('Check-in não feito na data de entrada ou check-out já realizado.')
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
        elif mode == 17:
            msg.setWindowTitle('Atenção')
            msg.setText('Check-out realizado com sucesso!')
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
        elif mode == 18:
            msg.setWindowTitle('Atenção')
            msg.setText('A data de saída é anterior a estipulada na reserva.')
            msg.setInformativeText('Deseja continuar?')
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg.setIcon(QMessageBox.Information)
            return msg.exec_()
        elif mode == 19:
            msg.setWindowTitle('Atenção')
            msg.setText('Check-out já feito para essa reserva ou Check-in não realizado.')
            msg.setIcon(QMessageBox.Information)
            msg.exec_()

    def set_labels(self):
        labels = [self.test_cpf, self.test_contato, self.test_cep]
        for c in labels:
            c.setVisible(False)
    
    def set_checkboxes(self):
        self.conn = conectar()
        self.curs_or = self.conn.cursor()

        consulta = f"""SELECT q.quarto 
	                        FROM reservas AS r, quartos AS q, checkins AS ch
                            WHERE r.id_quarto = q.id and ch.id_reserva = r.id AND r.ativa='1'"""
        self.curs_or.execute(consulta)
        dados = self.curs_or.fetchall()

        for i in dados:
            check = f"self.checkBox_{i[0]}.setChecked(1)"
            exec(check)

        desconectar(self.conn)

    def seleciona_tab(self, value: int, mode: int):
        self.tabWidget.setCurrentIndex(value)
        if mode == 0:
            return
        elif mode == 1:
            self.set_checkboxes()
        elif mode == 2:
            self.verifify_perm_inactive()
            
    def table_click(self):
        self.conn = conectar()
        self.curs_or = self.conn.cursor()

        index = (self.table_clients.selectionModel().currentIndex())
        value1 = index.sibling(index.row(),0).data()
        value2 = index.sibling(index.row(),1).data()
        value3 = index.sibling(index.row(),2).data()

        consulta = f'SELECT * FROM clientes WHERE id={value1} and nome="{value2}" and cpf="{value3}"'
        self.curs_or.execute(consulta)
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

    def label_room_click(self, mode):
        try:
            self.conn = conectar()
            self.curs_or = self.conn.cursor()
            
            if mode == 1:
                temp = self.list_q_d_pq.currentItem().text().split(" ")
            elif mode == 2:
                temp = self.list_q_d_med.currentItem().text().split(" ")
            elif mode == 3:
                temp = self.list_q_d_gran.currentItem().text().split(" ")
            else:
                temp = self.list_q_d_luxo.currentItem().text().split(" ")

            consulta = f"""SELECT c.nome, c.cpf, r.id, r.qtde_pessoas, r.ativa, q.tipo_quarto, q.quarto, r.obs
                                FROM clientes AS c, reservas AS r, quartos AS q
                                WHERE r.id_quarto = q.id AND r.id_cliente = c.id AND r.ativa=1 AND q.quarto={temp[1]}"""
            self.curs_or.execute(consulta)
            dados = self.curs_or.fetchall()

            self.line_q_name.setText(dados[0][0])
            self.line_q_cpf.setText(dados[0][1])
            self.line_q_rnumber.setText(str(dados[0][2]))
            self.line_q_roomtype.setText(dados[0][5])
            self.line_q_pax.setText(str(dados[0][3]))
            self.line_q_obs.setText(dados[0][7])

            desconectar(self.conn)

        except IndexError: 
            dados = [self.line_q_name, self.line_q_cpf, self.line_q_rnumber, self.line_q_roomtype, self.line_q_pax,self.line_q_obs]
            for i in dados:
                i.clear()
            return

    def change_button(self, mode):
        self.btn_checkin_2.setEnabled(0)
        
        if mode == 1:
            dados = [self.line_checkin_cpf_2, self.line_checkin_name, self.line_checkin_lastname, self.line_checkin_email,
            self.line_checkin_contact, self.line_checkin_room, self.line_checkin_room_2, self.line_checkin_roomtype]
            for i in dados:
                i.clear()

    def change_active(self):
        self.temp_reserve_status = False

        dados = [self.line_checkout_name, self.line_checkout_lastname, self.line_checkout_cpf_2, self.line_checkout_email,
        self.line_checkout_contact, self.line_checkout_room, self.line_checkout_room_2, self.line_checkout_roomtype,
        self.line_checkout_reserva_data_e, self.line_checkout_reserva_data_s, self.line_checkout_checkin_id,
        self.line_checkout_checkin_date]
        for i in dados:
            i.clear()

    def verifify_perm_inactive(self):
        self.conn = conectar()
        self.curs_or = self.conn.cursor()

        self.curs_or.execute(f"""UPDATE reservas AS r INNER JOIN quartos AS q
	                                SET r.perm_inativo = "1", q.ignorado = "1"
	                                WHERE r.id_quarto = q.id AND r.ativa = 0 AND q.data_entrada < '{self.dt.strftime("%Y-%m-%d")}' AND perm_inativo = 0""")

        self.conn.commit()
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

    def atualiza_banco(self):
        self.conn = conectar()
        self.curs_or = self.conn.cursor()

        self.conn.commit()

    def verifica_banco_r(self, mode):
        self.conn = conectar()
        self.curs_or = self.conn.cursor()

        self.temp_reserve_status = False

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
            try:
                if self.line_checkin_cpf.text() != '':
                    consulta = self.curs_or.execute(f"""SELECT ch.id, r.id, r.ativa, c.cpf
	                                            FROM reservas AS r, checkins AS ch , clientes AS c
                                                WHERE ch.id_reserva=r.id AND r.ativa=1 AND r.id_cliente=c.id AND c.cpf='{self.line_checkin_cpf.text()}'""")
                    if consulta == 0:
                        self.line_checkin_number.clear()

                        consulta = f"""SELECT r.id, r.qtde_pessoas, r.obs, q.quarto, q.tipo_quarto, c.cpf, c.nome, c.sobrenome, c.email, c.contato, q.data_entrada, q.data_saida
                                            FROM reservas AS r, quartos AS q, clientes AS c
                                            WHERE r.id_quarto=q.id AND r.id_cliente=c.id AND c.cpf={self.line_checkin_cpf.text()} AND r.perm_inativo=0"""
                        self.curs_or.execute(consulta)
                        dados = self.curs_or.fetchall()

                        self.line_checkin_number.setText(str(dados[0][0]))

                        if len(dados) == 0:
                            self.show_popup(2)
                            return
                        else:
                            dados_e_conv = dados[0][10].strftime("%Y-%m-%d")
                            dados_s_conv = dados[0][11].strftime("%Y-%m-%d")

                            self.line_checkin_room.setText("Quarto " + str(dados[0][3]))
                            self.line_checkin_room_2.setText(str(dados[0][1]))
                            self.line_checkin_roomtype.setText(dados[0][4])
                            self.line_checkin_status.setText(dados[0][2])
                            self.line_checkin_name.setText(dados[0][6])
                            self.line_checkin_lastname.setText(dados[0][7])
                            self.line_checkin_email.setText(dados[0][8])
                            self.line_checkin_contact.setText(dados[0][9])
                            self.line_checkin_cpf_2.setText(dados[0][5])
                            self.line_checkin_reserva_data_e.set(dados_e_conv)
                            self.line_checkin_reserva_data_s.set(dados_s_conv)

                        
                        # Verificação da data da reserva
                        consulta = f"""SELECT q.data_entrada
	                                        FROM reservas AS r, quartos AS q, clientes AS c
                                            WHERE r.id_quarto=q.id AND r.id_cliente=c.id AND c.cpf={self.line_checkin_cpf.text()}"""
                        self.curs_or.execute(consulta)
                        dados = self.curs_or.fetchall()

                        dt_init = datetime.now().strftime("%Y-%m-%d")
                        dt_conv = datetime.strptime(dt_init, "%Y-%m-%d")
                        dados_init = dados[0][0].strftime("%Y-%m-%d")
                        dados_conv = datetime.strptime(dados_init, "%Y-%m-%d")

                        if dt_conv < dados_conv:
                            situation = self.show_popup(15)
                            if situation == QMessageBox.Ok:
                                pass
                            else:
                                return

                        self.btn_checkin_2.setEnabled(1)
                    
                    else:
                        self.show_popup(14)
                        return

                elif self.line_checkin_number.text() != '':
                    consulta = self.curs_or.execute(f"""SELECT ch.id, r.id, r.ativa, c.cpf
	                                            FROM reservas AS r, checkins AS ch , clientes AS c
                                                WHERE ch.id_reserva=r.id AND r.ativa=1 AND r.id_cliente=c.id AND r.id='{self.line_checkin_number.text()}'""")
                    if consulta == 0:
                        consulta = f"""SELECT r.id, r.qtde_pessoas, r.obs, q.quarto, q.tipo_quarto, c.cpf, c.nome, c.sobrenome, c.email, c.contato, q.data_entrada, q.data_saida
                                            FROM reservas AS r, quartos AS q, clientes AS c
                                            WHERE r.id_quarto=q.id AND r.id_cliente=c.id AND r.id={self.line_checkin_number.text()} AND r.perm_inativo=0"""
                        self.curs_or.execute(consulta)
                        dados = self.curs_or.fetchall()

                        if len(dados) == 0:
                            self.show_popup(2)
                            return
                        else:
                            dados_e_conv = dados[0][10].strftime("%Y-%m-%d")
                            dados_s_conv = dados[0][11].strftime("%Y-%m-%d")

                            self.line_checkin_room.setText("Quarto " + str(dados[0][3]))
                            self.line_checkin_room_2.setText(str(dados[0][1]))
                            self.line_checkin_roomtype.setText(dados[0][4])
                            self.line_checkin_status.setText(dados[0][2])
                            self.line_checkin_name.setText(dados[0][6])
                            self.line_checkin_lastname.setText(dados[0][7])
                            self.line_checkin_email.setText(dados[0][8])
                            self.line_checkin_contact.setText(dados[0][9])
                            self.line_checkin_cpf_2.setText(dados[0][5])
                            self.line_checkin_reserva_data_e.setText(dados_e_conv)
                            self.line_checkin_reserva_data_s.setText(dados_s_conv)

                       
                        # Verificação da data da reserva
                        consulta = f"""SELECT q.data_entrada
	                                        FROM reservas AS r, quartos AS q
                                            WHERE r.id_quarto=q.id and r.id={self.line_checkin_number.text()}"""
                        self.curs_or.execute(consulta)
                        dados = self.curs_or.fetchall()

                        dt_init = datetime.now().strftime("%Y-%m-%d")
                        dt_conv = datetime.strptime(dt_init, "%Y-%m-%d")
                        dados_init = dados[0][0].strftime("%Y-%m-%d")
                        dados_conv = datetime.strptime(dados_init, "%Y-%m-%d")

                        if dt_conv < dados_conv:
                            situation = self.show_popup(15)
                            if situation == QMessageBox.Ok:
                                pass
                            else:
                                return
                        
                        self.btn_checkin_2.setEnabled(1)
                    
                    else: 
                        self.show_popup(14)
                        return
                else: 
                    self.show_popup(2)
                    return
            
            except:
                self.show_popup(2)
            
                campos = [self.line_checkin_room, self.line_checkin_room_2, self.line_checkin_roomtype, self.line_checkin_status,
                self.line_checkin_number, self.line_checkin_cpf]
                for c1 in campos:
                    c1.clear() 
            
        elif mode == 3:
            if self.line_proc_client.text() != '':
                busca = self.line_proc_client.text()
                nome = ""
                sobrenome = ""

                if len(busca.split()) > 1:
                    nome = busca.split()[0].upper().strip()
                    sobrenome = busca.split()[1].upper().strip()
                    consulta = f'SELECT * FROM clientes WHERE id="{busca}" OR cpf="{busca}" OR (nome="{nome}" and sobrenome="{sobrenome}")'
                else:
                    nome = busca.upper().strip()
                    consulta = f'SELECT * FROM clientes WHERE id="{busca}" OR cpf="{busca}" OR nome = "{nome}"'

                self.curs_or.execute(consulta)
                dados = self.curs_or.fetchall()

                self.table_clients.setRowCount(len(dados))
                self.table_clients.setColumnCount(3)

                for c in range(0, len(dados)):
                    for c1 in range(0,3):
                        self.table_clients.setItem(c, c1, QTableWidgetItem(str(dados[c][c1])))
            else: pass  

        elif mode == 4:
            try:
                if self.line_checkout_cpf.text() != '':
                    consulta = self.curs_or.execute(f"""SELECT ch.id, r.id, r.ativa, c.cpf
	                                            FROM reservas AS r, checkins AS ch , clientes AS c
                                                WHERE ch.id_reserva=r.id AND r.ativa=1 AND r.id_cliente=c.id AND c.cpf='{self.line_checkout_cpf.text()}'""")
                    if consulta != 0:
                        self.line_checkout_number.clear()

                        consulta = f"""SELECT r.id, r.obs, q.quarto, q.tipo_quarto, c.cpf, c.nome, c.sobrenome, c.email, c.contato, ch.id, ch.data_hora_checkin, q.data_entrada, q.data_saida, r.qtde_pessoas
                                            FROM reservas AS r, quartos AS q, clientes AS c, checkins AS ch
                                            WHERE r.id_quarto=q.id AND r.id_cliente=c.id AND ch.id_reserva=r.id AND r.perm_inativo=0 AND c.cpf={self.line_checkout_cpf.text()}"""

                        self.curs_or.execute(consulta)
                        dados = self.curs_or.fetchall()

                        self.line_checkout_number.setText(str(dados[0][0]))

                        if len(dados) == 0:
                            self.show_popup(2)
                            return
                        else:
                            dados_conversao = dados[0][10].strftime("%Y-%m-%d | %H:%M:%S")
                            dados_e_conv = dados[0][11].strftime("%Y-%m-%d")
                            dados_s_conv = dados[0][12].strftime("%Y-%m-%d")

                            self.line_checkout_obs.setText(dados[0][1])
                            self.line_checkout_room.setText("Quarto " + str(dados[0][2]))
                            self.line_checkout_roomtype.setText(dados[0][3])
                            self.line_checkout_cpf_2.setText(dados[0][4])
                            self.line_checkout_name.setText(dados[0][5])
                            self.line_checkout_lastname.setText(dados[0][6])
                            self.line_checkout_email.setText(dados[0][7])
                            self.line_checkout_contact.setText(dados[0][8])
                            self.line_checkout_checkin_id.setText(str(dados[0][9]))
                            self.line_checkout_checkin_date.setText(dados_conversao)
                            self.line_checkout_reserva_data_e.setText(dados_e_conv)
                            self.line_checkout_reserva_data_s.setText(dados_s_conv)
                            self.line_checkout_room_2.setText(str(dados[0][13]))                            
             
                        # Verificação da data de saída
                        consulta = f"""SELECT q.data_saida
	                                        FROM reservas AS r, quartos AS q, clientes AS c
                                            WHERE r.id_quarto=q.id AND r.id_cliente=c.id AND c.cpf={self.line_checkout_cpf.text()}"""
                        self.curs_or.execute(consulta)
                        dados = self.curs_or.fetchall()

                        dt_init = datetime.now().strftime("%Y-%m-%d")
                        dt_conv = datetime.strptime(dt_init, "%Y-%m-%d")
                        dados_init = dados[0][0].strftime("%Y-%m-%d")
                        dados_conv = datetime.strptime(dados_init, "%Y-%m-%d")

                        if dt_conv < dados_conv:
                            situation = self.show_popup(18)
                            if situation == QMessageBox.Ok:
                                self.temp_reserve_status = True
                            else:
                                return

                        self.btn_checkout_2.setEnabled(1)
                    
                    else:
                        self.show_popup(19)
                        return

                elif self.line_checkout_number.text() != '':
                    consulta = self.curs_or.execute(f"""SELECT ch.id, r.id, r.ativa, c.cpf
	                                            FROM reservas AS r, checkins AS ch , clientes AS c
                                                WHERE ch.id_reserva=r.id AND r.ativa=1 AND r.id_cliente=c.id AND r.id='{self.line_checkout_number.text()}'""")
                    
                    if consulta != 0:
                        consulta = f"""SELECT r.id, r.obs, q.quarto, q.tipo_quarto, c.cpf, c.nome, c.sobrenome, c.email, c.contato, ch.id, ch.data_hora_checkin, q.data_entrada, q.data_saida, r.qtde_pessoas
                                            FROM reservas AS r, quartos AS q, clientes AS c, checkins AS ch
                                            WHERE r.id_quarto=q.id AND r.id_cliente=c.id AND ch.id_reserva=r.id AND r.perm_inativo=0 AND r.id={self.line_checkout_number.text()}"""
                        self.curs_or.execute(consulta)
                        dados = self.curs_or.fetchall()

                        if len(dados) == 0:
                            self.show_popup(2)
                            return
                        else:
                            date_checkin1 = dados[0][10].strftime("%Y-%m-%d")
                            date_checkin2 = datetime.strptime(date_checkin1, "%Y-%m-%d")  
                            dt_init = datetime.now().strftime("%Y-%m-%d")
                            dt_conv = datetime.strptime(dt_init, "%Y-%m-%d")
                            self.diarias = len(date_range(date_checkin1, dt_conv))

                            dados_conversao = dados[0][10].strftime("%Y-%m-%d | %H:%M:%S")
                            dados_e_conv = dados[0][11].strftime("%Y-%m-%d")
                            dados_s_conv = dados[0][12].strftime("%Y-%m-%d")

                            self.line_checkout_obs.setText(dados[0][1])
                            self.line_checkout_room.setText("Quarto " + str(dados[0][2]))
                            self.line_checkout_roomtype.setText(dados[0][3])
                            self.line_checkout_cpf_2.setText(dados[0][4])
                            self.line_checkout_name.setText(dados[0][5])
                            self.line_checkout_lastname.setText(dados[0][6])
                            self.line_checkout_email.setText(dados[0][7])
                            self.line_checkout_contact.setText(dados[0][8])
                            self.line_checkout_checkin_id.setText(str(dados[0][9]))
                            self.line_checkout_checkin_date.setText(dados_conversao)
                            self.line_checkout_reserva_data_e.setText(dados_e_conv)
                            self.line_checkout_reserva_data_s.setText(dados_s_conv)
                            self.line_checkout_room_2.setText(str(dados[0][13]))
                            self.line_checkout_dnumber.setText(str(self.diarias))
                       
                        # Verificação da data de saída
                        consulta = f"""SELECT q.data_saida
	                                        FROM reservas AS r, quartos AS q
                                            WHERE r.id_quarto=q.id AND r.id='{self.line_checkout_number.text()}'"""
                        self.curs_or.execute(consulta)
                        dados = self.curs_or.fetchall()

                        dt_init = datetime.now().strftime("%Y-%m-%d")
                        dt_conv = datetime.strptime(dt_init, "%Y-%m-%d")
                        dados_init = dados[0][0].strftime("%Y-%m-%d")
                        dados_conv = datetime.strptime(dados_init, "%Y-%m-%d")

                        if dt_conv < dados_conv:
                            situation = self.show_popup(18)
                            if situation == QMessageBox.Ok:
                                self.temp_reserve_status = True
                            else:
                                return

                        self.btn_checkout_2.setEnabled(1)
                    
                    else:
                        self.show_popup(19)
                        return
                else: 
                    self.show_popup(2)
                    return
            except:
                self.show_popup(2)
            
                campos = [self.line_checkin_room, self.line_checkin_room_2, self.line_checkin_roomtype, self.line_checkin_status,
                self.line_checkin_number, self.line_checkin_cpf]
                for c1 in campos:
                    c1.clear() 
 
        self.conn.commit()
        desconectar(self.conn)

    def insert_checkin(self):
        
        self.conn = conectar()
        self.curs_or = self.conn.cursor()
        
        self.curs_or.execute(f"""INSERT INTO checkins (
                id_reserva, data_hora_checkin)
                VALUES (
                '{self.line_checkin_number.text()}',
                '{datetime.now()}')"""
                )

        self.curs_or.execute(f"""UPDATE reservas
	                                SET ativa='1'
                                    WHERE id={self.line_checkin_number.text()}""")

        self.show_popup(13)
        self.btn_checkin_2.setEnabled(0)

        self.conn.commit()
        desconectar(self.conn)

    def insert_checkout(self):

        self.conn = conectar()
        self.curs_or = self.conn.cursor()

        self.curs_or.execute(f"""INSERT INTO checkouts (
            id_checkin, data_hora_checkout, diarias_cumpridas)
            VALUES (
            '{self.line_checkout_checkin_id.text()}',
            '{datetime.now()}',
            '{self.diarias}')"""
            )
        if self.temp_reserve_status == True:
            self.curs_or.execute(f"""UPDATE reservas AS r INNER JOIN quartos AS q
	                                    SET q.ignorado = "1", r.perm_inativo = "1", ativa = "0"
	                                    WHERE r.id_quarto = q.id AND r.id = {self.line_checkout_number.text()}""")
        else:
            self.curs_or.execute(f"""UPDATE reservas
                                        SET perm_inativo='1', ativa='0'
                                        WHERE id='{self.line_checkout_number.text()}'""")

        self.show_popup(17)
        self.btn_checkout_2.setEnabled(0)

        self.conn.commit()
        desconectar(self.conn)

    def insert_quartos(self, start, end, tipo_quarto):
        """Função para verificar disponibilidade de datas em cada quarto no banco de dados
                start: data de entrada
                end: data de saída
                tipo_quarto: tipo de quarto, baseado na quantidade de hóspedes
        """
        self.conn = conectar()
        self.curs_or = self.conn.cursor()

        quartos_p = (11,12,13,14,15,21,22,23,24,25,31,32,33,34,35)
        quartos_m = (41,42,43,44,45,51,52,53,54,55,61,62,63,64,65)
        quartos_g = (71,72,73,74,75,81,82,83,84,85,91,92,93,94,95)
        quartos_l = (101,102,103,104,105)

        data_gerada = set(date_range(start, end))

        # Consulta ao banco por datas disponíveis
        if tipo_quarto == 'Pequeno':
            contador = quartos_p
        elif tipo_quarto == 'Médio':
            contador = quartos_m
        elif tipo_quarto == 'Grande':
            contador = quartos_g
        else:
            contador = quartos_l

        auxiliar = False
        for i in contador: 
            self.curs_or.execute(f"SELECT quarto, data_entrada, data_saida FROM quartos WHERE tipo_quarto='{tipo_quarto}' and quarto={i} AND ignorado=0")
            consulta = self.curs_or.fetchall()

            valida = False
            if len(consulta) != 0:
                for j in range(len(consulta)):
                    teste = set(date_range(consulta[j][1], consulta[j][2]))

                    if len(teste.intersection(data_gerada)) != 0:
                        valida = False
                        break
                    else:
                        valida = True
            
                if valida: 
                    self.curs_or.execute(f"INSERT INTO quartos ("
                    "tipo_quarto, quarto, data_entrada, data_saida)"
                    "VALUES ("
                    f"'{tipo_quarto}',"
                    f"'{i}',"
                    f"'{start}',"
                    f"'{start}'"
                    ")"
                    )

                    auxiliar = True
                    break
            else: 
                self.curs_or.execute(f"INSERT INTO quartos ("
                "tipo_quarto, quarto, data_entrada, data_saida)"
                "VALUES ("
                f"'{tipo_quarto}',"
                f"'{i}',"
                f"'{start}',"
                f"'{end}'"
                ")"
                )

                auxiliar = True
                break

        if not auxiliar:
            self.show_popup(9)
            return
        
        self.conn.commit()
        desconectar(self.conn)

    def limpa_campos_reservas(self):
        campos = [self.line_r_name, self.line_r_lastname, self.line_r_cpf, self.line_r_email, 
        self.line_r_contato, self.line_obs]

        self.combo_payment.setCurrentIndex(0)
        self.spin_adults.setValue(0)
        self.date_entrada.setDate(self.dt)
        self.date_saida.setDate(self.dt)
        for c2 in campos:
            c2.clear()

    def insert_reserva(self):
        self.conn = conectar()
        self.curs_or = self.conn.cursor()

        # Definição do campo id_cliente
        self.curs_or.execute(f'SELECT id FROM clientes WHERE cpf="{self.line_r_cpf.text()}"')
        id_data = self.curs_or.fetchall()

        # Teste de campos
        show = False
        campos = [self.line_r_name, self.line_r_lastname, self.line_r_cpf, self.line_r_email, self.line_r_contato]

        # Checagens:
            # Campos em Branco 
        for c in campos:
            if (c.text() == ''):
                show = True

        if show:
            self.show_popup(1)
            return

            # Se o cliente já tem reserva em seu nome
        consulta = self.curs_or.execute(f"SELECT * FROM reservas WHERE id_cliente='{id_data[0][0]}' AND perm_inativo=0")
        if consulta != 0:
            self.show_popup(8)
            return

            # Atribuir quarto disponível já verificando as datas
        date_re = datetime.strptime(self.date_entrada.date().toString(Qt.ISODate), "%Y-%m-%d")
        date_sa = datetime.strptime(self.date_saida.date().toString(Qt.ISODate), "%Y-%m-%d")
        dt_init = datetime.now().strftime("%Y-%m-%d")
        dt_conv = datetime.strptime(dt_init, "%Y-%m-%d")

        if date_re < date_re:
            self.show_popup(12)
            return
        
        if date_re < dt_conv or date_sa < dt_conv:
            self.show_popup(12)
            return
        
            # Quantidade de hóspedes
        if self.spin_adults.value() <= 2:
            tipo_quarto = 'Pequeno'
        elif self.spin_adults.value() == 3:
            tipo_quarto = 'Médio'
        elif self.spin_adults.value() == 4:
            tipo_quarto = 'Grande'
        elif self.spin_adults.value() == 5:
            tipo_quarto = 'Luxo'
        else:
            self.show_popup(10)
            return


        self.conn.commit()
        desconectar(self.conn)

        self.insert_quartos(date_re, date_sa, tipo_quarto)

        self.conn = conectar()
        self.curs_or = self.conn.cursor()

        self.curs_or.execute('SELECT id FROM quartos ORDER BY id DESC LIMIT 1')
        id_data2 = self.curs_or.fetchall()

        self.curs_or.execute('INSERT INTO reservas ('
            'qtde_pessoas, forma_pagamento, obs, id_cliente, id_quarto)' 
            'VALUES (' 
            f'"{self.spin_adults.value()}",'
            f'"{self.combo_payment.currentText()}",' 
            f'"{self.line_obs.text()}",'
            f'"{id_data[0][0]}",'
            f'"{id_data2[0][0]}"'
            ')'
            )

        self.show_popup(11)
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

