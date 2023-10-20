import mysql.connector as my
from tkinter import messagebox
import hashlib


con = my.connect(
    host="192.168.1.162",
    user="teste",
    passwd="pass123W."
)
cur = con.cursor()

# criar base de dados se nao existir
sql = "CREATE DATABASE IF NOT EXISTS goaltrack;"
cur.execute(sql)
con.commit()

# Utilizar a base de dados
sql = "USE goaltrack;"
cur.execute(sql)
con.commit()

# Criar a tabela dos utilizadores
sql = """CREATE TABLE IF NOT EXISTS utilizador (
    username VARCHAR(20) PRIMARY KEY,
    email VARCHAR(40) UNIQUE NOT NULL,
    password VARCHAR(120) NOT NULL
);"""
cur.execute(sql)
con.commit()

# criar a tabela dos objectivos
sql = """CREATE TABLE IF NOT EXISTS objectivos (
    nome_objectivo VARCHAR(30) PRIMARY KEY,
    Data_final DATE NOT NULL,
    Data_criaçao DATE NOT NULL,
    Data_realizaçao DATE
);"""
cur.execute(sql)
con.commit()

# cirar a tabela das tarefas
sql = """CREATE TABLE IF NOT EXISTS tarefas (
    nome_tarefa VARCHAR(30) PRIMARY KEY,
    objectivo VARCHAR(30),
    nome_user VARCHAR(20),
    estado VARCHAR(20),
    Data_final DATE NOT NULL,
    Data_criaçao DATE NOT NULL,
    Data_realizaçao DATE,
    Descrição_da_tarefa TEXT(200),
    FOREIGN KEY (objectivo) REFERENCES objectivos(nome_objectivo),
    FOREIGN KEY (nome_user) REFERENCES utilizador(username)
);"""
cur.execute(sql)
con.commit()

resposta = messagebox.askyesno("Exemplos", "Deseja que sejam criados exemplos de objectivos e tarefas para a apliacação")
if resposta:
    ################  Exemplos    ##################
    usernames = ["Pedro", "Marcia", "Bierre"]
    emails = ["pedro@email.com", "marcia@email.com", "bierre@email.com"]
    passwords = ["PasswordP!", "PasswordM!", "PasswordB!"]

    passwords_encriptadas = [hashlib.sha256(password.encode()).hexdigest() for password in passwords]

    for username, email, hashed_password in zip(usernames, emails, passwords_encriptadas):
        cur.execute("INSERT INTO utilizador (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
        con.commit()


    sql = """INSERT INTO objectivos (nome_objectivo, Data_final, Data_criaçao, Data_realizaçao)
             VALUES (%s, %s, %s, %s)"""
    dados_objectivos = [
        ("Limpar A Casa", "2023-09-30", "2023-07-15", "2023-06-28"),
        ("Preparar viagem", "2023-09-30", "2023-07-15", "2023-06-28"),
        ("Acabar a aplicação", "2023-12-31", "2023-07-15", "2023-12-30")]

    cur.executemany(sql, dados_objectivos)
    con.commit()

    sql = """INSERT INTO tarefas (nome_tarefa, objectivo, nome_user, estado, Data_final, Data_criaçao, Data_realizaçao, Descrição_da_tarefa)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
    dados_tarefas = [
        ("Limpar Cozinha", "Limpar A Casa", "Pedro", "Concluído", "2023-08-30", "2023-06-15", "2023-06-28",
         "Lavar e arrumar a loiça, varrer e passar o chão a pano"),
        ("Limpar Sala", "Limpar A Casa", "Marcia", "Em Progresso", "2023-09-15", "2023-06-20", "2023-07-10",
         "Arrumar o que está em cima das mesas, limpar o pó, varrer o chão, passar o chão a pano"),
        ("Limpar Quarto", "Limpar A Casa", None, "Em Progresso", "2023-10-31", "2023-08-01", "2023-08-28",
         "Trocar os lençóis, limpar o pó, arrumar os móveis e varrer o chão"),
        ("Escolher destino", "Preparar viagem", "Pedro", "Pendente", "2023-10-31", "2023-08-01", "2023-08-28",
         "Um destino que seja agradável e não seja caro e que tenha coisas a ver"),
        ("Preparar para arrancar", "Preparar viagem", None, "Pendente", "2023-10-31", "2023-08-01", "2023-08-28",
         "Comprar o voo, marcar o hotel e fazer as malas"),
        ("Criar funcionalidades", "Acabar a aplicação", None, "Pendente", "2023-12-31", "2023-12-01", "2023-12-30",
         "Implementar novas funcionalidades no sistema"),
        ("Criar visual", "Acabar a aplicação", "Pedro", "Pendente", "2023-12-31", "2023-12-01", "2023-12-30",
         "Melhorar a aparência visual da aplicação")]

    cur.executemany(sql, dados_tarefas)
    con.commit()


    messagebox.showinfo("Sucesso", "Base de dados e exemplo criados com sucesso")

else:
    messagebox.showinfo("Sucesso", "Base de dados criada com sucesso")


cur.close()
con.close()
