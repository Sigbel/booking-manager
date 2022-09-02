import MySQLdb
import pycep_correios
import re
import datetime
from pandas import date_range

# Conexão e Desconexão com Banco de Dados
def conectar():
    try:
        conn = MySQLdb.connect(
            db = 'booking_manager',
            host = 'localhost',
            user = 'belgamo',
            password = '123')
        return conn
    except MySQLdb.Error as e:
        print(f'Erro na conexão do MySQL Server ({e})')

def desconectar(conn):
    if conn:
        conn.close()  

# Busca de logradouro através do CEP
def find_cep(cep: str):
    """Função para encontrar logradouro a partir do CEP"""
    try:
        adress = pycep_correios.get_address_from_cep(cep)

        return adress
    
    except pycep_correios.exceptions.InvalidCEP as eic:
        print(f"O CEP digitado é inválido ({eic})")
    except pycep_correios.exceptions.CEPNotFound as ecnf:
        print(f"O CEP digitado não foi encontrado ({ecnf})")
    except pycep_correios.exceptions.ConnectionError as errc:
        print(f"Erro de conexão ({errc})")
    except pycep_correios.exceptions.Timeout as errt:
        print(f"Tempo de conexão atingido ({errt})")
    except pycep_correios.exceptions.HTTPError as errh:
        print(f"Erro de HTTP ({errh})")
    except pycep_correios.exceptions.BaseException as e:
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

# Verificação de Range de Datas
def range_dates(start: str, end: str):
    """Função para verificar disponibilidade de reservas no banco de dados
            start: data de entrada
            end: data de saída
    """
    conn = conectar()
    curs_or = conn.cursor()
    
    c = datetime.datetime.strptime(start, "%d-%m-%Y")
    f = datetime.datetime.strptime(end, "%d-%m-%Y")

    data_gerada = date_range(c, f)
    
    conn.commit()
    desconectar(conn)
    





