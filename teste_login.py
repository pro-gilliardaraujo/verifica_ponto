import time
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

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
        print(f"Erro ao inicializar o driver: {e}")
        traceback.print_exc()
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
            print(f"Login pode ter falhado. URL atual: {driver.current_url}")
            return False
    
    except TimeoutException:
        print("Timeout ao aguardar elementos na página de login.")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"Erro durante o login: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Parâmetros de login
    url_login = "https://autenticador.secullum.com.br/Authorization?response_type=code&client_id=3&redirect_uri=https%3A%2F%2Fpontoweb.secullum.com.br%2FAuth"
    email = "fer.b.silveira@gmail.com"
    senha = "1234"
    
    driver = None
    try:
        # Inicializar o driver
        driver = inicializar_driver()
        if driver is None:
            print("Não foi possível inicializar o driver. Abortando o teste.")
            exit(1)
        
        # Fazer login
        login_sucesso = fazer_login(driver, url_login, email, senha)
        
        if login_sucesso:
            print("Teste de login bem-sucedido!")
            # Aguardar alguns segundos para visualizar a página após o login
            time.sleep(10)
            print("Página atual:", driver.current_url)
            print("Título da página:", driver.title)
        else:
            print("Teste de login falhou!")
    
    except Exception as e:
        print(f"Erro durante o teste: {e}")
        traceback.print_exc()
    
    finally:
        # Fechar o navegador
        if driver:
            print("Fechando o navegador...")
            driver.quit() 