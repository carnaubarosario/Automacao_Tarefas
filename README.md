# ⚙️ Automação de Extração e Carga de Dados com Python, PostgreSQL e Telegram

Este projeto realiza a automação completa de um pipeline de dados: desde a extração de um relatório em um sistema web (como TOTVS), até o tratamento com Pandas, carga no Data Warehouse PostgreSQL e envio de notificações via Telegram. Ideal para tarefas recorrentes e integrações com painéis como Power BI e Looker Studio.

---

## 🚀 Funcionalidades

- Login automático em portal web com Selenium
- Download de relatório em Excel (.xlsx)
- Tratamento dos dados com Pandas
- Inserção em tabelas de dimensões e fato no PostgreSQL
- Notificação automática no Telegram ao final do processo
- Pronto para agendamento com `.bat` e Task Scheduler

---

## 📦 Tecnologias Utilizadas

- Python 3.12  
- Selenium WebDriver  
- Pandas  
- psycopg2  
- SQLAlchemy  
- Telegram Bot API  
- PostgreSQL  
- WebDriver Manager  
- Power BI / Looker Studio (consumo dos dados)

---

## 🧠 Estrutura do Pipeline

```mermaid
graph TD;
    A[Extração com Selenium] --> B[Download XLSX];
    B --> C[Processamento com Pandas];
    C --> D[Inserção no PostgreSQL];
    D --> E[Envio de alerta via Telegram];
    D --> F[Painel BI: Power BI / Looker Studio];
