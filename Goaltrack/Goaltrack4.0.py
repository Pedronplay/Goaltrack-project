from tkinter import *
from tkinter import ttk, messagebox
import mysql.connector as my
from PIL import ImageTk, Image
import hashlib
from datetime import date

# Dados que nao vão variar durante a utilizaçao
hoje = date.today()
dias = [str(day) for day in range(1, 32)]
meses = [
    'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
    'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
anos = [str(year) for year in range(2023, 2031)]


# funcões
def goaltrack(user_sessao):
    def criar_frame_objectivo(objectivo_escolhido):
        def criar_tarefa():
            def criar_nova_tarefa():
                data_fim = (combo_ano_tar.get(), combo_mes_tar.get(), combo_dia_tar.get())
                mensagemvalidacao = valida_data(*data_fim)
                string_data = f"{data_fim[0]}-{meses.index(data_fim[1]) + 1}-{data_fim[2]}"  # string para dar para inserir no sql
                if mensagemvalidacao:
                    messagebox.showerror("Erro de validação da data", mensagemvalidacao)
                    data_check = False
                else:
                    data_check = True
                if data_check and len(entry_criar_n_tarefa.get()) > 0 and len(
                        textbox_descricao_tar.get('1.0', END)) > 0:
                    sql = """INSERT INTO tarefas (nome_tarefa, objectivo, nome_user, estado, Data_final, Data_criaçao, Data_realizaçao, Descrição_da_tarefa)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                    dados_tarefas = [(entry_criar_n_tarefa.get(), objectivo_escolhido, None, "Pendente",
                                      string_data, str(hoje), None, textbox_descricao_tar.get('1.0', END))]
                    cur.executemany(sql, dados_tarefas)
                    con.commit()
                    messagebox.showinfo("Tarefa adicionada",
                                        f"A tarefa {entry_criar_n_tarefa.get()}\n foi criada com sucesso")
                    criar_frame_objectivo(objectivo_escolhido)
                    update_aplica_alteracoes()
                    criar_tarefa.destroy()

            criar_tarefa = Toplevel()
            criar_tarefa.overrideredirect(True)
            criar_tarefa.geometry(f"500x400+400+200")  # adjust the geometry as per your requirements
            criar_tarefa.configure(background="#9933FF")
            criar_tarefa.bind("<Escape>", lambda event: criar_tarefa.destroy())
            # criar_tarefa.attributes("-topmost", True)

            # Widgets
            label_criar_n_tarefa = Label(criar_tarefa, text="Criar Nome da tarefa: ", background="#4C0099",
                                         foreground="gold", font=('Arial BOLD', 16))
            entry_criar_n_tarefa = Entry(criar_tarefa, font=('Arial BOLD', 14), background="#4C0099",
                                         relief="sunken", borderwidth=3, foreground="gold")
            label_criar_data_limite = Label(criar_tarefa, text="Data Limite:", background="#4C0099",
                                            foreground="gold", font=('Arial BOLD', 16))
            combo_ano_tar = ttk.Combobox(criar_tarefa, values=anos, state="readonly", width=4,
                                         font=("Segoe UI", 14, "bold"))
            combo_ano_tar.current(0)
            combo_mes_tar = ttk.Combobox(criar_tarefa, values=meses, state="readonly", width=9,
                                         font=("Segoe UI", 14, "bold"))
            combo_mes_tar.current(0)
            combo_dia_tar = ttk.Combobox(criar_tarefa, values=dias, state="readonly", width=4,
                                         font=("Segoe UI", 14, "bold"))
            combo_dia_tar.current(0)
            label_criar_descricao_tarefa = Label(criar_tarefa, text="Descrição da tarefa:", background="#4C0099",
                                                 foreground="gold", font=('Arial BOLD', 18))
            textbox_descricao_tar = Text(criar_tarefa, height=5, width=30, font=('Arial BOLD', 14),
                                         background="#4C0099",
                                         relief="sunken", borderwidth=3, foreground="gold")
            butao_criar_tarefa = Button(criar_tarefa, text="Criar Tarefa", command=criar_nova_tarefa, bg="#4B0082",
                                        activebackground="#FFD700", relief="raised", borderwidth=6,
                                        foreground="#FFD700",
                                        font=("Segoe UI", 12, "bold"))
            butao_voltar = Button(criar_tarefa, text="Voltar", command=criar_tarefa.destroy, background="RED",
                                  relief="raised", borderwidth=3, font=("Segoe UI", 12, "bold"))

            # Layout
            label_criar_n_tarefa.place(relx=0.02, rely=0.05, anchor="w")
            entry_criar_n_tarefa.place(relx=0.46, rely=0.05, anchor="w")
            label_criar_data_limite.place(relx=0.02, rely=0.19, anchor="w")
            combo_ano_tar.place(relx=0.40, rely=0.2, anchor="w")
            combo_mes_tar.place(relx=0.55, rely=0.2, anchor="w")
            combo_dia_tar.place(relx=0.78, rely=0.2, anchor="w")
            label_criar_descricao_tarefa.place(relx=0.02, rely=0.33, anchor="w")
            textbox_descricao_tar.place(relx=0.02, rely=0.55, anchor="w", relwidth=0.96, relheight=0.35)
            butao_criar_tarefa.place(relx=0.02, rely=0.8, anchor="w", relwidth=0.96)
            butao_voltar.place(relx=0.02, rely=0.95, anchor="w", relwidth=0.96)

            criar_tarefa.mainloop()

        def editar_tarefa(tarefa_id):
            def novo_nome():
                resposta = messagebox.askyesno("Confirmação", f"Tem certeza de que deseja alterar o nome de{tarefa_id} "
                                                              f",para {entry_alterar_n_tarefa.get()} ")
                if resposta and entry_alterar_n_tarefa.get():
                    sql = f"""UPDATE tarefas SET nome_tarefa = '{entry_alterar_n_tarefa.get()}' WHERE nome_tarefa = '{tarefa_id}';"""
                    cur.execute(sql)
                    con.commit()
                    messagebox.showinfo("Exclusão", "Nome da tarefa alterado com sucesso.")
                    update_aplica_alteracoes()
                    criar_frame_objectivo(objectivo_escolhido)  # chama a funçao e actualiza a janela
                else:
                    messagebox.showinfo("Alteração cancelada", "A alteração foi cancelada.")

            def atribuir_outro_user():
                resposta = messagebox.askyesno("Confirmação", f"Tem certeza de que deseja atribuir esta tarefa ao user "
                                                              f"{combo_user_atribuido.get()}")
                if resposta and combo_user_atribuido.get():
                    sql = f"UPDATE tarefas SET nome_user = '{combo_user_atribuido.get()}' WHERE nome_tarefa = '{tarefa_id}';"
                    cur.execute(sql)
                    con.commit()
                    messagebox.showinfo("Exclusão", "User atribuido com sucesso.")
                    update_aplica_alteracoes()
                    criar_frame_objectivo(objectivo_escolhido)
                else:
                    messagebox.showinfo("Alteração cancelada", "A alteração foi cancelada.")

            def nova_data():
                data_fim = (combo_ano_tar.get(), combo_mes_tar.get(), combo_dia_tar.get())
                mensagemvalidacao = valida_data(
                    *data_fim)  # o * serve para desempacotar o tuplo para irem os 3 parametros para a funçao
                if mensagemvalidacao:
                    messagebox.showerror("Erro de validação da data", mensagemvalidacao)
                else:
                    resposta = messagebox.askyesno("Confirmação",
                                                   f"Tem certeza de que deseja alterar a data limite para:"
                                                   f"{combo_dia_tar.get()} de {combo_mes_tar.get()} de {combo_ano_tar.get()} ")
                    string_data = f"{data_fim[0]}-{meses.index(data_fim[1]) + 1}-{data_fim[2]}"

                    if resposta and len(entry_alterar_n_tarefa.get()) > 0:
                        sql = f"""UPDATE tarefas SET Data_final = '{string_data}',
                                estado = 'Pendente' WHERE nome_tarefa = '{tarefa_id}';"""
                        cur.execute(sql)
                        con.commit()
                        messagebox.showinfo("Exclusão", "Data limite alterada com sucesso.")
                        update_aplica_alteracoes()
                        criar_frame_objectivo(objectivo_escolhido)
                    else:
                        messagebox.showinfo("Alteração cancelada", "A alteração foi cancelada.")

            def nova_descricao():
                resposta = messagebox.askyesno("Confirmação", f"Tem certeza de que deseja alter a descrição da tarefa")
                if resposta and len(textbox_descricao_tar.get(1.0, END)) > 0:
                    sql = f"UPDATE tarefas SET Descrição_da_tarefa = '{textbox_descricao_tar.get('1.0', END)}' WHERE nome_tarefa = '{tarefa_id}';"
                    cur.execute(sql)
                    con.commit()
                    messagebox.showinfo("Exclusão", "Descriçao alterada com sucesso.")
                    update_aplica_alteracoes()
                    criar_frame_objectivo(objectivo_escolhido)
                else:
                    messagebox.showinfo("Alteração cancelada", "A alteração foi cancelada.")

            editar_tarefa = Toplevel()
            editar_tarefa.overrideredirect(True)
            editar_tarefa.geometry(f"550x420+400+200")  # ao meter no goal track alterar para centrar na janela
            editar_tarefa.configure(background="#9933FF")
            editar_tarefa.bind("<Escape>", lambda event: editar_tarefa.destroy())
            # editar_tarefa.attributes("-topmost", True)

            sql = f"SELECT nome_user, estado, data_final, descrição_da_tarefa FROM tarefas WHERE nome_tarefa = '{tarefa_id}'"
            cur.execute(sql)
            tarefas = cur.fetchall()
            sql = f"SELECT username FROM utilizador"
            cur.execute(sql)
            usersdisponiveis = cur.fetchall()

            # widgets
            label_alterar_n_tarefa = Label(editar_tarefa, text="Alterar Nome da tarefa:", background="#4C0099",
                                           foreground="gold", font=('Arial BOLD', 16))
            entry_alterar_n_tarefa = Entry(editar_tarefa, font=('Arial BOLD', 14), background="#4C0099",
                                           relief="sunken", borderwidth=3, foreground="gold")
            entry_alterar_n_tarefa.insert(0, tarefa_id)
            butao_confirma_alterar_nome = Button(editar_tarefa, text="Alterar Nome", command=novo_nome, bg="#4B0082",
                                                 activebackground="#FFD700", relief="raised", foreground="#FFD700",
                                                 font=("Segoe UI", 10, "bold"), borderwidth=6)
            label_atribuir_a = Label(editar_tarefa, text="Atribuir tarefa a:", background="#4C0099", foreground="gold",
                                     font=('Arial BOLD', 16))
            combo_user_atribuido = ttk.Combobox(editar_tarefa, values=usersdisponiveis, state="readonly", width=20,
                                                font=("Segoe UI", 14, "bold"))
            butao_atribuir = Button(editar_tarefa, text="Atribuir Tarefa", command=atribuir_outro_user, bg="#4B0082",
                                    activebackground="#FFD700", relief="raised", foreground="#FFD700",
                                    font=("Segoe UI", 10, "bold"), borderwidth=6)
            label_alterar_data_limite = Label(editar_tarefa, text="Alterar Data Limite", background="#4C0099",
                                              foreground="gold", font=('Arial BOLD', 16))
            combo_ano_tar = ttk.Combobox(editar_tarefa, values=anos, state="readonly", width=4,
                                         font=("Segoe UI", 14, "bold"))
            combo_ano_tar.current(0)
            combo_mes_tar = ttk.Combobox(editar_tarefa, values=meses, state="readonly", width=9,
                                         font=("Segoe UI", 14, "bold"))
            combo_mes_tar.current(0)
            combo_dia_tar = ttk.Combobox(editar_tarefa, values=dias, state="readonly", width=4,
                                         font=("Segoe UI", 14, "bold"))
            combo_dia_tar.current(0)
            butao_alterar_data = Button(editar_tarefa, text="Alterar para nova data", command=nova_data, bg="#4B0082",
                                        activebackground="#FFD700", relief="raised", foreground="#FFD700",
                                        font=("Segoe UI", 12, "bold"), borderwidth=6)
            label_alterar_descricao_tarefa = Label(editar_tarefa, text="Editar descrição da tarefa selecionada",
                                                   background="#4C0099", foreground="gold", font=('Arial BOLD', 18))
            textbox_descricao_tar = Text(editar_tarefa, height=5, font=('Arial BOLD', 14), background="#4C0099",
                                         relief="sunken", borderwidth=3, foreground="gold")
            textbox_descricao_tar.insert(1.0, tarefas[0][
                3])  # inserir o que ja estava na tarefa para facilitar as alteracoes
            butao_alterar_descricao = Button(editar_tarefa, text="Alterar descrição da tarefa", command=nova_descricao,
                                             bg="#4B0082", activebackground="#FFD700", relief="raised", borderwidth=6,
                                             foreground="#FFD700", font=("Segoe UI", 12, "bold"))
            butao_voltar = Button(editar_tarefa, text="Voltar", command=editar_tarefa.destroy, background="RED",
                                  relief="raised", borderwidth=3, font=("Segoe UI", 12, "bold"))

            label_alterar_n_tarefa.place(relx=0.02, rely=0.05, anchor="w")
            entry_alterar_n_tarefa.place(relx=0.43, rely=0.05, anchor="w")
            butao_confirma_alterar_nome.place(relx=0.8, rely=0.05, anchor="w")
            label_atribuir_a.place(relx=0.02, rely=0.15, anchor="w")
            combo_user_atribuido.place(relx=0.35, rely=0.15, anchor="w")
            butao_atribuir.place(relx=0.8, rely=0.15, anchor="w")
            label_alterar_data_limite.place(relx=0.02, rely=0.25, anchor="w")
            combo_ano_tar.place(relx=0.40, rely=0.25, anchor="w")
            combo_mes_tar.place(relx=0.55, rely=0.25, anchor="w")
            combo_dia_tar.place(relx=0.78, rely=0.25, anchor="w")
            butao_alterar_data.place(relx=0.02, rely=0.35, anchor="w", relwidth=0.96)
            label_alterar_descricao_tarefa.place(relx=0.02, rely=0.45, anchor="w")
            textbox_descricao_tar.place(relx=0.02, rely=0.6, anchor="w", relwidth=0.96, relheight=0.2)
            butao_alterar_descricao.place(relx=0.02, rely=0.8, anchor="w", relwidth=0.96)
            butao_voltar.place(relx=0.02, rely=0.95, anchor="w", relwidth=0.96)

            editar_tarefa.mainloop()

        def eliminar_tarefa(tarefa_id):
            resposta = messagebox.askyesno("Confirmação", f"Tem certeza de que deseja excluir a Tarefa {tarefa_id}")
            if resposta:
                sql = f"DELETE FROM tarefas WHERE nome_tarefa = '{tarefa_id}'"
                cur.execute(sql)
                con.commit()
                messagebox.showinfo("Exclusão", "Tarefas excluídas com sucesso.")
                update_aplica_alteracoes()
                criar_frame_objectivo(objectivo_escolhido)
            else:
                messagebox.showinfo("Exclusão", "Exclusão cancelada.")

        def atribuir_usuario(tarefa_id):
            sql = f"UPDATE tarefas SET nome_user = '{user_sessao}', estado = 'Em Progresso' WHERE nome_tarefa = '{tarefa_id}'"
            cur.execute(sql)
            con.commit()
            criar_frame_objectivo(objectivo_escolhido)  # volta a chamar a funçao para actualizar as alteraçoes

        def marcar_concluido(tarefa_id):
            resposta = messagebox.askyesno("Confirmação",
                                           f"Tem certeza de que deseja marcar a tarefa {tarefa_id} como concluida?")
            if resposta:
                sql = f"UPDATE tarefas SET estado = 'Concluído', data_realizaçao = '{hoje}' WHERE nome_tarefa = '{tarefa_id}'"
                cur.execute(sql)
                con.commit()
                criar_frame_objectivo(objectivo_escolhido)
                update_aplica_alteracoes()
            else:
                messagebox.showinfo("Conclusão", "Conclusão cancelada.")

        visao_objectivo.lift()
        # Limpar todos os widgets
        for widget in visao_objectivo.winfo_children():
            widget.destroy()
        # Frame 1
        frame_1 = Frame(visao_objectivo, bg="#9933FF")
        frame_1.place(relwidth=0.3, relheight=1)
        # Frame 2
        frame_2 = Frame(visao_objectivo)
        frame_2.place(relwidth=0.7, relheight=1, relx=0.3)

        # widgets da frame1
        label_viger1 = Label(frame_1, text=objectivo_escolhido, borderwidth=4, bg="#9933FF", foreground="#FFD700",
                             font=("Segoe UI", 20, "bold"))
        botao_adicionar_tarefa = Button(frame_1, text="Adicionar Tarefa", command=criar_tarefa, borderwidth=9,
                                        bg="#4B0082", activebackground="#FFD700",
                                        foreground="#FFD700", font=("Segoe UI", 12, "bold"))
        botao_volta_inicio = Button(frame_1, text="Voltar", command=visao_geral.lift, background="RED", relief="raised",
                                    borderwidth=3, font=("Segoe UI", 12, "bold"))
        # layout da frame 1
        label_viger1.place(relx=0, rely=0, relheight=0.2, relwidth=1)
        botao_adicionar_tarefa.place(x=0, y=150, relheight=0.2, relwidth=1)
        botao_volta_inicio.place(relx=0, rely=0.9, relheight=0.1, relwidth=1)

        # area de scroll da frame
        canvas = Canvas(frame_2, bg="#990099")
        canvas.grid(row=0, column=0, sticky="nsew")
        # scroll horizontal
        scrollbar = Scrollbar(frame_2, orient="horizontal", command=canvas.xview)
        scrollbar.grid(row=1, column=0, sticky="ew")
        canvas.configure(xscrollcommand=scrollbar.set)
        # scroll vertical
        scrollbar_vertical = Scrollbar(frame_2, orient="vertical", command=canvas.yview)
        scrollbar_vertical.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar_vertical.set)
        canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        scrollable_frame = Frame(canvas, bg="#990099")
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # widgets para serem colocados na frame2
        sql = f"SELECT * FROM tarefas WHERE objectivo = '{objectivo_escolhido}'"
        cur.execute(sql)
        tarefas = cur.fetchall()

        separadores = ttk.Notebook(
            scrollable_frame)  # cada frame mostra todos os dados das tarefas do objectivo escolhido previamente
        for tarefa in tarefas:
            framex = Frame(separadores, bg="#990099")  # cada tarefa cria uma frame para o notebook (separadores)
            if tarefa[3] == "Concluído":
                cor_estado = "green"
                # se estiver concluido coloca uma label a dizer a data em que foi concluido
            elif tarefa[3] == "Em Progresso":
                cor_estado = "orange"
            else:
                cor_estado = "red"

            # widgets de cada tarefa
            label_nome_tarefa = Label(framex, text=tarefa[0], font=("Segoe UI", 24), bg=cor_estado)
            label_data_conclusao = Label(framex, text=f"Tarefa concluida em: {tarefa[6]}", bg=cor_estado)
            label_data_criacao = Label(framex, text=f"Tarefa criada em: {tarefa[5]} ", font=("Segoe UI", 14),
                                       bg="#990099", fg="gold")
            label_data_final = Label(framex, text=f"A data maxima para terminar esta tarefa é: {tarefa[4]} ",
                                     font=("Segoe UI", 14), bg="#990099", fg="gold")
            label_tarefa2 = Label(framex, text=f"Estado da tarefa: {tarefa[3]}", font=("Segoe UI", 14), bg=cor_estado)
            label_user_da_tarefa = Label(framex, text=f"Tarefa atribuida a : {tarefa[2]}", font=("Segoe UI", 14),
                                         bg="#990099", fg="gold")
            label_descricao_tarefa = Label(framex, text=f"Detalhes da tarefa:\n {tarefa[7]}", font=("Segoe UI", 14),
                                           bg="#990099", wraplength=600, fg="gold")
            botao_atribuir_user = Button(framex, text="Aceitar Tarefa",
                                         command=lambda tar=tarefa[0]: atribuir_usuario(tar),
                                         bg="Gold", relief="raised", borderwidth=5, font=("Segoe UI", 12, "bold"))
            botao_tarefa_concluida = Button(framex, text="Marcar como Concluída",
                                            command=lambda tar=tarefa[0]: marcar_concluido(tar),
                                            bg="green", relief="raised", borderwidth=5, font=("Segoe UI", 12, "bold"))
            botao_eliminar_tarefa = Button(framex, text="Eliminar Tarefa",
                                           command=lambda tar=tarefa[0]: eliminar_tarefa(tar),
                                           background="RED", relief="raised", borderwidth=3,
                                           font=("Segoe UI", 12, "bold"))
            botao_editar_tarefa = Button(framex, text="Editar Tarefa", command=lambda tar=tarefa[0]: editar_tarefa(tar),
                                         borderwidth=9, bg="#4B0082", activebackground="#FFD700", foreground="#FFD700",
                                         font=("Segoe UI", 12, "bold"))

            # layout dos widgets da tarefa
            label_nome_tarefa.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=10)
            label_data_criacao.grid(row=1, column=0, columnspan=3, sticky="w", padx=10)
            label_data_final.grid(row=2, column=0, columnspan=3, sticky="w", padx=10)
            label_tarefa2.grid(row=3, column=0, columnspan=3, sticky="w", padx=10)
            label_user_da_tarefa.grid(row=4, column=0, columnspan=3, sticky="w", padx=10)
            label_descricao_tarefa.grid(row=5, column=0, columnspan=3, sticky="w", padx=10)
            botao_eliminar_tarefa.grid(row=8, column=0, sticky="e", padx=10, pady=10)
            botao_editar_tarefa.grid(row=8, column=1, sticky="e", padx=10, pady=10)

            if cor_estado == "green":
                label_data_conclusao.grid(row=6, column=1, sticky="e", padx=10, pady=3)
            elif user_sessao == tarefa[2]:
                botao_tarefa_concluida.grid(row=7, column=0, columnspan=3, pady=3)
            else:
                botao_atribuir_user.grid(row=6, column=0, columnspan=3, pady=3)

            separadores.add(framex, text=tarefa[0])

        separadores.pack(fill="both", expand=True)

        canvas.configure(scrollregion=canvas.bbox("all"))
        frame_2.grid_rowconfigure(0, weight=1)
        frame_2.grid_columnconfigure(0, weight=1)

    def update_aplica_alteracoes():
        def update_frame_ger2():
            # Limpar os widgets da frame
            for widget in frame_ger2.winfo_children():
                widget.destroy()
            # Criar um canvas para colocar os widgets dentro e ter a capacidade de fazer scroll no frame ger2
            canvas_ger2 = Canvas(frame_ger2, bg="#990099")
            canvas_ger2.pack(side="left", fill="both", expand=True)
            scrollbar_ger2 = Scrollbar(frame_ger2, orient="vertical", command=canvas_ger2.yview)
            scrollbar_ger2.pack(side="right", fill="y")
            canvas_ger2.configure(yscrollcommand=scrollbar_ger2.set)
            canvas_ger2.bind("<Configure>", lambda e: canvas_ger2.configure(scrollregion=canvas_ger2.bbox("all")))
            scrollable_frame_ger2 = Frame(canvas_ger2, bg="#990099")
            canvas_ger2.create_window((0, 0), window=scrollable_frame_ger2, anchor="nw")

            # Atualizar frame_ger2
            sql = "SELECT nome_objectivo, Data_final FROM objectivos;"
            cur.execute(sql)
            objectivos = cur.fetchall()

            # o aspecto das progressbar so podem ser alteradas com os temas
            estilo_barra = ttk.Style()
            estilo_barra.theme_use("clam")
            estilo_barra.configure("Custom.Horizontal.TProgressbar", troughcolor="purple", troughborderwidth=0,
                                   background="gold", bordercolor="black", lightcolor="purple", darkcolor="purple",
                                   thickness=30)

            for objectivo in objectivos:
                label_nome_obj = Label(scrollable_frame_ger2, text=f"{objectivo[0]}", font=("Segoe UI", 24, "bold"),
                                       bg="#990099", fg="gold")
                sql = f"SELECT estado FROM tarefas WHERE objectivo='{objectivo[0]}'"
                cur.execute(sql)
                tarefas = cur.fetchall()
                tarefas_total = len(tarefas)
                concluidos = 0
                for tarefa in tarefas:
                    if tarefa[0] == "Concluído":
                        concluidos += 1
                if tarefas_total != 0:
                    percentagem = (concluidos / tarefas_total) * 100
                else:
                    percentagem = 100
                progressbar = ttk.Progressbar(scrollable_frame_ger2, length=200, mode="determinate", value=percentagem,
                                              style="Custom.Horizontal.TProgressbar")
                label_percentagem = ttk.Label(scrollable_frame_ger2, text=f"{int(percentagem)}% Concluida",
                                              background="#990099", foreground="gold", font=("Segoe UI", 12, "bold"))
                label_prazo = ttk.Label(scrollable_frame_ger2,
                                        text=f"O prazo para entrega deste projeto é {objectivo[1]}",
                                        background="#990099", foreground="gold", font=("Segoe UI", 12, "bold"))

                label_nome_obj.pack()
                progressbar.pack()
                label_percentagem.pack()
                label_prazo.pack()

                # Atualizar a região de scroll do canvas ger2
                canvas_ger2.configure(scrollregion=canvas_ger2.bbox("all"))

        def update_frame_viger2():
            # Limpar os widgets da frame
            for widget in frame_viger2.winfo_children():
                widget.destroy()
            # Criar um canvas para colocar os widgets dentro e ter a capacidade de fazer scroll no frame viger2
            canvas_viger2 = Canvas(frame_viger2, bg="#990099")
            canvas_viger2.pack(side="left", fill="both", expand=True)
            scrollbar_viger2 = Scrollbar(frame_viger2, orient="vertical", command=canvas_viger2.yview)
            scrollbar_viger2.pack(side="right", fill="y")
            canvas_viger2.configure(yscrollcommand=scrollbar_viger2.set)
            canvas_viger2.bind("<Configure>", lambda e: canvas_viger2.configure(scrollregion=canvas_viger2.bbox("all")))
            scrollable_frame_viger2 = Frame(canvas_viger2, bg="#990099")
            canvas_viger2.create_window((0, 0), window=scrollable_frame_viger2, anchor="nw")

            # Atualizar frame_viger2
            sql = "SELECT nome_objectivo FROM objectivos;"
            cur.execute(sql)
            objectivos = cur.fetchall()
            Label(scrollable_frame_viger2,
                  text="Caso o sroll deixe de funcionar, aumente e volte a reduzir o tamanho da janela").pack()
            """Nao consegui descobrir porque o tkinter estava a dar este erro, mas vi que quando minizei e voltei a ampliar a janela 
            a funcionalidade voltava a funcionar como pretendido tentei fazer main_window.state('zoomed') e depois meter o state
            'normal', mas dessa forma nao estava a funcionar na mesma"""
            for objectivo in objectivos:
                Button(scrollable_frame_viger2, text=f"{objectivo[0]}", font=("Segoe UI", 24),
                       command=lambda obj=objectivo[0]: criar_frame_objectivo(obj), relief="raised",
                       borderwidth=5, bg="#4B0082", activebackground="#FFD700", foreground="#FFD700").pack()
                sql = f"SELECT nome_tarefa from tarefas where objectivo='{objectivo[0]}'"  # , relief="raised", bg="#4B0082", activebackground="#FFD700", foreground="#FFD700"
                cur.execute(sql)
                tarefas = cur.fetchall()
                todas = []
                todas_texto = ""
                for index, tarefa in enumerate(tarefas, start=1):
                    todas.append(f"{index}. {tarefa[0]}")
                    if index % 3 == 0:  # caso o index seja múltiplo de 3, passa para nova linha
                        todas_texto += f"{todas[-1]}\n"
                    else:
                        todas_texto += f"{todas[-1]} "
                Label(scrollable_frame_viger2, text=f"As tarefas deste objectivo são:\n {todas_texto}",
                      background="#990099", foreground="gold", font=("Segoe UI", 12, "bold")).pack()
            # Atualizar a região de rolagem do canvas viger2
            canvas_viger2.configure(scrollregion=canvas_viger2.bbox("all"))

        # chamar funçoes para voltar a criar com as actualizacoes da base de dados
        update_frame_ger2()
        update_frame_viger2()

    def valida_data(ano, mes, dia):
        ano = int(ano)
        anobisexto = int(ano) % 4 == 0 and (int(ano) % 100 != 0 or int(ano) % 400 == 0)
        if ano < hoje.year or (ano == hoje.year and meses.index(mes) + 1 < hoje.month) \
                or (ano == hoje.year and meses.index(mes) + 1 == hoje.month and int(dia) < hoje.day):
            return "A data final para a conclusao não pode ser no passado"
        if mes == "fevereiro":
            if anobisexto and int(dia) > 29:
                return "A data é inválida. Fevereiro não tem mais de 29 dias em anos bissextos."
            elif not anobisexto and int(dia) > 28:
                return "A data é inválida. Fevereiro não tem mais de 28 dias em anos não bissextos."
        elif mes in ["abril", "junho", "setembro", "novembro"] and int(dia) > 30:
            return "A data é inválida. O mês selecionado não tem mais de 30 dias."
        return None  # e possivel nos meses que nao coloquei aqui ter mais de 31 dias mas vou limitar nas comboboxes (readonly)

    def adiconar_objectivo():
        def cria_objectivo():
            data_check = False
            data_fim = (combo_ano.get(), combo_mes.get(), combo_dia.get())
            mensagemvalidacao = valida_data(
                *data_fim)  # o * serve para desempacotar o tuplo para irem os 3 parametros para a funçao
            if mensagemvalidacao:
                messagebox.showerror("Erro de validação da data", mensagemvalidacao)
            else:
                data_check = True
            # fazer novo check com a base de dados caso tenham sido apagados os objectivos e o user queira intuduzir com o nome que apagou
            sql = "SELECT nome_objectivo, Data_final FROM objectivos;"
            cur.execute(sql)
            objectivos = cur.fetchall()

            if entry_nome_obj.get() not in [obj[0] for obj in objectivos] and data_check and len(
                    entry_nome_obj.get()) > 1:
                string_data = f"{data_fim[0]}-{meses.index(data_fim[1]) + 1}-{data_fim[2]}"
                sql = """INSERT INTO objectivos (nome_objectivo, Data_final, Data_criaçao, Data_realizaçao)
                VALUES (%s, %s, %s, %s)"""
                dados_objectivos = [entry_nome_obj.get(), string_data, str(hoje), None]
                cur.execute(sql, dados_objectivos)
                con.commit()
                messagebox.showinfo("Objectivo Adicionado",
                                    f"{entry_nome_obj.get()} adiconado \ncom data limite: {string_data}")
                adicinar_obj.destroy()
                update_aplica_alteracoes()
            else:
                messagebox.showerror("Erro de validação da data", "Nao pode intruduzir esse Goal")

        adicinar_obj = Toplevel()
        adicinar_obj.overrideredirect(True)
        adicinar_obj.geometry(f"273x248+400+200")  # ao meter no goal track alterar para centrar na janela
        adicinar_obj.configure(background="#9933FF")
        adicinar_obj.bind("<Escape>", lambda event: adicinar_obj.destroy())
        # adicinar_obj.attributes("-topmost", True)  # fica por cima das messageboxes, nao posso usar

        # widgets
        label_nome_obj = Label(adicinar_obj, text="Nome do objectivo:",
                               background="#4C0099", foreground="gold", font=('Arial BOLD', 18), anchor="center")
        entry_nome_obj = Entry(adicinar_obj, font=('Arial BOLD', 18), background="#4C0099", relief="sunken",
                               borderwidth=3,
                               foreground="gold")
        label_prazo = Label(adicinar_obj, text="Prazo Final:",
                            background="#4C0099", foreground="gold", font=('Arial BOLD', 18), anchor="center")
        combo_ano = ttk.Combobox(adicinar_obj, values=anos, state="readonly", width=4, font=("Segoe UI", 14, "bold"))
        combo_ano.current(0)
        combo_mes = ttk.Combobox(adicinar_obj, values=meses, state="readonly", width=9, font=("Segoe UI", 14, "bold"))
        combo_mes.current(0)
        combo_dia = ttk.Combobox(adicinar_obj, values=dias, state="readonly", width=4, font=("Segoe UI", 14, "bold"))
        combo_dia.current(0)
        botao_add_obj = Button(adicinar_obj, text="Submeter", command=cria_objectivo, bg="#4B0082",
                               foreground="#FFD700",
                               activebackground="#FFD700", relief="raised", font=("Segoe UI", 12, "bold"))
        botao_cancelar_add = Button(adicinar_obj, text="voltar", command=lambda: adicinar_obj.destroy(),
                                    background="RED", relief="raised", borderwidth=3, font=("Segoe UI", 12, "bold"))

        # layout
        label_nome_obj.grid(row=0, column=0, padx=0.5, columnspan=3, pady=4, sticky="nsew")
        entry_nome_obj.grid(row=1, column=0, padx=0.5, columnspan=3, pady=5, sticky="nsew")
        label_prazo.grid(row=2, column=0, padx=0.5, columnspan=3, sticky="nsew")
        combo_dia.grid(row=3, column=2, padx=4, pady=4, sticky="nsew")
        combo_mes.grid(row=3, column=1, padx=4, pady=4, sticky="nsew")
        combo_ano.grid(row=3, column=0, padx=4, pady=4, sticky="nsew")
        botao_add_obj.grid(row=4, column=0, columnspan=3, pady=4, padx=0.5, sticky="nsew")
        botao_cancelar_add.grid(row=5, column=0, columnspan=3, pady=4, padx=0.5, sticky="nsew")

        adicinar_obj.mainloop()

    def adiar_objectivo():
        def altera_objectivo():
            data_fim = (combo_ano.get(), combo_mes.get(), combo_dia.get())
            mensagemvalidacao = valida_data(*data_fim)
            if mensagemvalidacao:
                messagebox.showerror("Erro de validação da data", mensagemvalidacao)
            else:
                sql = "UPDATE objectivos SET Data_final = %s WHERE nome_objectivo = %s"
                nome_objectivo = combo_objectivos.get()
                string_data = f"{data_fim[0]}-{meses.index(data_fim[1]) + 1}-{data_fim[2]}"
                cur.execute(sql, (string_data, nome_objectivo))
                con.commit()
                update_aplica_alteracoes()
                editar_obj.destroy()
                messagebox.showinfo("Data alterada", f"Data do objectivo alterada para  {string_data} \n com sucesso")

        editar_obj = Toplevel()
        editar_obj.overrideredirect(True)
        editar_obj.geometry(f"360x240+400+200")  # ao meter no goal track alterar para centrar na janela
        editar_obj.configure(background="#9933FF")
        editar_obj.bind("<Escape>", lambda event: editar_obj.destroy())
        # editar_obj.attributes("-topmost", True) # se usar o topmoust as messageboxes ficam atraz e nao dao para usar

        sql = "SELECT nome_objectivo FROM objectivos;"
        cur.execute(sql)
        objectivos = cur.fetchall()
        todos = []
        for objectivo in objectivos:
            todos.append(objectivo[0])

        #  widgets
        label_escolha = ttk.Label(editar_obj, text="Escolha o objectivo que quer alterar a data",
                                  background="#4C0099", foreground="gold", font=('Arial BOLD', 14), anchor="center")
        combo_objectivos = ttk.Combobox(editar_obj, values=todos, state="readonly", font=("Segoe UI", 14, "bold"))
        combo_objectivos.current(0)
        label_prazo = Label(editar_obj, text="Alterar a data para:",
                            background="#4C0099", foreground="gold", font=('Arial BOLD', 14), anchor="center")
        combo_ano = ttk.Combobox(editar_obj, values=anos, state="readonly", width=4, font=("Segoe UI", 14, "bold"))
        combo_ano.current(0)
        combo_mes = ttk.Combobox(editar_obj, values=meses, state="readonly", width=9, font=("Segoe UI", 14, "bold"))
        combo_mes.current(0)
        combo_dia = ttk.Combobox(editar_obj, values=dias, state="readonly", width=3, font=("Segoe UI", 14, "bold"))
        combo_dia.current(0)
        botao_add_obj = Button(editar_obj, text="Submeter", command=altera_objectivo, bg="#4B0082",
                               activebackground="#FFD700", foreground="#FFD700", font=("Segoe UI", 12, "bold"))
        botao_cancelar_add = Button(editar_obj, text="voltar", command=lambda: editar_obj.destroy(),
                                    background="RED", relief="raised", borderwidth=3, font=("Segoe UI", 12, "bold"))
        # layout
        label_escolha.grid(row=0, column=0, columnspan=3, sticky="NSEW")
        combo_objectivos.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="NSEW")
        label_prazo.grid(row=2, column=0, columnspan=3, pady=10, sticky="NSEW")
        combo_dia.grid(row=3, column=2, padx=5, pady=5, sticky="NSEW")
        combo_mes.grid(row=3, column=1, padx=5, pady=5, sticky="NSEW")
        combo_ano.grid(row=3, column=0, padx=5, pady=5, sticky="NSEW")
        botao_add_obj.grid(row=4, column=0, columnspan=3, pady=5, sticky="NSEW")
        botao_cancelar_add.grid(row=5, column=0, columnspan=3, sticky="NSEW")

    def eliminar_objectivo():
        def elimina_obj():
            resposta = messagebox.askyesno("Confirmação",
                                           f"Tem certeza de que deseja excluir o objectivo {combo_objectivos.get()}"
                                           f" e todas as suas tarefas?")
            if resposta:
                sql = "DELETE FROM tarefas WHERE objectivo = %s"
                objectivo = combo_objectivos.get()
                cur.execute(sql, (objectivo,))
                con.commit()
                sql = "DELETE FROM objectivos WHERE nome_objectivo = %s"
                cur.execute(sql, (objectivo,))
                con.commit()
                messagebox.showinfo("Exclusão", "Objectivo e tarefas excluídas com sucesso.")
                update_aplica_alteracoes()
                eliminar_obj.destroy()
            else:
                messagebox.showinfo("Exclusão", "Exclusão cancelada.")

        eliminar_obj = Toplevel()
        eliminar_obj.overrideredirect(True)
        eliminar_obj.geometry(f"570x200+400+200")  # ao meter no goal track alterar para centrar na janela
        eliminar_obj.configure(background="#9933FF")
        eliminar_obj.bind("<Escape>", lambda event: eliminar_obj.destroy())
        # eliminar_obj.attributes("-topmost", True) se usar o topmoust as messageboxes ficam atraz e nao dao para usar

        sql = "SELECT nome_objectivo FROM objectivos;"
        cur.execute(sql)
        objectivos = cur.fetchall()
        todos = []
        for objectivo in objectivos:
            todos.append(objectivo[0])
        combo_objectivos = ttk.Combobox(eliminar_obj, values=todos, state="readonly")
        combo_objectivos.current(0)

        # praparar a grid para colocar os widgets
        eliminar_obj.grid_rowconfigure((0, 1, 2, 3, 4), weight=2, uniform="a")
        eliminar_obj.grid_columnconfigure((0, 1), weight=1, uniform="b")

        # widgets
        label_eleminar = ttk.Label(eliminar_obj, background="#4C0099", foreground="gold", font=('Arial BOLD', 14),
                                   anchor="center",
                                   text="Selecione o objectivo a eleminar")
        label_eleminar_info = ttk.Label(eliminar_obj, background="#4C0099", foreground="gold", font=('Arial BOLD', 14),
                                        anchor="center",
                                        text="Atenção: Todas as tarefas deste objetivo também serão eliminadas!")
        combo_objectivos = ttk.Combobox(eliminar_obj, values=todos, state="readonly", font=("Segoe UI", 14, "bold"))
        combo_objectivos.current(0)
        botao_add_obj = Button(eliminar_obj, text="Eliminar", command=elimina_obj, bg="red",
                               activebackground="#FFD700", foreground="#FFD700", font=("Segoe UI", 12, "bold"))
        botao_cancelar_add = Button(eliminar_obj, text="voltar", command=lambda: eliminar_obj.destroy(),
                                    background="RED", relief="raised", borderwidth=3, font=("Segoe UI", 12, "bold"))

        # layout
        label_eleminar.grid(row=0, column=0, columnspan=2, sticky="NSEW")
        label_eleminar_info.grid(row=1, column=0, columnspan=2, sticky="NSEW")
        combo_objectivos.grid(row=2, column=0, columnspan=2, rowspan=2, padx=10, pady=10, sticky="NSEW")
        botao_add_obj.grid(row=4, column=1, sticky="NSEW", padx=10, pady=1)
        botao_cancelar_add.grid(row=4, column=0, sticky="NSEW", pady=1)

        eliminar_obj.mainloop()

    #  Aplicaçao principal
    main_window = Tk()
    main_window.iconbitmap("imagens/goaltrakicon.ico")
    main_window.title("GoalTrack 4.0")
    main_window.minsize(400, 400)
    main_window.geometry("700x500")

    # criar 3 frames que vao ocupar a janela completamente para servirem de janela vao ser chamados ao topo
    # Bem vindo menu inicial / visao geral objectivos / visao do singular objectivo / visao da tarefa singular
    # A criaçao e a ediçao dos objectivos sera feita com janelas pop up como fiz no log in
    visao_geral = Frame(main_window, bg="yellow")
    visao_objectivo = Frame(main_window, bg="red")
    visao_tarefa = Frame(main_window, bg="purple")
    menu_inicial = Frame(main_window, bg="blue")  # e o ultimo a ser criado para aparecer no topo

    visao_geral.place(relheight=1, relwidth=1)
    visao_objectivo.place(relheight=1, relwidth=1)
    menu_inicial.place(relheight=1, relwidth=1)

    ############################################
    # Layout da primeira janela <================
    ############################################
    frame_ger1 = Frame(menu_inicial, bg="#9933FF")
    frame_ger2 = Frame(menu_inicial, bg="green")
    frame_ger1.place(relwidth=0.3, relheight=1)
    frame_ger2.place(relwidth=0.7, relheight=1, relx=0.3)

    # dentro do frame_ger1
    # dentro do frame_ger1
    label_ger1 = Label(frame_ger1, text=f"Bem vindo,\n {user_sessao}", borderwidth=4, bg="#9933FF",
                       activebackground="#FFD700", foreground="#FFD700", font=("Segoe UI", 24, "bold"))
    butao_entra_geral = Button(frame_ger1, text="Ir para Objectivos", command=lambda: visao_geral.lift(),
                               relief="raised",
                               borderwidth=9, bg="#4B0082", activebackground="#FFD700", foreground="#FFD700",
                               font=("Segoe UI", 12, "bold"))
    label_ger1.place(relx=0, rely=0, relheight=0.2, relwidth=1)
    butao_entra_geral.place(x=0, y=150, relheight=0.2, relwidth=1)

    ###########################################################################
    # layout da Visao geral (segunda janela)<==================================
    ###########################################################################
    frame_viger1 = Frame(visao_geral, bg="#9933FF")
    frame_viger2 = Frame(visao_geral)
    frame_viger1.place(relwidth=0.3, relheight=1)
    frame_viger2.place(relwidth=0.7, relheight=1, relx=0.3)

    # frame Visao geral 1
    label_viger1 = Label(frame_viger1, text=f"Objectivos", borderwidth=4, bg="#9933FF",
                         activebackground="#FFD700", foreground="#FFD700", font=("Segoe UI", 24, "bold"))
    botao_adicionar_obj = Button(frame_viger1, text="Adiciona Objectivo", command=adiconar_objectivo, relief="raised",
                                 borderwidth=9, bg="#4B0082", activebackground="#FFD700", foreground="#FFD700",
                                 font=("Segoe UI", 12, "bold"))
    botao_editar_obj = Button(frame_viger1, text="Adiar Objectivo", command=adiar_objectivo, relief="raised",
                              borderwidth=9, bg="#4B0082", activebackground="#FFD700", foreground="#FFD700",
                              font=("Segoe UI", 12, "bold"))
    botao_eleminar_obj = Button(frame_viger1, text="Eliminar Objectivo", command=eliminar_objectivo, relief="raised",
                                borderwidth=9, bg="#4B0082", activebackground="#FFD700", foreground="#FFD700",
                                font=("Segoe UI", 12, "bold"))
    botao_volta_inicio = Button(frame_viger1, text="voltar", command=lambda: menu_inicial.lift(), background="RED",
                                relief="raised", borderwidth=3, font=("Segoe UI", 12, "bold"))

    label_viger1.place(relx=0, rely=0, relheight=0.2, relwidth=1)
    botao_adicionar_obj.place(relx=0, rely=0.3, relheight=0.15, relwidth=1)
    botao_editar_obj.place(relx=0, rely=0.45, relheight=0.15, relwidth=1)
    botao_eleminar_obj.place(relx=0, rely=0.6, relheight=0.15, relwidth=1)
    botao_volta_inicio.place(relx=0, rely=0.9, relheight=0.1, relwidth=1)

    update_aplica_alteracoes()
    #  As frame 2 de cada uma das frames (janela) anteriores nao são atualizadas na funçao, por isso sao criadas na base

    main_window.mainloop()


def jan_login_window():
    global user_sessao
    def conectar():
        global con, cur
        try:
            con = my.connect(host="localhost", database="goaltrack", user="root", password="")
            cur = con.cursor()
        except:
            x = messagebox.askretrycancel(title="Falha na conexao ao servidor", message="Porfavor ligue o servidor e Clique repetir")
            if x is True:
                conectar()


    def desconectar():  # Chamar esta funçao sempre que se fecha a aplicaçao
        cur.close()
        con.close()
        # print("desconectado do servidor")
        login_window.quit()


    def tentar_login():
        global user_sessao
        nome = user_entry.get()
        psw = encriptar(password_entry.get())
        # Recolher dados do servidor
        sql = "SELECT username, password FROM utilizador WHERE username = %s"
        cur.execute(sql, (nome,))  # ao usar o (%s tenho de colocar sempre tuplo)
        dados = cur.fetchone()  # so retorna uma linha
        if dados is not None:
            missing_user.grid_forget()
            username, password = dados
            if psw == password:
                missing_pass.grid_forget()
                user_sessao = username
                login_window.destroy()
                return user_sessao
            else:
                missing_pass.grid(row=5, column=0, columnspan=3)
        else:
            missing_user.grid(row=2, column=0, columnspan=3)


    def password_parametros(password):
        simbolos = "!@#$%^&*(),.?\":{}|<>"
        tem_maiuscula = False
        tem_simbolo = False
        if len(password) >= 8:
            for caracter in password:
                if caracter.isupper():
                    tem_maiuscula = True
                    print("Maiuscula check")
                elif caracter in simbolos:
                    tem_simbolo = True
                    print("simbolo check")
        return tem_maiuscula, tem_simbolo


    def encriptar(psw):
        password_bytes = psw.encode('utf8')
        sha256_hash = hashlib.sha256()
        sha256_hash.update(password_bytes)
        pass_encriptada = sha256_hash.hexdigest()
        return pass_encriptada


    def criar_user():
        def voltar():
            criar_novo_user_Butao.configure(state="enabled")
            novo_user_window.destroy()

        def confirmar():
            # verificar se o user e o email ainda nao existem na base de dados caso existam messagebox
            # tudo confirmado messagebox para dizer que esta tudo otimo
            # encriptar a password e submer o codigo sql para guardar o utilizador
            usercheck = False
            emailcheck = False
            passcheck = False
            sql = "select username, email from utilizador order by username;"
            cur.execute(sql)
            dados = cur.fetchall()
            usernames = []
            emails = []
            for item in dados:
                usernames.append(item[0])
                emails.append(item[1])
            if entry_nome_user.get() not in usernames and entry_nome_user.get() != "":
                usercheck = True
                label_user_indisponivel.grid_forget()
            else:
                usercheck = False
                label_user_indisponivel.grid(row=3, column=1, sticky="N")

            if entry_email.get() not in emails:
                emailcheck = True
                label_email_indisponivel.grid_forget()
                email = entry_email.get()
                if email.count("@") != 1 or "." not in email or len(email) < 3:
                    label_email_indisponivel.configure(text="Por favor insira um email válido")
                    label_email_indisponivel.grid(row=5, column=1, sticky="N")
                    emailcheck = False
                else:
                    email_pt1, email_pt2 = email.split("@")
                    if not email_pt1 or not email_pt2:
                        label_email_indisponivel.configure(text="Por favor insira um email válido")
                        label_email_indisponivel.grid(row=5, column=1, sticky="N")
                        emailcheck = False
                    else:
                        pt_1, pt_2 = email_pt2.split(".")
                        if not pt_1 or not pt_2 or len(pt_2) < 2 or len(pt_2) > 3:
                            label_email_indisponivel.configure(text="Por favor insira um email válido")
                            label_email_indisponivel.grid(row=5, column=1, sticky="N")
                            emailcheck = False


            # Verificar Passwords
            # verificar se as passords coicidem caso exista messagebox e verificar se a password tem os requesitos
            # tem de ter uma maiuscula mais de 10 caracters e um simbolo
            if entry_password.get() == entry_confirmar_password.get() and len(entry_password.get()) >= 8:
                tem_maiuscula, tem_simbolo = password_parametros(entry_password.get())
                if tem_maiuscula and tem_simbolo:
                    passcheck = True
                    label_info_password.configure(text="Password Valida")
                elif entry_password.get() != entry_confirmar_password.get():
                    label_info_password.configure(text="As passwords inseridas nao correspondem")
                elif tem_maiuscula is False and tem_simbolo is False:
                    label_info_password.configure(text="A password deve conter no minimo\n um simbolo e uma letra Maiuscula")
                elif tem_simbolo and not tem_maiuscula:
                    label_info_password.configure(text="A password deve conter no minimo\n uma letra Maiuscula")
                elif tem_maiuscula and not tem_simbolo:
                    label_info_password.configure(text="A password deve conter no minimo\n um simbolo (!@#$%^&*(),.?\":{}|<>)")
            elif len(entry_password.get()) < 8:
                label_info_password.configure(text="A password tem de ter no minimo 8 caracters")


            if usercheck and emailcheck and passcheck:  # todos os parametros cumpridos regista o user na BD
                password_para_encriptar = entry_password.get()  # Funcao para encriptar a password
                pass_encriptada = encriptar(password_para_encriptar)
                sql = f"""INSERT INTO `utilizador`( `username`, `email`, `password`) 
                VALUES ('{entry_nome_user.get()}','{entry_email.get()}','{pass_encriptada}')"""
                cur.execute(sql)
                con.commit()
                messagebox.showinfo("SUCESSO", "Utilizador Criado com sucesso")
                novo_user_window.destroy()
                criar_novo_user_Butao.configure(state="enabled")

        # Configurar a janela para criar o novo user
        criar_novo_user_Butao.configure(state="disabled")
        novo_user_window = Toplevel()
        novo_user_window.overrideredirect(True)
        novo_user_window.geometry(f"450x300+{horizontal-85}+{vertical+75}")
        novo_user_window.configure(background="#9933FF")
        novo_user_window.bind("<Return>", lambda event: confirmar())
        novo_user_window.bind("<Escape>", lambda event: voltar())

        # Configurar o layout da janela
        novo_user_window.grid_rowconfigure((0,1,2,4,6,7,9), weight=3, uniform="a")
        novo_user_window.grid_rowconfigure((3,5,8), weight=1, uniform="c")
        novo_user_window.grid_columnconfigure((0,1), weight=1, uniform="b")

        # widgets da janela
        label_cabecalho = ttk.Label(novo_user_window, text="Criar Novo User",
                                    style="estilo2.TLabel", font=('Arial BOLD', 20), anchor="center")
        label_nome_user = ttk.Label(novo_user_window, text="Intruduza o Username:",
                                    font=('Arial BOLD', 14), style="estilo1.TLabel")
        label_user_indisponivel = ttk.Label(novo_user_window, text="Esse nome de utilizador já esta a ser utilizado",
                                            font=('Arial', 8), foreground="#FFFFFF", background="#9933FF")
        entry_nome_user = ttk.Entry(novo_user_window, style="estilo2.TLabel", font=("arial", 13))
        label_email = ttk.Label(novo_user_window, text="Insira o seu email:",
                                font=('Arial BOLD', 14), style="estilo1.TLabel")
        label_email_indisponivel = ttk.Label(novo_user_window, text="Esse e-mail já tem uma conta associada",
                                             font=('Arial', 8), foreground="#FFFFFF", background="#9933FF")
        entry_email = ttk.Entry(novo_user_window, style="estilo2.TLabel", font=("arial", 13))
        label_info_password = ttk.Label(novo_user_window, text="A password deve conter 8 caracters "
                                                              "\npelo menos um simbolo e uma letra minúscula.",
                                        font=('Arial', 8), foreground="#FFFFFF", background="#9933FF")
        label_password = ttk.Label(novo_user_window, text="Insira a sua password:",
                                   font=('Arial BOLD', 14), style="estilo1.TLabel")
        entry_password = ttk.Entry(novo_user_window, show="*", style="estilo2.TLabel", font=("arial", 18))
        label_confirmar_password = ttk.Label(novo_user_window, text="Confirme a sua password:",
                                             font=('Arial BOLD', 14), style="estilo1.TLabel")
        entry_confirmar_password = ttk.Entry(novo_user_window, show="*",
                                             style="estilo2.TLabel", font=("arial", 18))
        botao_cancelar = Button(novo_user_window, text="Voltar", background="RED",
                                relief="sunken", borderwidth=3, command=voltar, font=("Segoe UI", 12, "bold"))
        botao_confirmar = Button(novo_user_window, text="Criar Utilizador", command=confirmar,
                                 bg="#4B0082", activebackground="#FFD700",
                                 foreground="#FFD700", font=("Segoe UI", 12, "bold"))

        # Layout dos widgets
        label_cabecalho.grid(row=0, column=0, columnspan=2, sticky="NSEW")
        label_nome_user.grid(row=2, column=0, sticky="E")
        entry_nome_user.grid(row=2, column=1, sticky="NWSE", pady=3, padx=10)
        label_email.grid(row=4, column=0, sticky="E")
        entry_email.grid(row=4, column=1, sticky="NSEW", pady=3, padx=10)
        label_password.grid(row=6, column=0, sticky="E")
        entry_password.grid(row=6, column=1, sticky="NSEW", pady=3, padx=10)
        label_confirmar_password.grid(row=7, column=0, sticky="E")
        entry_confirmar_password.grid(row=7, column=1, sticky="NSEW", pady=3, padx=10)
        label_info_password.grid(row=8, column=1, columnspan=2)
        botao_confirmar.grid(row=9, column=1, sticky="NSEW", padx=10, pady=1)
        botao_cancelar.grid(row=9, column=0, sticky="NSEW", padx=10, pady=1)

        novo_user_window.mainloop()


    def recuperar_password():
        def tenta_recuperar():
            usernames = []
            emails = []
            sql = "select username, email from utilizador;"
            cur.execute(sql)
            dados = cur.fetchall()
            for item in dados:
                usernames.append(item[0])
                emails.append(item[1])
            user = entry_nome_user.get()
            if user in usernames:
                posicao = usernames.index(user)
                label_aviso_user.grid_forget()
                if emails[posicao] == entry_email_user.get():
                    pass_nova = encriptar("MontyPython!")
                    sql = f"update utilizador set password = '{pass_nova}' where username = '{user}';"
                    cur.execute(sql)
                    con.commit()
                    recuperar_password_window.destroy()
                    messagebox.showinfo("Pass redefenida", "Não tive tempo de aprender a incorporar um programa"
                                                           " para enviar e-mails com um código de confirmação e"
                                                           " permitir a criação de uma nova senha. Portanto, a "
                                                           "nova senha para esse usuário será                   "
                                                           "   ==>   MontyPython!   <==")
                else:
                    label_aviso_email.configure(foreground="#FFFFFF", background="#9933FF", text="Esse user e e-mail não correspondem")
            else:
                label_aviso_user.configure(foreground="#FFFFFF", background="#9933FF", text="Esse user nao esta no sistema")


        recuperar_password_window = Toplevel()
        recuperar_password_window.overrideredirect(True)
        recuperar_password_window.geometry(f"450x300+{horizontal - 85}+{vertical + 75}")
        recuperar_password_window.bind("<Return>", lambda event: tenta_recuperar())

        # preparar o layout da janela
        frame_rp1 = Frame(recuperar_password_window)
        frame_rp2 = Frame(recuperar_password_window, background="#9933FF")
        frame_rp3 = Frame(recuperar_password_window, background="#9933FF")
        frame_rp1.place(rely=0, relx=0, relwidth=1, relheight=0.3)
        frame_rp2.place(rely=0.3, relx=0, relwidth=1, relheight=0.6)
        frame_rp3.place(rely=0.9, relx=0, relwidth=1, relheight=0.1)

        # Frame1
        image = Image.open("imagens\Recuperar_pass.png")
        photo_pass_perdida = ImageTk.PhotoImage(image)
        imaglabel = ttk.Label(frame_rp1, image=photo_pass_perdida, background="#4C0099", anchor="center")
        imaglabel.pack(expand=True, fill="both")

        # preparar a Grid da Frame2 para os widgets
        frame_rp2.grid_rowconfigure((0, 1, 2, 3,), weight=2, uniform="a")
        frame_rp2.grid_columnconfigure((0,1), weight=1, uniform="b")

        # widgets frame2
        label_nome_user = ttk.Label(frame_rp2, text="Nome de utilizador:",
                                    font=('Arial BOLD', 14), style="estilo1.TLabel")
        label_aviso_user = ttk.Label(frame_rp2, foreground="#9933FF", background="#9933FF")
        entry_nome_user = ttk.Entry(frame_rp2, style="estilo2.TLabel", font=("arial", 13))
        label_email_user = ttk.Label(frame_rp2, text="Email da conta:",
                                    font=('Arial BOLD', 14), style="estilo1.TLabel")
        label_aviso_email = ttk.Label(frame_rp2, foreground="#9933FF", background="#9933FF") # se o user existe e o email nao mostrar mensagem diferente
        entry_email_user = ttk.Entry(frame_rp2, style="estilo2.TLabel", font=("arial", 13))


        # layout dos widgets frame2
        label_nome_user.grid(row=0, column=0, sticky="E")
        entry_nome_user.grid(row=0, column=1, sticky="nsew", pady=5, padx=3)
        label_aviso_user.grid(row=1, column=1, sticky="NEW")
        label_email_user.grid(row=2, column=0, sticky="E")
        entry_email_user.grid(row=2, column=1, sticky="nsew", pady=5, padx=3)
        label_aviso_email.grid(row=3, column=1, sticky="NEW")


        # Frame3
        # widgets
        botao_recuperar = Button(frame_rp3, text="Recuperar", command=tenta_recuperar,
                                 bg="#4B0082", activebackground="#FFD700", relief="raised",
                                 foreground="#FFD700", font=("Segoe UI", 12, "bold"))
        botao_voltar = Button(frame_rp3, text="Voltar", command=lambda: recuperar_password_window.destroy(),
                              background="RED", relief="raised", borderwidth=3, font=("Segoe UI", 12, "bold"))
        #layout
        botao_voltar.place(relx=0.1, relheight=0.9, relwidth=0.38)
        botao_recuperar.place(relx=0.9, relheight=0.9, relwidth=0.38, anchor="ne")



        recuperar_password_window.mainloop()


    #####################################  script inicial  ############################################

    login_window = Tk()
    conectar()
    # ###################################### Criar mais estilos
    # estilo para o ttk
    estilo = ttk.Style()
    estilo.configure("estilo1.TLabel", background="#9933FF")
    estilo.configure("estilo2.TLabel", background="#4C0099", foreground="gold")
    estilo.configure("estilo3.TButton", background="#990099", activebackground="#202020", foreground="purple")

    # dimensões da janela, nao alteraveis / centrar a janela no ecra do computador onde for utilizada a app
    login_window.resizable(False, False)
    largura_da_janela = 300
    altura_da_janela = 400
    largura = login_window.winfo_screenwidth()
    altura = login_window.winfo_screenheight()
    login_window.geometry(f"{largura_da_janela}x{altura_da_janela}")
    horizontal = int(largura / 2 - largura_da_janela / 2)
    vertical = int(altura/2 - altura_da_janela/2)
    login_window.geometry(f"{largura_da_janela}x{altura_da_janela}+{horizontal}+{vertical}")

    # propriedades da janela
    login_window.bind("<Escape>", lambda event: desconectar())  # para fechar a janela rapido com o Esc
    login_window.bind("<Return>", lambda event: tentar_login())  # para tentar login ao pressionar enter
    login_window.overrideredirect(True)  # retirar os simbolos de fechar/minimizar (linux/windows/mac)
    # login_window.attributes("-topmost", True) # para ficar acima de tudo nao sei se vou usar


    # Frames
    frame1 = ttk.Frame(login_window, style="estilo1.TLabel")
    frame2 = ttk.Frame(login_window, style="estilo1.TLabel")
    frame3 = ttk.Frame(login_window, style="estilo2.TLabel")
    frame1.place(relx=0, rely=0, relheight=0.2, relwidth=1)
    frame2.place(relx=0, rely=0.2, relheight=0.6, relwidth=1)
    frame3.place(relx=0, rely=0.8, relheight=0.2, relwidth=1)

    #   Frame 1
    #  label com o logo da app
    ########################################## Fazer mais tarde ####################################
    image = Image.open("imagens\Logo.png")
    photo = ImageTk.PhotoImage(image)
    logo = ttk.Label(frame1, image=photo, style="estilo1.TLabel")
    logo.pack(expand=True, fill="both")


    # frame 2
    frame2.grid_rowconfigure((0, 1, 4, 6), weight=2, uniform="a")
    frame2.grid_rowconfigure((2, 5), weight=1, uniform="a")
    frame2.grid_columnconfigure((0, 1, 2), weight=1, uniform="b")

    # Widgets frame 2
    user_label = ttk.Label(frame2, text="Username", font="BradaSans, 20", style="estilo1.TLabel")
    user_entry = ttk.Entry(frame2, font="BradaSans, 20", width=15, style="estilo2.TLabel")
    password_label = ttk.Label(frame2, text="Password", font="BradaSans, 20", style="estilo1.TLabel")
    password_entry = ttk.Entry(frame2, show="*", font="BradaSans, 20", width=10, style="estilo2.TLabel")
    login_button = Button(frame2, text="Log In", command=tentar_login, relief="raised", borderwidth=4,
                          bg="#4B0082", activebackground="#FFD700", foreground="#FFD700", font=("Segoe UI", 12, "bold"))
    # mensagens para serem mostradas ao correr a func tentar_log_in caso necessario
    missing_user = ttk.Label(frame2, text="Nome de utilizador nao esta correcto", foreground="#FFFFFF", background="#9933FF")
    missing_pass = ttk.Label(frame2, text="A password que intruduziu nao esta correta", foreground="#FFFFFF", background="#9933FF")


    # layout Frame 3
    user_label.grid(row=0, column=0, columnspan=2, sticky="nwse", padx=10)
    user_entry.grid(row=1, column=1, columnspan=2, sticky="nwse", padx=10)
    password_label.grid(row=3, column=0, columnspan=2, sticky="nwse", padx=10)
    password_entry.grid(row=4, column=1, columnspan=2, sticky="nwse", padx=10)
    login_button.grid(row=6, column=0, columnspan=3, sticky="nsew")

    # Frame 3 Botao de sair e labels com estilo Hiperligaçao
    frame3.configure(border=5, borderwidth=5, relief="sunken")
    esqueceu_pass_label = ttk.Label(frame3, text="Esqueceu a sua password?", style="estilo2.TLabel")
    esqueceu_pass_botao = ttk.Button(frame3, text="Não consigo entrar", style="estilo3.TButton", command=recuperar_password)
    criar_novo_user_label = ttk.Label(frame3, text="Ainda nao tem conta?", style="estilo2.TLabel")
    criar_novo_user_Butao = ttk.Button(frame3, text="Criar novo utilizador", style="estilo3.TButton", command=criar_user)
    botao_sair = Button(frame3, text="SAIR", background="RED", relief="sunken", borderwidth=3, command=lambda: login_window.destroy())

    # layout da janela do log in
    esqueceu_pass_label.grid(row=0, column=0, sticky="NWES")
    esqueceu_pass_botao.grid(row=0, column=1, columnspan=1, sticky="NWES")
    criar_novo_user_label.grid(row=1, column=0, sticky="NWES")
    criar_novo_user_Butao.grid(row=1, column=1, columnspan=1, sticky="NWES")
    botao_sair.grid(row=2, column=2, sticky="NSEW")


    login_window.mainloop()

##### Script inicial #######
user_sessao = None
jan_login_window()  # usa a aplicaçao que criei para fazer o log in e devolve o utilizador caso faça login
if user_sessao:
    goaltrack(user_sessao)
