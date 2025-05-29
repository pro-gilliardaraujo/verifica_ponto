import time
import traceback
import sys
import os
import pandas as pd
import glob
import argparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def log_erro(mensagem, erro=None):
    """Registra erros de forma detalhada"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    erro_log = f"[ERRO] {timestamp} - {mensagem}"
    
    if erro:
        erro_log += f"\nDetalhes: {str(erro)}\n"
        erro_log += traceback.format_exc()
    
    print(erro_log)
    
    # Opcionalmente, pode salvar em um arquivo de log
    with open("erro_log.txt", "a", encoding="utf-8") as f:
        f.write(erro_log + "\n\n")

def inicializar_driver():
    """Inicializa e retorna um WebDriver do Chrome"""
    try:
        print("Inicializando o driver do Chrome...")
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        print("Driver inicializado com sucesso!")
        return driver
    except Exception as e:
        log_erro("Falha ao inicializar o driver do Chrome", e)
        return None

def fazer_login(driver, url_login, email, senha, manter_conectado=True):
    """Realiza o login no sistema Secullum Ponto Web"""
    try:
        print("Acessando página de login...")
        driver.get(url_login)
        
        # Aguardar página de login carregar
        print("Aguardando página de login carregar...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="Email"]'))
        )
        
        # Preencher email
        print("Preenchendo email...")
        campo_email = driver.find_element(By.XPATH, '//*[@id="Email"]')
        campo_email.clear()
        campo_email.send_keys(email)
        
        # Preencher senha
        print("Preenchendo senha...")
        campo_senha = driver.find_element(By.XPATH, '//*[@id="Senha"]')
        campo_senha.clear()
        campo_senha.send_keys(senha)
        
        # Marcar checkbox se necessário
        if manter_conectado:
            print("Marcando 'Continuar conectado'...")
            try:
                checkbox = driver.find_element(By.XPATH, '//*[@id="ContinuarConectado"]')
                if not checkbox.is_selected():
                    checkbox.click()
            except NoSuchElementException:
                print("Checkbox 'Continuar conectado' não encontrado.")
        
        # Clicar no botão de login
        print("Clicando em 'Entrar'...")
        botao_login = driver.find_element(By.XPATH, '//*[@id="login"]')
        botao_login.click()
        
        # Aguardar redirecionamento após login
        print("Aguardando redirecionamento após login...")
        time.sleep(5)  # Ajuste conforme necessário
        
        # Verificar se o login foi bem-sucedido
        print(f"URL atual após login: {driver.current_url}")
        
        if "pontoweb.secullum.com.br" in driver.current_url:
            print("Login realizado com sucesso!")
            return True
        else:
            log_erro(f"Login falhou. URL atual: {driver.current_url}")
            return False
    
    except TimeoutException as e:
        log_erro("Timeout ao aguardar elementos na página de login", e)
        return False
    except Exception as e:
        log_erro("Erro durante o login", e)
        return False

def navegar_para_cartao_ponto(driver):
    """Navega para a página de cartão-ponto após o login"""
    try:
        # Aguardar a página inicial carregar completamente
        print("Aguardando a página inicial carregar...")
        time.sleep(3)  # Aguarda um tempo para garantir que a página carregou

        # Clicar no botão Movimentações
        print("Clicando no botão 'Movimentações'...")
        botao_movimentacoes = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="movimentacoes"]'))
        )
        botao_movimentacoes.click()
        time.sleep(2)  # Aguarda o menu expandir

        # Clicar no botão Cartão-Ponto
        print("Clicando no botão 'Cartão-Ponto'...")
        botao_cartao_ponto = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="cartao-ponto"]'))
        )
        botao_cartao_ponto.click()

        # Aguardar a página de cartão-ponto carregar
        print("Aguardando a página de cartão-ponto carregar...")
        time.sleep(5)  # Ajuste conforme necessário

        print(f"Navegação concluída. URL atual: {driver.current_url}")
        return True

    except TimeoutException as e:
        log_erro("Timeout ao aguardar elementos na navegação", e)
        return False
    except Exception as e:
        log_erro("Erro durante a navegação", e)
        return False

def preencher_datas(driver, data_inicio, data_fim):
    """Preenche os campos de data na página de cartão-ponto"""
    try:
        print(f"Verificando/preenchendo datas: {data_inicio} a {data_fim}")
        
        # Localizar campo de data início
        campo_data_inicio = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="DataInicio"]'))
        )
        
        # Verificar se a data de início já está correta
        valor_atual_inicio = campo_data_inicio.get_attribute("value")
        print(f"Data início atual: '{valor_atual_inicio}', desejada: '{data_inicio}'")
        
        if valor_atual_inicio == data_inicio:
            print("Data de início já está correta, não precisa alterar.")
        else:
            # Limpeza rigorosa do campo de data início
            print("Limpando campo de data início...")
            campo_data_inicio.click()
            time.sleep(0.5)
            campo_data_inicio.clear()
            time.sleep(0.5)
            campo_data_inicio.send_keys(Keys.CONTROL + "a")  # Selecionar todo o texto
            time.sleep(0.5)
            campo_data_inicio.send_keys(Keys.DELETE)  # Deletar o texto selecionado
            time.sleep(0.5)
            
            # Verificar se o campo está vazio
            if campo_data_inicio.get_attribute("value"):
                print("Campo ainda não está vazio, tentando método alternativo...")
                for _ in range(10):  # Tentar backspace múltiplas vezes
                    campo_data_inicio.send_keys(Keys.BACKSPACE)
                    time.sleep(0.1)
            
            # Preencher a data de início lentamente
            print(f"Preenchendo data início: {data_inicio}")
            for char in data_inicio:
                campo_data_inicio.send_keys(char)
                time.sleep(0.1)  # Pequena pausa entre cada caractere
            
            # Confirmar entrada e esperar
            campo_data_inicio.send_keys(Keys.TAB)
            time.sleep(1.5)  # Espera mais longa
        
        # Localizar campo de data fim
        campo_data_fim = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="DataFim"]'))
        )
        
        # Verificar se a data de fim já está correta
        valor_atual_fim = campo_data_fim.get_attribute("value")
        print(f"Data fim atual: '{valor_atual_fim}', desejada: '{data_fim}'")
        
        if valor_atual_fim == data_fim:
            print("Data de fim já está correta, não precisa alterar.")
        else:
            # Limpeza rigorosa do campo de data fim
            print("Limpando campo de data fim...")
            campo_data_fim.click()
            time.sleep(0.5)
            campo_data_fim.clear()
            time.sleep(0.5)
            campo_data_fim.send_keys(Keys.CONTROL + "a")  # Selecionar todo o texto
            time.sleep(0.5)
            campo_data_fim.send_keys(Keys.DELETE)  # Deletar o texto selecionado
            time.sleep(0.5)
            
            # Verificar se o campo está vazio
            if campo_data_fim.get_attribute("value"):
                print("Campo ainda não está vazio, tentando método alternativo...")
                for _ in range(10):  # Tentar backspace múltiplas vezes
                    campo_data_fim.send_keys(Keys.BACKSPACE)
                    time.sleep(0.1)
            
            # Preencher a data de fim lentamente
            print(f"Preenchendo data fim: {data_fim}")
            for char in data_fim:
                campo_data_fim.send_keys(char)
                time.sleep(0.1)  # Pequena pausa entre cada caractere
            
            # Confirmar entrada e esperar
            campo_data_fim.send_keys(Keys.TAB)
            time.sleep(1.5)  # Espera mais longa
        
        # Verificar se as datas foram alteradas
        datas_alteradas = (valor_atual_inicio != data_inicio) or (valor_atual_fim != data_fim)
        
        if datas_alteradas:
            # Se alguma data foi alterada, aguardar o carregamento dos dados
            print("Datas foram alteradas. Aguardando carregamento dos dados...")
            time.sleep(5)  # Espera mais longa para carregamento
        else:
            print("Nenhuma data foi alterada, prosseguindo sem aguardar carregamento adicional.")
        
        print("Verificação/preenchimento de datas concluído!")
        return True
        
    except TimeoutException as e:
        log_erro("Timeout ao aguardar campos de data", e)
        return False
    except Exception as e:
        log_erro("Erro ao preencher datas", e)
        return False

def encontrar_arquivo_excel(caminho=None):
    """Encontra o arquivo Excel especificado ou o primeiro da pasta"""
    try:
        if caminho and os.path.exists(caminho):
            print(f"Usando arquivo Excel especificado: {caminho}")
            return caminho
            
        # Se não foi especificado ou não existe, procurar na pasta atual
        arquivos_excel = glob.glob("*.xlsx")
        if arquivos_excel:
            print(f"Arquivo Excel encontrado: {arquivos_excel[0]}")
            return arquivos_excel[0]
        else:
            log_erro("Nenhum arquivo Excel (.xlsx) encontrado na raiz do projeto")
            return None
    except Exception as e:
        log_erro("Erro ao buscar arquivo Excel", e)
        return None

def listar_planilhas_excel(arquivo):
    """Lista todas as planilhas disponíveis no arquivo Excel"""
    try:
        # Listar todas as planilhas disponíveis
        xls = pd.ExcelFile(arquivo)
        planilhas = xls.sheet_names
        print(f"Planilhas disponíveis no arquivo: {planilhas}")
        return planilhas
    except Exception as e:
        log_erro(f"Erro ao listar planilhas do arquivo Excel: {arquivo}", e)
        return []

def ler_dados_excel(arquivo):
    """Lê os dados do arquivo Excel e imprime as 5 primeiras linhas"""
    try:
        print(f"\n{'='*50}")
        print(f"Lendo arquivo Excel: {arquivo}")
        
        # Primeiro, listar todas as planilhas disponíveis
        planilhas = listar_planilhas_excel(arquivo)
        if not planilhas:
            return None
        
        # Usar a primeira planilha disponível
        primeira_planilha = planilhas[0]
        print(f"Usando a planilha: {primeira_planilha}")
        
        # Ler a planilha
        df = pd.read_excel(arquivo, sheet_name=primeira_planilha)
        
        # Armazenar o nome do arquivo e da planilha como atributos do DataFrame
        # Isso será útil ao salvar as atualizações posteriormente
        df.attrs['arquivo_excel'] = arquivo
        df.attrs['sheet_name'] = primeira_planilha
        
        # Verificar as colunas esperadas
        colunas_esperadas = ["Cód Epr", "NOME", "ADMISS", "FUNÇÃO", "21 A 31", "01 A 10", "11 A 20"]
        colunas_faltantes = [col for col in colunas_esperadas if col not in df.columns]
        
        if colunas_faltantes:
            log_erro(f"Colunas faltantes no arquivo Excel: {', '.join(colunas_faltantes)}")
            print("Colunas encontradas:", list(df.columns))
        else:
            print("Todas as colunas esperadas foram encontradas!")
        
        # Imprimir informações básicas
        total_linhas = df.shape[0]
        print(f"\nDimensões do DataFrame: {total_linhas} linhas x {df.shape[1]} colunas")
        
        # Filtrar linhas vazias ou com valores NaN na coluna 'NOME'
        df_filtrado = df.dropna(subset=['NOME'])
        df_filtrado = df_filtrado[df_filtrado['NOME'].str.strip() != '']
        
        # Manter os atributos do DataFrame original
        df_filtrado.attrs = df.attrs.copy()
        
        print(f"Total de linhas após filtrar nomes vazios: {len(df_filtrado)}")
        
        # Imprimir as 5 primeiras linhas de forma mais detalhada
        print("\n===== 5 PRIMEIRAS ENTRADAS DO ARQUIVO =====")
        registros_mostrados = 0
        
        for i in range(min(10, len(df_filtrado))):  # Verificamos até 10 para garantir que encontraremos 5
            try:
                if registros_mostrados >= 5:
                    break
                    
                # Verificar se o registro tem nome válido
                nome = str(df_filtrado.iloc[i]['NOME'])
                if not nome or nome.lower() == 'nan' or nome.strip() == '':
                    continue
                    
                registros_mostrados += 1
                print(f"\nRegistro #{registros_mostrados}:")
                print(f"  Código: {df_filtrado.iloc[i]['Cód Epr']}")
                print(f"  Nome: {nome}")
                print(f"  Admissão: {df_filtrado.iloc[i]['ADMISS']}")
                print(f"  Função: {df_filtrado.iloc[i]['FUNÇÃO']}")
                print(f"  Período 21 A 31: {df_filtrado.iloc[i]['21 A 31']}")
                print(f"  Período 01 A 10: {df_filtrado.iloc[i]['01 A 10']}")
                print(f"  Período 11 A 20: {df_filtrado.iloc[i]['11 A 20']}")
                print(f"  {'-'*40}")
            except Exception as e:
                print(f"Erro ao processar linha {i}: {str(e)}")
        
        print(f"Total de registros mostrados: {registros_mostrados}")
        print(f"{'='*50}\n")
        return df_filtrado
    
    except Exception as e:
        log_erro(f"Erro ao ler o arquivo Excel: {arquivo}", e)
        return None

def testar_busca_funcionarios(driver, df, coluna_periodo):
    """Função simplificada para testar apenas a busca de funcionários, sem verificações adicionais"""
    try:
        print(f"\n{'='*50}")
        print(f"Iniciando teste de busca de funcionários para o período {coluna_periodo}")
        print(f"Total de funcionários no arquivo: {len(df)}")
        
        # Contar quantos funcionários já têm o período preenchido
        preenchidos = df[df[coluna_periodo].notnull() & (df[coluna_periodo].astype(str).str.strip() != '')].shape[0]
        vazios = df[df[coluna_periodo].isnull() | (df[coluna_periodo].astype(str).str.strip() == '')].shape[0]
        
        print(f"Funcionários com período já preenchido: {preenchidos}")
        print(f"Funcionários com período vazio: {vazios}")
        
        # Funções a serem ignoradas
        funcoes_ignorar = ["MOTORISTA", "MOTORISTA CARRETEIRO", "ENCARREGADO DE SERVICO DE TRANSPORTE"]
        print(f"Funções que serão ignoradas: {', '.join(funcoes_ignorar)}")
        
        # Contador de funcionários verificados
        testados = 0
        ignorados = 0
        erros = 0
        
        # Percorrer cada linha do DataFrame
        for index, row in df.iterrows():
            # Limitamos a testar apenas 5 funcionários para o teste inicial
            if testados >= 5:
                print("\nLimite de 5 funcionários atingido para o teste inicial.")
                break
                
            try:
                # Verificar se a coluna do período está vazia
                valor_periodo = str(row[coluna_periodo]).strip() if pd.notnull(row[coluna_periodo]) else ""
                
                if valor_periodo == "" or valor_periodo.lower() == "nan":
                    # Encontrou um funcionário com período vazio
                    nome_funcionario = row["NOME"]
                    codigo_funcionario = row["Cód Epr"]
                    funcao_funcionario = str(row["FUNÇÃO"]).strip()
                    
                    # Verificar se a função deve ser ignorada
                    if funcao_funcionario.upper() in [f.upper() for f in funcoes_ignorar]:
                        ignorados += 1
                        print(f"\n{'-'*50}")
                        print(f"Ignorando funcionário: {nome_funcionario} (Código: {codigo_funcionario})")
                        print(f"Função ignorada: {funcao_funcionario}")
                        continue
                    
                    print(f"\n{'-'*50}")
                    print(f"Testando busca para: {nome_funcionario} (Código: {codigo_funcionario}, Função: {funcao_funcionario})")
                    
                    # Aguardar um pouco para garantir que a página está pronta
                    time.sleep(2)
                    
                    # Abordagem direta para interagir com o campo de busca usando seu ID
                    try:
                        # 1. Localizar o campo de busca diretamente pelo ID
                        print("Localizando campo de busca pelo ID 'funcionarioId'...")
                        
                        # Primeiro limpar qualquer seleção existente
                        try:
                            clear_button = driver.find_element(By.CSS_SELECTOR, '.Select-clear-zone')
                            clear_button.click()
                            print("Limpou seleção existente")
                            time.sleep(1)
                        except:
                            print("Não foi possível limpar seleção existente ou não havia seleção")
                        
                        # Localizar o elemento de controle Select e clicar nele para ativar o input
                        try:
                            select_control = driver.find_element(By.CSS_SELECTOR, '.Select-control')
                            select_control.click()
                            print("Clicou no controle Select para ativar o input")
                            time.sleep(1)
                        except Exception as e:
                            print(f"Erro ao clicar no controle Select: {e}")
                        
                        # Localizar o campo de input diretamente pelo ID
                        input_field = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, 'funcionarioId'))
                        )
                        print("Encontrou o campo de input pelo ID")
                        
                        # Focar no campo de input
                        driver.execute_script("arguments[0].focus();", input_field)
                        print("Focou no campo de input")
                        time.sleep(0.5)
                        
                        # Limpar qualquer texto existente
                        input_field.clear()
                        driver.execute_script("arguments[0].value = '';", input_field)
                        print("Limpou o campo de input")
                        time.sleep(0.5)
                        
                        # 2. Digitar o nome do funcionário caractere por caractere
                        print(f"Digitando nome: {nome_funcionario}")
                        for char in nome_funcionario:
                            input_field.send_keys(char)
                            time.sleep(0.1)  # Pequena pausa entre os caracteres
                        
                        # Garantir que o React registrou o valor
                        driver.execute_script("""
                            var input = arguments[0];
                            var event = new Event('input', { bubbles: true });
                            input.dispatchEvent(event);
                            var event2 = new Event('change', { bubbles: true });
                            input.dispatchEvent(event2);
                        """, input_field)
                        
                        time.sleep(1)
                        
                        # 3. Pressionar Enter
                        input_field.send_keys(Keys.RETURN)
                        print("Enter pressionado")
                        
                        # Aguardar para ver o resultado
                        print(f"Aguardando resultados para {nome_funcionario}...")
                        time.sleep(3)
                        
                        # Capturar screenshot para verificação
                        screenshot_file = f"busca_{nome_funcionario.replace(' ', '_')}.png"
                        driver.save_screenshot(screenshot_file)
                        print(f"Screenshot salvo: {screenshot_file}")
                        
                        # Verificar se o nome aparece no componente
                        try:
                            nome_exibido = driver.find_element(By.ID, 'react-select-3--value-item').text
                            print(f"Nome exibido no componente: '{nome_exibido}'")
                            
                            if nome_funcionario.strip() in nome_exibido:
                                print("✓ SUCESSO: Nome encontrado corretamente!")
                            else:
                                print("✗ FALHA: Nome exibido não corresponde ao esperado")
                        except:
                            print("Não foi possível verificar o nome exibido")
                        
                        # Incrementar contador
                        testados += 1
                        
                    except Exception as e:
                        erros += 1
                        print(f"Erro ao buscar funcionário {nome_funcionario}: {e}")
                        traceback.print_exc()
                    
                    # Pequena pausa entre cada funcionário
                    time.sleep(2)
            
            except Exception as e:
                erros += 1
                print(f"Erro ao processar linha {index}: {e}")
                continue
        
        # Imprimir resumo do teste
        print(f"\nResumo do teste de busca:")
        print(f"Total de funcionários testados: {testados}")
        print(f"Total de funcionários ignorados (por função): {ignorados}")
        print(f"Total de erros durante o processamento: {erros}")
        
        print(f"{'='*50}\n")
        return testados > 0
    
    except Exception as e:
        log_erro("Erro durante o teste de busca de funcionários", e)
        return False

def executar(arquivo_excel, periodo, data_inicio, data_fim):
    """Função principal que coordena todo o processo"""
    # Ler o arquivo Excel
    df = ler_dados_excel(arquivo_excel)
    if df is None:
        print("Não foi possível ler os dados do Excel. Verifique o arquivo.")
        return False
    
    # Parâmetros de login
    url_login = "https://autenticador.secullum.com.br/Authorization?response_type=code&client_id=3&redirect_uri=https%3A%2F%2Fpontoweb.secullum.com.br%2FAuth"
    email = "fer.b.silveira@gmail.com"
    senha = "1234"
    
    driver = None
    erro_ocorreu = False
    
    try:
        # Inicializar o driver
        driver = inicializar_driver()
        if driver is None:
            print("Não foi possível inicializar o driver. Abortando o teste.")
            return False
        
        # Fazer login
        login_sucesso = fazer_login(driver, url_login, email, senha)
        
        if login_sucesso:
            print("Login bem-sucedido! Navegando para a página de cartão-ponto...")
            
            # Navegar para a página de cartão-ponto
            navegacao_sucesso = navegar_para_cartao_ponto(driver)
            
            if navegacao_sucesso:
                print("Navegação concluída com sucesso!")
                
                # Preencher as datas
                if preencher_datas(driver, data_inicio, data_fim):
                    print(f"Datas preenchidas: {data_inicio} a {data_fim}")
                    
                    # Testar a busca de funcionários (apenas busca, sem verificação)
                    try:
                        print("\nIniciando teste de busca de funcionários...")
                        testar_busca_funcionarios(driver, df, periodo)
                        print("Teste de busca concluído!")
                    except Exception as e:
                        print(f"Erro durante o teste de busca de funcionários: {str(e)}")
                        traceback.print_exc()
                    
                    print("\nNavegador mantido aberto para verificação manual.")
                    print("Pressione Ctrl+C para encerrar o script quando desejar.")
                    
                    # Manter o script em execução para o navegador não fechar
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("\nScript interrompido pelo usuário.")
                else:
                    print("Falha ao preencher as datas.")
                    erro_ocorreu = True
            else:
                print("Falha na navegação para a página de cartão-ponto.")
                erro_ocorreu = True
        else:
            print("Falha no login. Não é possível continuar.")
            erro_ocorreu = True
    
    except KeyboardInterrupt:
        print("\nScript interrompido pelo usuário.")
    except Exception as e:
        log_erro("Erro não tratado durante a execução", e)
        erro_ocorreu = True
    
    finally:
        # Fechar o navegador apenas se ocorreu algum erro
        if driver and erro_ocorreu:
            print("Fechando o navegador devido a erros...")
            driver.quit()
        elif driver and not erro_ocorreu:
            print("Execução concluída com sucesso. Navegador mantido aberto.")
            print("Para fechar o navegador, pressione Ctrl+C.")
        
        return not erro_ocorreu

if __name__ == "__main__":
    # Processar argumentos de linha de comando
    args = parse_arguments()
    
    # Modo de execução
    modo_apenas_excel = args.apenas_excel
    
    # Verificar se existe arquivo Excel
    arquivo_excel = encontrar_arquivo_excel(args.arquivo)
    if arquivo_excel:
        # Ler e mostrar os dados do Excel
        df = ler_dados_excel(arquivo_excel)
        if df is None:
            print("Não foi possível ler os dados do Excel. Verifique o arquivo.")
            sys.exit(1)
        
        # Se estiver apenas no modo de leitura do Excel, encerrar aqui
        if modo_apenas_excel:
            print("Modo de leitura do Excel concluído. Encerrando o script.")
            sys.exit(0)
            
        # Executar verificação completa
        if args.data_inicio and args.data_fim:
            sucesso = executar(
                arquivo_excel, 
                args.periodo, 
                args.data_inicio, 
                args.data_fim
            )
            sys.exit(0 if sucesso else 1)
        else:
            print("Datas de início e fim são obrigatórias para a verificação.")
            sys.exit(1)
    else:
        print("Nenhum arquivo Excel encontrado. Não é possível continuar.")
        sys.exit(1) 