# **End-to-End Weather Data Pipeline**

Um pipeline de Engenharia de Dados completo e containerizado que extrai dados meteorológicos em tempo real, transforma os dados para formato analítico e os carrega em um Data Warehouse PostgreSQL, garantindo **Idempotência** e **Rastreabilidade**.

## **Arquitetura**

O projeto segue uma arquitetura ETL (Extract, Transform, Load) orquestrada em micro-serviços Docker:

Snippet de código

```mermaid
graph LR  
    A\[Open-Meteo API\] \--\>|JSON| B(Container ETL Python)  
    B \--\>|Extração & Limpeza| C{Verificação de Duplicidade}  
    C \--\>|Novos Dados| D\[(PostgreSQL DB)\]  
    C \--\>|Dados Existentes| E\[Ignora\]  
    D \--\>|Persistência| F\[Docker Volume\]  
    G\[PgAdmin4\] \--\>|Interface Visual| D
```

## **Funcionalidades Chave**

* **Ingestão Automatizada:** Coleta dados da API Open-Meteo a cada minuto (configurável).  
* **Idempotência (Data Quality):** Implementa lógica de *Left Anti-Join* para comparar dados novos com o histórico do banco, garantindo que **nenhum registro seja duplicado**, mesmo se o pipeline rodar múltiplas vezes.  
* **Ambiente Isolado (Docker):** Todo o ecossistema (Python, Postgres, PgAdmin) sobe com um único comando, sem necessidade de instalar dependências na máquina local.  
* **Logging Estruturado:** Sistema de logs persistentes (rotacionados em arquivo e console) para monitoramento e debugging.  
* **Segurança:** Gerenciamento de credenciais via variáveis de ambiente (.env), sem senhas hardcoded no repositório.

## **Estrutura do Projeto**

```Plaintext
weather-etl-pipeline/  
├── src/  
│   ├── extract.py    \# Conexão com API e tratamento inicial  
│   ├── load.py       \# Lógica de Banco de Dados e Deduplicação  
│   └── pipeline.py   \# Orquestrador e Agendador (Entrypoint)  
├── logs/             \# Logs persistidos do container  
├── docker-compose.yml  
├── Dockerfile  
├── Makefile          \# Atalhos de comandos  
├── requirements.txt  
└── .env.example      \# Template de variáveis de ambiente
```

## **Como Executar**

### **Pré-requisitos**

* Docker e Docker Compose instalados.

### **Passo a Passo**

1. **Clone o repositório:**  
   ```Bash  
   git clone https://github.com/SEU-USUARIO/weather-etl-pipeline.git  
   cd weather-etl-pipeline
   ```

2. **Configure as Variáveis de Ambiente:**  
   ```Bash  
   cp .env.example .env
   ```

   *Edite o arquivo .env com seus dados preferidos.*  
3. **Suba o Ambiente (Via Makefile):**  
   ```Bash  
   make up
   ```

   *Ou manualmente: ```docker compose up --build -d```*  
4. **Acompanhe os Logs:**  

   ```Bash  
   make logs
   ```

   *Você verá o processo de extração e carga acontecendo em tempo real.*

## **Acessando os Dados (PgAdmin)**

O projeto inclui o PgAdmin4 para visualização dos dados.

1. Acesse: http://localhost:8080  
2. Login: Use o e-mail e senha definidos no seu .env.  
3. Conecte ao servidor:  
   * **Host:** postgres (Nome do serviço Docker)  
   * **Username/Password:** O mesmo do .env.

## **Detalhes Técnicos**

### **Estratégia de Carga (Upsert Logic)**

Para evitar a inserção de duplicatas sem sobrecarregar o banco, o pipeline utiliza uma estratégia de **Janela de Tempo**:

1. O script define uma janela de interesse (ex: dados de hoje em diante).  
2. Lê apenas esse subconjunto do banco de dados para a memória (Pandas).  
3. Realiza um merge entre os dados da API e os dados do Banco.  
4. Filtra apenas os registros que existem na API mas **não** existem no banco ```(_merge == 'left_only')```.  
5. Insere apenas o delta, garantindo eficiência e integridade.

---

**Autor:** [Keven Gomes](https://www.linkedin.com/in/keven-gomes/)
