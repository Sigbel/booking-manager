import pymysql
pymysql.install_as_MySQLdb()

import brazilcep
import re
import datetime
from pandas import date_range

# Conexão e Desconexão com Banco de Dados
database='booking_manager'
_user='root'
_password='123'
def init_configurations(_user, _password):
    try:
        conn = pymysql.connect(
            host = 'localhost',
            user = _user,
            password = _password)
        return conn
    except pymysql.Error as e:
        print(f'Erro na conexão do MySQL Server ({e})')

def conectar(datab, _user, _password):
    try:
        conn = pymysql.connect(
            db = datab,
            host = 'localhost',
            user = _user,
            password = _password)
        return conn
    except pymysql.Error as e:
        print(f'Erro na conexão do MySQL Server ({e})')

def desconectar(conn):
    if conn:
        conn.close()  

# Busca de logradouro através do CEP
def find_cep(cep: str):
    """Função para encontrar logradouro a partir do CEP"""
    try:
        adress = brazilcep.get_address_from_cep(cep)

        return adress
    
    except brazilcep.exceptions.InvalidCEP as eic:
        print(f"O CEP digitado é inválido ({eic})")
    except brazilcep.exceptions.CEPNotFound as ecnf:
        print(f"O CEP digitado não foi encontrado ({ecnf})")
    except brazilcep.exceptions.ConnectionError as errc:
        print(f"Erro de conexão ({errc})")
    except brazilcep.exceptions.Timeout as errt:
        print(f"Tempo de conexão atingido ({errt})")
    except brazilcep.exceptions.HTTPError as errh:
        print(f"Erro de HTTP ({errh})")
    except brazilcep.exceptions.BaseException as e:
        print(f"Erro na base de dados ({e})")

# Verificar emails
pattern = "^[A-Za-z0-9]+[\._]?[A-Za-z0-9]+[@]\w+[.]\w{2,3}$"
def verificar_email(email: str):
    """Função para verificar se emails são válidos"""
    verify = re.search(pattern, email)

    if verify:
        return True
    else:
        return False


        