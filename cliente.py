import base64
import os
import sys
import tkinter as tk
from tkinter import messagebox
import threading
import time
import datetime
import pyautogui
import cv2
import numpy as np
import playsound

# Configuração de login
USUARIO_CORRETO = "admin"
SENHA_CORRETA = "1234"

# Arquivo de registro encriptado
DIAS_LIMITE = 30
DATA_INICIO_ARQUIVO = "data_inicio.txt"

# Variável global para controle de monitoramento
monitorando = False

def resource_path(relative_path):
    """Retorna o caminho absoluto do recurso, compatível com PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Itens monitorados
itens_monitorados = {
    "Gemstone": {"imagem": resource_path("img_Gemstone.jpg"), "som": resource_path("Gemstone_SOM.mp3"), "ativo": None},
    "Jewel": {"imagem": resource_path("img_jewel.jpg"), "som": resource_path("Jewel_SOM.mp3"), "ativo": None},
    "Bless": {"imagem": resource_path("img_Bless.jpg"), "som": resource_path("Todos_SOM.mp3"), "ativo": None},
    "Claw": {"imagem": resource_path("Img_Claw.jpg"), "som": resource_path("Todos_SOM.mp3"), "ativo": None},
    "Splinter": {"imagem": resource_path("img_Splinter.jpg"), "som": resource_path("Todos_SOM.mp3"), "ativo": None}
}

# Proteção do tempo de uso
def verificar_tempo_restante():
    if not os.path.exists(DATA_INICIO_ARQUIVO):
        data_inicio = datetime.date.today().isoformat()
        with open(DATA_INICIO_ARQUIVO, "w") as f:
            f.write(base64.b64encode(data_inicio.encode()).decode())
    else:
        with open(DATA_INICIO_ARQUIVO, "r") as f:
            try:
                data_inicio = base64.b64decode(f.read().strip()).decode()
            except Exception:
                return 0
    
    data_inicio = datetime.datetime.strptime(data_inicio, "%Y-%m-%d").date()
    dias_passados = (datetime.date.today() - data_inicio).days
    return max(0, DIAS_LIMITE - dias_passados)

# Monitoramento
def tocar_som(audio):
    if os.path.exists(audio):
        threading.Thread(target=playsound.playsound, args=(audio,), daemon=True).start()
    else:
        print(f"Arquivo de áudio não encontrado: {audio}")

def monitorar_tela():
    global monitorando, status_label
    status_label.config(text="Código Rodando", fg="green")
    while monitorando:
        tela = np.array(pyautogui.screenshot())
        tela = cv2.cvtColor(tela, cv2.COLOR_RGB2GRAY)
        
        for nome, dados in itens_monitorados.items():
            if dados["ativo"].get():
                imagem = cv2.imread(dados["imagem"], cv2.IMREAD_GRAYSCALE)
                if imagem is not None:
                    result = cv2.matchTemplate(tela, imagem, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, _ = cv2.minMaxLoc(result)
                    if max_val > 0.87:
                        tocar_som(dados["som"])
        time.sleep(1)
    status_label.config(text="Código Parado", fg="red")

def iniciar_monitoramento():
    global monitorando
    if not monitorando:
        monitorando = True
        threading.Thread(target=monitorar_tela, daemon=True).start()

def parar_monitoramento():
    global monitorando
    monitorando = False

def criar_interface():
    dias_restantes = verificar_tempo_restante()
    if dias_restantes <= 0:
        messagebox.showerror("Erro", "Seu período de teste expirou!")
        sys.exit()
    
    global status_label
    janela = tk.Tk()
    janela.title("Monitoramento de Itens")
    janela.geometry("400x350")  # Aumentado o tamanho da interface
    
    for nome, dados in itens_monitorados.items():
        dados["ativo"] = tk.BooleanVar(janela)
    
    frame_itens = tk.Frame(janela)
    frame_itens.pack(pady=10)
    
    for nome, dados in itens_monitorados.items():
        tk.Checkbutton(frame_itens, text=nome, variable=dados["ativo"], fg="blue").pack(anchor='w')
    
    frame_botoes = tk.Frame(janela)
    frame_botoes.pack(pady=10)
    
    tk.Button(frame_botoes, text="Iniciar", command=iniciar_monitoramento, bg="green", fg="white").pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botoes, text="Parar", command=parar_monitoramento, bg="gray", fg="white").pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botoes, text="Sair", command=janela.quit, bg="red", fg="white").pack(side=tk.LEFT, padx=5)
    
    status_label = tk.Label(janela, text="Código Parado", fg="red")
    status_label.pack(pady=5)
    
    label_tempo = tk.Label(janela, text=f"Dias restantes: {dias_restantes}", fg="red", font=("Arial", 12, "bold"))
    label_tempo.place(x=10, y=10)
    
    janela.mainloop()

def verificar_login():
    usuario = entrada_usuario.get()
    senha = entrada_senha.get()
    if usuario == USUARIO_CORRETO and senha == SENHA_CORRETA:
        login_janela.destroy()
        criar_interface()
    else:
        messagebox.showerror("Erro", "Usuário ou senha incorretos")

# Criando tela de login
login_janela = tk.Tk()
login_janela.title("Login")
login_janela.geometry("300x150")

entrada_usuario = tk.Entry(login_janela)
entrada_usuario.pack()
entrada_senha = tk.Entry(login_janela, show="*")
entrada_senha.pack()

tk.Button(login_janela, text="Entrar", command=verificar_login).pack()
login_janela.mainloop()
