from fastapi import FastAPI, Request
from typing import List
import pandas as pd
from datetime import datetime, timedelta
import re
from datetime import datetime

app = FastAPI()

# In-memory storage simulado para datos de batería
battery_data = []


@app.post("/battery/status")
async def update_battery_status(request: Request):
    data = await request.json()
    # Verificar que los datos necesarios estén presentes
    if "energy_available_kW" in data and "battery_capacity_kW" in data:
        # Generar automáticamente el timestamp actual
        data["timestamp"] = datetime.now()
        # Calcular el porcentaje de carga de la batería basado en la energía disponible y la capacidad total
        data["battery_level"] = (data["energy_available_kW"] / data["battery_capacity_kW"]) * 100
        battery_data.append(data)
        return {"message": "Battery status updated"}
    else:
        return {"error": "Invalid data format. Must include 'energy_available_kW' and 'battery_capacity_kW'."}

@app.get("/battery/current")
def get_current_battery_status():
    if battery_data:
        # Último estado almacenado
        current_status = battery_data[-1]
        return {
            "timestamp": current_status["timestamp"],
            "battery_level": current_status["battery_level"],
            "battery_capacity_kW": current_status["battery_capacity_kW"],
            "energy_available_kW": current_status["energy_available_kW"]
        }
    return {"message": "No data available"}

@app.get("/battery/history")
def get_battery_history(delta: str):
    try:
        match = re.match(r"(\d+)([dhm])", delta)
        if not match:
            return {"error": "Invalid time delta format. Use formats like '1d', '2h', or '30m'."}
        
        value, unit = int(match.group(1)), match.group(2)
        if unit == 'd':
            time_threshold = datetime.now() - timedelta(days=value)
        elif unit == 'h':
            time_threshold = datetime.now() - timedelta(hours=value)
        elif unit == 'm':
            time_threshold = datetime.now() - timedelta(minutes=value)
        else:
            return {"error": "Unsupported time unit. Use 'd' for days, 'h' for hours, or 'm' for minutes."}
        
        if not battery_data or "timestamp" not in battery_data[0]:
            return {"error": "No valid battery data available."}
        
        for entry in battery_data:
            entry['timestamp'] = pd.to_datetime(entry['timestamp'])
        
        df = pd.DataFrame(battery_data)
        mask = df['timestamp'] >= time_threshold
        filtered_data = df[mask].to_dict(orient='records')

        return filtered_data

    except Exception as e:
        return {"error": str(e)}

# Endpoint para cargar datos generados desde un CSV (ej. el archivo que creaste antes)
@app.post("/battery/load")
async def load_battery_data():
    try:
        # Leer datos del CSV
        data = pd.read_csv('battery_data.csv')
        # Asegurarse de que las columnas estén presentes
        if 'Timestamp' in data.columns and 'Battery_Level' in data.columns and 'Battery_Capacity_kW' in data.columns:
            # Renombrar columnas si es necesario
            data.rename(columns={'Timestamp': 'timestamp', 'Battery_Level': 'battery_level', 
                                 'Battery_Capacity_kW': 'battery_capacity_kW', 'Energy_Available_kW': 'energy_available_kW'}, inplace=True)
            # Convertir el timestamp a formato datetime
            data["timestamp"] = pd.to_datetime(data["timestamp"])
            # Si falta la columna 'energy_available_kW', calcularla
            if 'energy_available_kW' not in data.columns:
                data["energy_available_kW"] = (data["battery_level"] / 100) * data["battery_capacity_kW"]
            # Convertir el DataFrame en lista de diccionarios y agregar a los datos existentes
            valid_data = data.to_dict(orient='records')
            battery_data.extend(valid_data)
            return {"message": "Battery data loaded from CSV"}
        else:
            return {"error": "CSV file must include 'Timestamp', 'Battery_Level', and 'Battery_Capacity_kW' columns."}
    except Exception as e:
        return {"error": str(e)}
    
"""
Para hacer update del status de la bateria:
curl -X POST "http://127.0.0.1:8000/battery/status" -H "Content-Type: application/json" -d '{"energy_available_kW": 8.5, "battery_capacity_kW": 10}'
--------------------------------------------------------------------------------------------------

Este endpoint devuelve el último estado de la batería que se haya registrado, incluyendo el timestamp, el porcentaje de carga (battery_level), la capacidad total (battery_capacity_kW), y la energía disponible en kW (energy_available_kW).
curl -X GET "http://127.0.0.1:8000/battery/current"
--------------------------------------------------------------------------------------------------

Este endpoint permite recuperar el historial de datos de la batería en función de un delta de tiempo. Usa parámetros como 1d (último día), 2h (últimas dos horas), 30m (últimos 30 minutos
Ej, Un dia
curl -X GET "http://127.0.0.1:8000/battery/history?delta=1d"

Una hora
curl -X GET "http://127.0.0.1:8000/battery/history?delta=1h"

--------------------------------------------------------------------------------------------------
Este endpoint es para cargar los datos de la bateria, a la memoria y poderlos visualizar con los otros comandos
*Este endpoint se debe cambiar para manejar los datos en la base de datos de la aplicacion, aca carga un CSV con datos inventados

curl -X POST "http://127.0.0.1:8000/battery/load"

"""

