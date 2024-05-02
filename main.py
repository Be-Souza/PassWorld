import sqlite3
import os
import time
from cryptography.fernet import Fernet
import string
import random

####LIDAR COM A CHAVE DE CRIPTOGRAFIA---------------------------------------------------------------------------------------------------

conn = sqlite3.connect('passworld.db')

cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS chaves (
    id INTEGER PRIMARY KEY,
    chave TEXT NOT NULL
)
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS SENHAS_SITES (
        id INTEGER PRIMARY KEY,
        site TEXT NOT NULL,
        usuario TEXT NOT NULL,
        senha TEXT NOT NULL,
        user_id INTEGER NOT NULL

    )
    ''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY,
        user TEXT NOT NULL,
        senha TEXT NOT NULL
    )
    ''')

conn.commit()

conn.close()

def carregarChaveDoBanco():
    conn = sqlite3.connect('passworld.db')
    cursor = conn.cursor()
    cursor.execute("SELECT chave FROM chaves ORDER BY id DESC LIMIT 1")
    chave = cursor.fetchone()
    conn.close()
    return chave[0] if chave else None

# Tentar carregar a chave do banco de dados
chave = carregarChaveDoBanco()

# Se a chave não foi encontrada no banco de dados, gerar uma nova chave
if chave is None:
    print("Chave Fernet não encontrada no banco de dados. Gerando uma nova chave...")
    chave = Fernet.generate_key()
    
    # Inserir a nova chave no banco de dados
    conn = sqlite3.connect('passworld.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chaves (chave) VALUES (?)", (chave,))
    conn.commit()
    conn.close()

# Inicializar o objeto Fernet com a chave carregada
chaveFernet = Fernet(chave)

# Gerar uma chave de criptografia
def gerar_chave():
    return Fernet.generate_key()

# Inicializar o objeto Fernet com a chave gerada
def inicializar_fernet(chave):
    return Fernet(chave)

# Criar uma tabela para armazenar as senhas se ela não existir
def criar_tabela(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS SENHAS_SITES (
        id INTEGER PRIMARY KEY,
        site TEXT NOT NULL,
        usuario TEXT NOT NULL,
        senha TEXT NOT NULL,
        user_id INTEGER NOT NULL
    )
    ''')


# Criptografar a senha
def criptografar_senha(fernet, senha):
    return fernet.encrypt(senha.encode())

# Descriptografar a senha
def descriptografar_senha(fernet, senha_criptografada):
    return fernet.decrypt(senha_criptografada).decode()

