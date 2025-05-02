# === IMPORTAÇÕES ===
import os
import time
import pandas as pd
import psycopg2
import requests
from sqlalchemy import create_engine
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# === CONFIGURAÇÕES GERAIS ===
TOKEN = "<SEU_TOKEN_TELEGRAM>"
CHAT_ID = "<SEU_CHAT_ID>"
CAMINHO_ARQUIVO = r"<CAMINHO_PARA_ARQUIVO_XLSX>"

# === FUNÇÕES UTILITÁRIAS ===
def enviar_mensagem_telegram(token, chat_id, mensagem):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": mensagem}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Erro ao enviar mensagem no Telegram:", e)

def baixar_relatorio_web():
    try:
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {
            "download.default_directory": os.path.dirname(CAMINHO_ARQUIVO),
            "download.prompt_for_download": False
        })
        options.add_argument("--user-data-dir=C:\\Temp\\ChromeProfile")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        wait = WebDriverWait(driver, 60)

        # Acessa e faz login
        driver.get("<URL_DO_PORTAL>")
        wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys("<SEU_EMAIL>")
        driver.find_element(By.NAME, "password").send_keys("<SUA_SENHA>")
        driver.find_element(By.XPATH, "<XPATH_DO_BOTAO_LOGIN>").click()

        # Acessa e exporta o relatório
        wait.until(EC.element_to_be_clickable((By.XPATH, "<XPATH_RELATORIO>"))).click()
        time.sleep(60)  # Aguardar carregamento
        wait.until(EC.element_to_be_clickable((By.XPATH, "<XPATH_EXPORTAR_XLSX>"))).click()
        time.sleep(3)
        driver.quit()
    except Exception as e:
        print("Erro no scraping:", e)
        driver.quit()
        raise

def processar_excel(caminho):
    df = pd.read_excel(caminho, skiprows=2)
    df.columns = [col.upper().strip() for col in df.columns]
    df.fillna(0, inplace=True)
    df.dropna(subset=["DATA"], inplace=True)
    df = df[~df.apply(lambda row: row.astype(str).str.contains("Rollup").any(), axis=1)]
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce").dt.date
    return df

def limpar_tabelas(cur, conn):
    cur.execute("TRUNCATE TABLE fato CASCADE;")
    cur.execute("TRUNCATE TABLE dim_tempo CASCADE;")
    cur.execute("TRUNCATE TABLE dim_entidade CASCADE;")
    conn.commit()

def inserir_dados(df, cur, conn):
    for _, row in df.iterrows():
        cur.execute("SELECT id FROM dim_entidade WHERE nome = %s", (row["ENTIDADE"],))
        res = cur.fetchone()
        if not res:
            cur.execute("INSERT INTO dim_entidade (nome) VALUES (%s)", (row["ENTIDADE"],))
            cur.execute("SELECT id FROM dim_entidade WHERE nome = %s", (row["ENTIDADE"],))
            res = cur.fetchone()
        id_entidade = res[0]

        cur.execute("SELECT id FROM dim_tempo WHERE data = %s", (row["DATA"],))
        res = cur.fetchone()
        if not res:
            cur.execute("INSERT INTO dim_tempo (data) VALUES (%s)", (row["DATA"],))
            cur.execute("SELECT id FROM dim_tempo WHERE data = %s", (row["DATA"],))
            res = cur.fetchone()
        id_tempo = res[0]

        cur.execute("""
            INSERT INTO fato (id_entidade, id_tempo, valor)
            VALUES (%s, %s, %s)
        """, (id_entidade, id_tempo, row["VALOR"]))

    conn.commit()

# === EXECUÇÃO PRINCIPAL ===
try:
    baixar_relatorio_web()
    df = processar_excel(CAMINHO_ARQUIVO)

    conn = psycopg2.connect(
        host="localhost",
        database="seu_dw",
        user="seu_user",
        password="sua_senha"
    )
    cur = conn.cursor()

    limpar_tabelas(cur, conn)
    inserir_dados(df, cur, conn)

    cur.close()
    conn.close()

    enviar_mensagem_telegram(TOKEN, CHAT_ID, "✅ Processo concluído com sucesso!")

except Exception as erro:
    print("Erro geral:", erro)
    enviar_mensagem_telegram(TOKEN, CHAT_ID, f"❌ Erro no processo: {erro}")
