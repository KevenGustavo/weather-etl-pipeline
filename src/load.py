import logging
import os
import pandas as pd
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine
from datetime import date

logger = logging.getLogger(__name__)

def get_db_engine() -> Engine:
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    db = os.getenv("POSTGRES_DB")
    host = os.getenv("DB_HOST")
    
    conn_str = f"postgresql://{user}:{password}@{host}:5432/{db}"
    return create_engine(conn_str, echo=False)

def load_data_to_postgres(df_new: pd.DataFrame, table_name: str) -> None:
    engine = get_db_engine()
    
    try:
        inspector = inspect(engine)

        if not inspector.has_table(table_name):
            logger.warning(f"Tabela '{table_name}' não encontrada. Criando nova (Cold Start)...")
            df_new.to_sql(table_name, engine, if_exists="append", index=False)
            logger.info(f"Carga Inicial: {len(df_new)} registros inseridos.")
            return

        today = date.today()
        logger.info(f"Buscando dados existentes a partir de: {today}")
        
        query = f"SELECT * FROM {table_name} WHERE data >= '{today}'"
        df_db = pd.read_sql(query, engine)
        
        # Normaliza tipos para garantir merge correto
        df_new["data"] = pd.to_datetime(df_new["data"]).dt.date
        df_new["hora"] = df_new["hora"].astype(str) # Hora costuma dar problema de tipo
        
        df_db["data"] = pd.to_datetime(df_db["data"]).dt.date
        df_db["hora"] = df_db["hora"].astype(str)

        # Left Anti-Join para achar apenas os novos
        merged = pd.merge(
            df_new, 
            df_db, 
            on=["data", "hora", "cidade"], 
            how="left", 
            indicator=True,
            suffixes=("", "_db")
        )
        
        #Armazenando apenas os novos registros, com as colunas corretas
        new_records = merged[merged["_merge"] == "left_only"][df_new.columns]

        if not new_records.empty:
            logger.info(f"Inserindo {len(new_records)} novos registros...")
            new_records.to_sql(table_name, engine, if_exists="append", index=False)
            logger.info("Carga finalizada com sucesso.")
        else:
            logger.info("Nenhum dado novo para inserir (Dados já atualizados).")

    except Exception as e:
        logger.error(f"Erro durante processo de carga no banco: {e}")
        raise