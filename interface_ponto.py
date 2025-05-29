import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
import traceback
import threading
import importlib.util
import subprocess
import time

# Verificar e instalar dependências
def verificar_dependencias():
    dependencias = ["pandas", "selenium", "webdriver_manager", "openpyxl"]
    faltando = []
    
    for dep in dependencias:
        try:
            __import__(dep)
        except ImportError:
            faltando.append(dep)
    
    if faltando:
        mensagem = f"Faltam as seguintes dependências: {', '.join(faltando)}\n\nDeseja instalar agora?"
        resposta = messagebox.askyesno("Dependências Ausentes", mensagem)
        
        if resposta:
            try:
                for dep in faltando:
                    print(f"Instalando {dep}...")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                    time.sleep(1)  # Dar tempo para concluir a instalação
                
                messagebox.showinfo("Instalação Concluída", "Dependências instaladas com sucesso. O programa será reiniciado.")
                python = sys.executable
                os.execl(python, python, *sys.argv)  # Reinicia o script
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao instalar dependências: {str(e)}")
                sys.exit(1)
        else:
            messagebox.showerror("Erro", "Não é possível continuar sem as dependências necessárias.")
            sys.exit(1)

# Inicializar Tkinter para mostrar mensagens
root_init = tk.Tk()
root_init.withdraw()  # Ocultar janela principal temporariamente