def inserirChaveNoBanco(chave):
    conn = sqlite3.connect('passworld.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chaves (chave) VALUES (?)", (chave,))
    conn.commit()
    conn.close()

def recuperarChaveDoBanco():
    conn = sqlite3.connect('passworld.db')
    cursor = conn.cursor()
    cursor.execute("SELECT chave FROM chaves ORDER BY id DESC LIMIT 1")
    chave = cursor.fetchone()
    conn.close()
    return chave[0] if chave else None

####FIM CHAVE CRIPTOGRAFIA BANCO DE DADOS-----------------------------------------------------------------------------------------------

def verificarUsuarioExistente(usuario):
    conn = sqlite3.connect('passworld.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()

    for user in usuarios:
        if usuario == user[0]:
            return True
    
    return False

def criarUsuario(fernet):
    
    limparTerminal()
    print("Bem vindo ao menu de criação de usuário!\n")

    # Conectar ao banco de dados SQLite
    conn = sqlite3.connect('passworld.db')

    # Criar um cursor para executar comandos SQL
    cursor = conn.cursor()

    # Criar uma tabela
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY,
        user TEXT NOT NULL,
        senha TEXT NOT NULL
    )
    ''')

    while True:
        user = input("Insira o nome de usuário a ser criado: ")
        if verificarUsuarioExistente(user):
            print("Esse usuário já existe. Por favor, escolha outro.")
        else:
            break
    
    senha = input("Insira a senha do usuário:")

    guardarInfo = 'INSERT INTO usuarios (user, senha) VALUES (?, ?)'

    senhaAppCript = criptografar_senha(fernet, senha)

    cursor.execute(guardarInfo,(user, senhaAppCript))

    conn.commit()
    conn.close()

def limparTerminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def login(fernet):

    limparTerminal()
    usuarioEntrou = False

    while not usuarioEntrou:
        
        userGerenciador = input("Usuário: ")
        senhaGerenciador = input("Senha: ")
        usuarioEntrou = verificarCredenciais(userGerenciador, senhaGerenciador)
        
        conn = sqlite3.connect('passworld.db')
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM usuarios WHERE user= ?', (userGerenciador,))
        global idUsuario
        id_usuario = cursor.fetchone()

    if id_usuario:
        idUsuario = id_usuario[0]
        print(f"O id do usuario é: {idUsuario}")
    else:
        print("Usuário não encontrado.")

        print(f"O id do usuario é: {idUsuario}")

        if usuarioEntrou:
            print("Inicializando...")
        else:
            print("Por favor, tente novamente!")
    print("Seja bem vindo ao PassWorld!")
    time.sleep(1)
    limparTerminal()

    print(f"Bem vindo {userGerenciador}!")

def verificarCredenciais(usuario, senha):
    
    conn = sqlite3.connect('passworld.db')

    cursor = conn.cursor()

    # Buscar no banco de dados, tal usuário

    cursor.execute('SELECT senha FROM usuarios WHERE user=?', (usuario,))
    deuCerto = cursor.fetchone()

    conn.close()    

    if deuCerto:
        senhaDoBanco = deuCerto[0]

        # Se a senha não estiver vazia, descriptografa e compara com a senha digitada
        if senhaDoBanco:
            senhaDecript = descriptografar_senha(chaveFernet, senhaDoBanco)

            if senhaDecript == senha:
                limparTerminal()
                print("Acesso concedido!")
                return True
            else:
                limparTerminal()
                print("Acesso negado.")
        else:
            limparTerminal()
            print("Usuário não encontrado ou senha não configurada.")
    else:
        limparTerminal()
        print("Usuário não encontrado.")

    return False



def printaTela():
    print("O que você deseja fazer?")
    print("\n")
    print("1. Listar senhas")
    print("2. Inserir nova senha")
    print("3. Excluir uma senha")
    print("4. Gerador de senhas") 
    print("5. Trocar/Criar Usuário")
    print("6. Sair")

####COMEÇO OFICIAL DO PROGRAMA-------------------------------------------------------------------------------------

def telaInicial():
    logou = False

    while not logou:

        conn = sqlite3.connect('passworld.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT COUNT(user) FROM usuarios''')
        temUserLoginCriado = cursor.fetchone()

        if temUserLoginCriado[0] > 0:
            print("Bem vindo ao PassWorld!\n")
            print("O que você deseja fazer?\n")
            print("------------------------\n")
            print("1. Entrar no PassWorld")
            print("2. Criar uma conta PassWorld")
            escolhaTelaInicial = input("\nDigite o número referente a opção desejada: ")

            if escolhaTelaInicial == '1':
                login(chaveFernet)
                logou = True
            elif escolhaTelaInicial == '2':
                criarUsuario(chaveFernet)
            else:
                limparTerminal()
                print("Opção inválida digitada, tente novamente.")

        else:
            print("Seja bem vindo ao PassWorld!")
            print("Você será redirecionado para o menu de criação de contas em breve")
            time.sleep(2)
            criarUsuario(chaveFernet)



usandoPrograma = True

####DEFINIÇÃO DE ESCOLHAS (cada um é uma função dentro do programa) -----------------------------------------

