import MySQLdb

# Conexão e Desconexão com Banco de Dados
def conectar():
    try:
        conn = MySQLdb.connect(
            db = 'booking_manager',
            host = 'localhost',
            user = 'Belgamo',
            password = '1234')
        return conn
    except MySQLdb.Error as e:
        print(f'Erro na conexão do MySQL Server ({e})')

def desconectar(conn):
    if conn:
        conn.close()  