try:
    # Verificar dependências
    verificar_dependencias()
    
    # Agora é seguro importar as dependências
    import pandas as pd
    import calendar
    from datetime import datetime, timedelta
    
    # Tentar importar o verificador_ponto.py como módulo
    try:
        spec = importlib.util.spec_from_file_location("verificador_ponto", "verificador_ponto.py")
        verificador_ponto = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verificador_ponto)
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível carregar o módulo verificador_ponto.py: {str(e)}")
        sys.exit(1)
    
    # Destruir a janela temporária
    root_init.destroy()
    
    # Criar a janela real da aplicação
    root = tk.Tk()
    
    class AplicacaoPonto:
        def __init__(self, root):
            self.root = root
            self.root.title("Verificador de Ponto")
            self.root.geometry("600x600")  # Aumentada a altura de 400 para 600 pixels
            self.root.resizable(True, True)
            
            # Variáveis
            self.arquivo_excel = tk.StringVar()
            self.periodo_selecionado = tk.StringVar(value="21 A 31")  # Valor padrão
            self.verificacao_em_andamento = False
            
            # Frame principal
            main_frame = ttk.Frame(root, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Título
            ttk.Label(main_frame, text="Verificador de Ponto", font=("Arial", 16, "bold")).pack(pady=10)
            
            # Frame para seleção de arquivo
            file_frame = ttk.LabelFrame(main_frame, text="Arquivo Excel", padding="10")
            file_frame.pack(fill=tk.X, pady=10)
            
            ttk.Entry(file_frame, textvariable=self.arquivo_excel, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            ttk.Button(file_frame, text="Selecionar", command=self.selecionar_arquivo).pack(side=tk.RIGHT, padx=5)
            
            # Frame para seleção de período
            period_frame = ttk.LabelFrame(main_frame, text="Selecione o Período", padding="10")
            period_frame.pack(fill=tk.X, pady=10)
            
            # Botões de rádio para os períodos
            ttk.Radiobutton(period_frame, text="21 a 31 (Fim do mês anterior)", variable=self.periodo_selecionado, value="21 A 31", command=self.calcular_datas).pack(anchor=tk.W, pady=5)
            ttk.Radiobutton(period_frame, text="01 a 10 (Início do mês atual)", variable=self.periodo_selecionado, value="01 A 10", command=self.calcular_datas).pack(anchor=tk.W, pady=5)
            ttk.Radiobutton(period_frame, text="11 a 20 (Meio do mês atual)", variable=self.periodo_selecionado, value="11 A 20", command=self.calcular_datas).pack(anchor=tk.W, pady=5)
            
            # Frame para exibir datas calculadas
            dates_frame = ttk.LabelFrame(main_frame, text="Datas a serem verificadas", padding="10")
            dates_frame.pack(fill=tk.X, pady=10)
            
            ttk.Label(dates_frame, text="Data Início:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            self.data_inicio_label = ttk.Label(dates_frame, text="", font=("Arial", 10, "bold"))
            self.data_inicio_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
            
            ttk.Label(dates_frame, text="Data Fim:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            self.data_fim_label = ttk.Label(dates_frame, text="", font=("Arial", 10, "bold"))
            self.data_fim_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
            
            # Botão atualizar datas
            ttk.Button(dates_frame, text="Calcular Datas", command=self.calcular_datas).grid(row=2, column=0, columnspan=2, pady=10)
            
            # Botão iniciar verificação
            self.start_button = ttk.Button(main_frame, text="Iniciar Verificação", command=self.iniciar_verificacao)
            self.start_button.pack(pady=20)
            
            # Status bar
            self.status_var = tk.StringVar(value="Pronto")
            status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
            status_bar.pack(side=tk.BOTTOM, fill=tk.X)
            
            # Calcular datas iniciais
            self.calcular_datas()
        
        def selecionar_arquivo(self):
            """Abre diálogo para selecionar arquivo Excel"""
            filetypes = [("Arquivos Excel", "*.xlsx *.xls"), ("Todos os arquivos", "*.*")]
            arquivo = filedialog.askopenfilename(title="Selecione o arquivo Excel", filetypes=filetypes)
            
            if arquivo:
                self.arquivo_excel.set(arquivo)
                self.status_var.set(f"Arquivo selecionado: {os.path.basename(arquivo)}")
        
        def calcular_datas(self):
            """Calcula as datas de início e fim baseado no período selecionado"""
            try:
                hoje = datetime.now()
                periodo = self.periodo_selecionado.get()
                
                # Períodos possíveis: "21 A 31", "01 A 10", "11 A 20"
                if periodo == "21 A 31":
                    # Fim do mês anterior
                    if hoje.month == 1:  # Janeiro
                        mes_ref = 12
                        ano_ref = hoje.year - 1
                    else:
                        mes_ref = hoje.month - 1
                        ano_ref = hoje.year
                    
                    data_inicio = datetime(ano_ref, mes_ref, 21)
                    # Último dia do mês (considerando fevereiro e meses com menos de 31 dias)
                    ultimo_dia = calendar.monthrange(ano_ref, mes_ref)[1]
                    data_fim = datetime(ano_ref, mes_ref, ultimo_dia)
                    
                elif periodo == "01 A 10":
                    # Início do mês atual
                    data_inicio = datetime(hoje.year, hoje.month, 1)
                    data_fim = datetime(hoje.year, hoje.month, 10)
                    
                elif periodo == "11 A 20":
                    # Meio do mês atual
                    data_inicio = datetime(hoje.year, hoje.month, 11)
                    data_fim = datetime(hoje.year, hoje.month, 20)
                    
                else:
                    raise ValueError(f"Período inválido: {periodo}")
                
                # Formatar as datas para exibição
                data_inicio_str = data_inicio.strftime("%d/%m/%Y")
                data_fim_str = data_fim.strftime("%d/%m/%Y")
                
                # Atualizar as labels
                self.data_inicio_label.config(text=data_inicio_str)
                self.data_fim_label.config(text=data_fim_str)
                self.status_var.set(f"Datas calculadas: {data_inicio_str} a {data_fim_str}")
                
                return data_inicio_str, data_fim_str
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao calcular datas: {str(e)}")
                traceback.print_exc()
                return None, None
        
        def verificar_dados(self):
            """Verifica se todos os dados estão preenchidos corretamente"""
            if not self.arquivo_excel.get():
                messagebox.showwarning("Aviso", "Selecione um arquivo Excel.")
                return False
            
            if not os.path.exists(self.arquivo_excel.get()):
                messagebox.showerror("Erro", "O arquivo Excel selecionado não existe.")
                return False
            
            # Verificar se é possível ler o arquivo Excel
            try:
                df = pd.read_excel(self.arquivo_excel.get())
                # Verificar se tem as colunas necessárias
                colunas_necessarias = ["Cód Epr", "NOME"]
                for col in colunas_necessarias:
                    if col not in df.columns:
                        messagebox.showerror("Erro", f"O arquivo Excel não contém a coluna '{col}'.")
                        return False
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao ler o arquivo Excel: {str(e)}")
                return False
            
            return True
        
        def thread_verificacao(self, arquivo_excel, periodo, data_inicio, data_fim):
            """Thread para executar a verificação em segundo plano"""
            try:
                self.verificacao_em_andamento = True
                self.status_var.set(f"Verificação em andamento para o período {periodo}...")
                
                # Chamar a função executar do verificador_ponto.py
                resultado = verificador_ponto.executar(
                    arquivo_excel, 
                    periodo, 
                    data_inicio, 
                    data_fim
                )
                
                # Atualizar interface quando terminar
                if resultado:
                    self.status_var.set(f"Verificação concluída com sucesso para o período {periodo}")
                else:
                    self.status_var.set(f"Verificação falhou para o período {periodo}")
            
            except Exception as e:
                self.status_var.set(f"Erro na verificação: {str(e)}")
                traceback.print_exc()
            
            finally:
                self.verificacao_em_andamento = False
                self.start_button.config(state=tk.NORMAL)
        
        def iniciar_verificacao(self):
            """Inicia o processo de verificação"""
            if self.verificacao_em_andamento:
                messagebox.showwarning("Aviso", "Uma verificação já está em andamento.")
                return
            
            if not self.verificar_dados():
                return
            
            # Calcular datas
            data_inicio, data_fim = self.calcular_datas()
            if not data_inicio or not data_fim:
                return
            
            # Desabilitar o botão durante a verificação
            self.start_button.config(state=tk.DISABLED)
            
            # Dados para a verificação
            arquivo_excel = self.arquivo_excel.get()
            periodo = self.periodo_selecionado.get()
            
            # Exibir informações da verificação
            messagebox.showinfo("Verificação Iniciada", 
                              f"Verificação iniciada com os seguintes parâmetros:\n\n"
                              f"Arquivo: {os.path.basename(arquivo_excel)}\n"
                              f"Período: {periodo}\n"
                              f"Data Início: {data_inicio}\n"
                              f"Data Fim: {data_fim}\n\n"
                              "O navegador será aberto para iniciar a verificação.")
            
            # Iniciar verificação em uma thread separada
            thread = threading.Thread(
                target=self.thread_verificacao,
                args=(arquivo_excel, periodo, data_inicio, data_fim),
                daemon=True
            )
            thread.start()

    # Iniciar a aplicação
    app = AplicacaoPonto(root)
    root.mainloop()
    
except Exception as e:
    messagebox.showerror("Erro", f"Erro ao iniciar a aplicação: {str(e)}")
    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    pass  # A execução principal já foi feita acima 