def insereSenha(fernet, id_usuario):
    limparTerminal()
    conn = sqlite3.connect('passworld.db')
    cursor = conn.cursor()
    criar_tabela(cursor)
    armazenaSite = input("Digite o SITE ou SERVIÇO para qual você deseja cadastrar uma senha: ")
    armazenaUser = input(f"Digite o USUÁRIO que será usado no site/serviço {armazenaSite}: ")
    armazenaSenha = input(f"Digite a SENHA que será usada no site/serviço ou digite -auto- para\nsenha automática: ")

    if armazenaSenha == 'auto':
        senhaAuto = gerarSenha()
        print(f"A senha gerada e cadastrada automaticamente é: {senhaAuto}")
        senha_criptografada = criptografar_senha(fernet, senhaAuto)
        cursor.execute("INSERT INTO SENHAS_SITES (site, usuario, senha, user_id) VALUES (?, ?, ?, ?)", (armazenaSite, armazenaUser, senha_criptografada, id_usuario))
        conn.commit()
        conn.close()
    else:
        senha_criptografada = criptografar_senha(fernet, armazenaSenha)
        cursor.execute("INSERT INTO SENHAS_SITES (site, usuario, senha, user_id) VALUES (?, ?, ?, ?)", (armazenaSite, armazenaUser, senha_criptografada, id_usuario))
        conn.commit()
        conn.close()

def listarSenhas(fernet, id_usuario):
    limparTerminal()
    conn = sqlite3.connect('passworld.db')
    cursor = conn.cursor()
    cursor.execute("SELECT site, usuario, senha FROM SENHAS_SITES WHERE user_id=?", (id_usuario,))
    senhas = cursor.fetchall()
    conn.close()

    print("Senhas armazenadas:")
    for site, usuario, senha_criptografada in senhas:
        senha_descriptografada = descriptografar_senha(fernet, senha_criptografada)
        print(f"Site: {site} \nUsuário: {usuario} \nSenha: {senha_descriptografada} \n")

def excluirSenha(id_usuario):
    limparTerminal()
    conn = sqlite3.connect('passworld.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, site, usuario FROM SENHAS_SITES WHERE user_id=?", (id_usuario,))
    senhas = cursor.fetchall()
    conn.close()

    print("Senhas armazenadas:")
    for id, site, usuario in senhas:
        print(f"ID: {id}, Site: {site}, Usuário: {usuario}")

    id_excluir = input("Digite o ID da senha que deseja excluir (ou 'cancelar' para voltar): ")
    limparTerminal()
    if id_excluir.lower() == 'cancelar':
        return

    conn = sqlite3.connect('passworld.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM SENHAS_SITES WHERE id=?", (id_excluir,))
    idSenhaExcluir = cursor.fetchone()[0]
    conn.commit()
    conn.close()

    try:
        id_excluir = int(id_excluir)
    except ValueError:
        print("Entrada inválida. Por favor, digite o ID numérico da senha que deseja excluir.")
        return
    if idSenhaExcluir == idUsuario:
        conn = sqlite3.connect('passworld.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM SENHAS_SITES WHERE id=?", (id_excluir,))
        conn.commit()
        conn.close()
        print("Senha excluída com sucesso.")
    else:
        print("Essa senha não foi cadastrada por você, acesso negado!")


def gerarSenha(comprimento=24):
    caracteres = string.ascii_letters + string.digits + string.punctuation
    senha = ''.join(random.choice(caracteres) for _ in range(comprimento))
    return senha

def mostraCripto(id_usuario):
        conn = sqlite3.connect('passworld.db')
        cursor = conn.cursor()
        cursor.execute("SELECT senha FROM SENHAS_SITES WHERE user_id= ?", (id_usuario,))
        conn.commit()
        senhasShowCripto = cursor.fetchall()
        print(f"{senhasShowCripto}")
        conn.close()
    

####DEFINIÇÃO DE ESCOLHAS (cada um é uma função dentro do programa) -----------------------------------------

telaInicial()

while usandoPrograma:
    printaTela()
    escolhaTela = input("\nDigite o número referente a opção desejada: ")
    if escolhaTela == '1':
        listarSenhas(chaveFernet, idUsuario)
    elif escolhaTela == '2':
        insereSenha(chaveFernet, idUsuario)
    elif escolhaTela == '3':
        excluirSenha(idUsuario)
    elif escolhaTela == '4':
        limparTerminal()
        senhaGerada = gerarSenha()
        print('A senha gerada foi: ', senhaGerada)
    elif escolhaTela == '5':
        telaInicial()
    elif escolhaTela == '6':
        usandoPrograma = False
    elif escolhaTela == '9':
        mostraCripto(idUsuario)
