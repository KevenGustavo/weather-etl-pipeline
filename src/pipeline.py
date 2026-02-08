import time
import schedule
import logging
import os
from extract import get_api_data
from load import load_data_to_postgres

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/etl_pipeline.log"), 
        logging.StreamHandler()                       
    ]
)

logger = logging.getLogger("ETL_Orchestrator")

TABLE_NAME = os.getenv("DB_TABLE", "clima_historico")

def run_etl():
    logger.info("--- Iniciando Job ETL ---")
    try:
        # 1. Extract
        data = get_api_data()
        
        # 2. Transform & Load
        load_data_to_postgres(data, TABLE_NAME)
        
    except Exception as e:
        logger.error(f"Falha na execução do Pipeline: {e}")

if __name__ == "__main__":
    logger.info("Agendador iniciado. Executando a cada 1 minuto.")
    
    # Executa uma vez imediatamente ao iniciar
    run_etl()
    
    # Agenda
    schedule.every(1).minutes.do(run_etl)
    
    while True:
        schedule.run_pending()
        time.sleep(1)