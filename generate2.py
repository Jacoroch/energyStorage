import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configuración para generar datos de 2 días, con lecturas cada minuto hasta la fecha actual
end_time = datetime.now()
start_time = end_time - timedelta(days=2)
timestamps = [start_time + timedelta(minutes=i) for i in range(2 * 24 * 60)]

# Configuración inicial para la generación de datos de energía
battery_level = 50  # Nivel inicial en porcentaje
battery_capacity_kW = 10  # Capacidad total de la batería en kW (puedes variar este valor para simular diferentes capacidades)
battery_levels = []
energy_available_kW = []

# Simulación de datos: cargar durante el día y descargar durante la noche
for timestamp in timestamps:
    hour = timestamp.hour
    if 8 <= hour <= 17:  # Día (carga)
        if 10 <= hour <= 14:  # Hora pico de carga (sol fuerte)
            change = np.random.uniform(0.2, 0.5)  # Más energía recibida
        else:
            change = np.random.uniform(0.1, 0.3)  # Energía moderada
        battery_level = min(100, battery_level + change)  # No superar 100%
    else:  # Noche (descarga)
        change = np.random.uniform(0.1, 0.4)  # Consumo constante
        battery_level = max(20, battery_level - change)  # No bajar de 20%

    # Calcular la energía disponible en kW
    energy_in_kW = (battery_level / 100) * battery_capacity_kW

    # Guardar los valores
    battery_levels.append(round(battery_level, 2))
    energy_available_kW.append(round(energy_in_kW, 2))

# Crear DataFrame con las nuevas columnas
data = pd.DataFrame({
    'Timestamp': timestamps,
    'Battery_Level': battery_levels,
    'Battery_Capacity_kW': battery_capacity_kW,  # Capacidad fija para todos, puede variar según implementación
    'Energy_Available_kW': energy_available_kW
})

# Guardar datos en un archivo CSV
data.to_csv('battery_data.csv', index=False)
print("Datos generados y guardados en 'battery_data_realistic_with_energy.csv'")