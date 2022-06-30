import re

def valida_CPF(cpf):

    cpf = str(cpf)
    cpf = re.sub(r'[^0-9]', '', cpf)
    if not cpf or len(cpf) != 11:
        return False

    valores_teste_dig = []
    cont1, cont2 = 10, 11
    """ # Verificação de CPF (não obrigatório)
    while not cpf.isnumeric():                      
        cpf = input('O CPF não pode conter ponto ou hífen.\nTente novamente: ')
    while len(cpf) != 11:
        cpf = input('O CPF deve conter 11 números.\nTente novamente: ')"""
    cpf_digitos1 = cpf[:-2]

    # Verifica digito 1
    for c1 in cpf_digitos1:
        valores_teste_dig.append((int(c1)*cont1))
        cont1 -= 1

    teste_digito1 = 11 - (sum(valores_teste_dig) % 11)

    digito1 = 0 if teste_digito1 > 9 else teste_digito1

    valores_teste_dig = []
    cpf_digitos2 = cpf_digitos1 + str(digito1)

    #Verifica digito 2
    for c2 in cpf_digitos2:
        valores_teste_dig.append((int(c2)*cont2))
        cont2 -= 1

    teste_digito2 = 11 - (sum(valores_teste_dig) % 11)

    digito2 = 0 if teste_digito2 > 9 else teste_digito2

    novo_cpf = cpf_digitos2 + str(digito2)
    if novo_cpf == cpf: 
        return True
    else: 
        return False
