import logging
import pandas as pd
import requests

logger = logging.getLogger(__name__)

def get_api_data() -> pd.DataFrame:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": -2.53,
        "longitude": -44.30,
        "hourly": "temperature_2m",
        "timezone": "America/Sao_Paulo"
    }

    try:
        logger.info(f"Iniciando requisição para API: {url}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Transformação Inicial
        df = pd.DataFrame({
            "timestamp_iso": data["hourly"]["time"],
            "temperatura": data["hourly"]["temperature_2m"],
            "cidade": "São Luís"
        })

        # Conversão de Tipos
        df["data_hora_full"] = pd.to_datetime(df["timestamp_iso"])
        df["data"] = df["data_hora_full"].dt.date
        df["hora"] = df["data_hora_full"].dt.time
        df["temperatura"] = df["temperatura"].astype(float)

        # Seleção final de colunas
        df_final = df[["data", "hora", "temperatura", "cidade"]].copy()
        
        logger.info(f"Extração concluída: {len(df_final)} registros obtidos.")
        return df_final

    except requests.exceptions.RequestException as e:
        logger.error(f"Erro fatal na conexão com a API: {e}")
        raise
    except KeyError as e:
        logger.error(f"Erro no formato do JSON recebido: {e}")
        raise