"""
MONITOR DE ENTROPÍA CLIMÁTICA - Versión mejorada con matplotlib moderno
No requiere pandas, solo numpy y matplotlib.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
import matplotlib.animation as animation
from collections import deque

# Configurar estilo más moderno
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.facecolor'] = '#2b2b2b'
plt.rcParams['axes.facecolor'] = '#3c3c3c'
plt.rcParams['text.color'] = 'white'
plt.rcParams['axes.labelcolor'] = 'white'
plt.rcParams['xtick.color'] = 'white'
plt.rcParams['ytick.color'] = 'white'

# -------------------------------------------------------------------
# GENERADOR DE DATOS (igual que antes)
# -------------------------------------------------------------------
def generador_clima(dias=365):
    t = np.arange(dias)
    temp_base = 15 + 10 * np.sin(2 * np.pi * t / 365)
    temp_ruido = np.random.normal(0, 3, dias)
    temp = temp_base + temp_ruido
    precip = np.random.gamma(2, 2, dias)
    hum_base = 70 + 10 * np.sin(2 * np.pi * t / 365 + 1)
    hum_ruido = np.random.normal(0, 5, dias)
    humedad = hum_base + hum_ruido
    for i in range(dias):
        yield temp[i], precip[i], humedad[i]

# -------------------------------------------------------------------
# MONITOR (igual que antes)
# -------------------------------------------------------------------
class ClimateMonitor:
    def __init__(self, ventana=30, dias_totales=365):
        self.ventana = ventana
        self.generador = generador_clima(dias_totales)
        self.variables = ['temp', 'precip', 'humedad']
        self.historial = {var: deque(maxlen=ventana) for var in self.variables}
        self.indice = 0
        self.entropy_history = deque(maxlen=100)
        self.datos_acumulados = {var: [] for var in self.variables}

    def siguiente_muestra(self):
        try:
            temp, precip, hum = next(self.generador)
        except StopIteration:
            return None
        self.historial['temp'].append(temp)
        self.historial['precip'].append(precip)
        self.historial['humedad'].append(hum)
        self.datos_acumulados['temp'].append(temp)
        self.datos_acumulados['precip'].append(precip)
        self.datos_acumulados['humedad'].append(hum)
        self.indice += 1
        return {var: list(self.historial[var]) for var in self.variables}

    def shannon_entropy(self, data, bins=10):
        if len(data) < bins:
            return 0.0
        hist, _ = np.histogram(data, bins=bins)
        probs = hist / len(data)
        probs = probs[probs > 0]
        if len(probs) == 0:
            return 0.0
        return -np.sum(probs * np.log2(probs)) / np.log2(bins)

    def snapshot(self):
        if self.indice == 0:
            self.siguiente_muestra()
        datos_actuales = self.siguiente_muestra()
        if datos_actuales is None:
            return None

        resultado = {}
        entropias = []
        for var, serie in datos_actuales.items():
            ent = self.shannon_entropy(serie)
            entropias.append(ent)
            resultado[var] = {
                'entropia': ent,
                'ultimo': serie[-1] if serie else None,
                'media': np.mean(serie) if serie else None,
                'std': np.std(serie, ddof=1) if len(serie) > 1 else 0.0
            }
        sys_ent = np.mean(entropias) if entropias else 0.0
        self.entropy_history.append(sys_ent)
        resultado['sistema'] = sys_ent
        return resultado

# -------------------------------------------------------------------
# DASHBOARD MEJORADO (con matplotlib moderno)
# -------------------------------------------------------------------
class ClimateDashboard:
    def __init__(self, monitor):
        self.monitor = monitor
        self.fig = plt.figure(figsize=(14, 9))
        # Especificar una cuadrícula más elaborada
        gs = gridspec.GridSpec(3, 3, figure=self.fig,
                               height_ratios=[1.5, 1, 1.2],
                               width_ratios=[1, 1, 1],
                               hspace=0.3, wspace=0.3)

        self.ax_bar = self.fig.add_subplot(gs[0, :2])   # gráfico de barras (ancho 2/3)
        self.ax_trend = self.fig.add_subplot(gs[0, 2])  # mini tendencia (ancho 1/3)
        self.ax_series = self.fig.add_subplot(gs[1, :]) # serie temporal completa
        self.ax_table = self.fig.add_subplot(gs[2, :])  # tabla

        self.update_interval = 800  # ms

        # Colores agradables
        self.colores = {'temp': '#e74c3c', 'precip': '#3498db', 'humedad': '#2ecc71'}
        self.nombres = {'temp': 'Temperatura', 'precip': 'Precipitación', 'humedad': 'Humedad'}

        # Texto informativo flotante (se actualizará)
        self.info_text = self.fig.text(0.02, 0.98, '', transform=self.fig.transFigure,
                                       fontsize=10, verticalalignment='top',
                                       bbox=dict(boxstyle='round', facecolor='#555555', alpha=0.9))

    def update(self, frame):
        snapshot = self.monitor.snapshot()
        if snapshot is None:
            print("Fin de los datos.")
            plt.close()
            return

        vars_list = ['temp', 'precip', 'humedad']

        # --- Gráfico de barras (entropía actual) ---
        self.ax_bar.clear()
        entropias = [snapshot[var]['entropia'] for var in vars_list]
        bars = self.ax_bar.bar([self.nombres[var] for var in vars_list], entropias,
                                color=[self.colores[var] for var in vars_list],
                                edgecolor='white', linewidth=0.5)
        self.ax_bar.set_ylim(0, 1)
        self.ax_bar.set_ylabel('Entropía (0-1)', fontsize=11)
        self.ax_bar.set_title('Entropía actual por variable', fontsize=12, weight='bold')
        self.ax_bar.axhline(y=0.3, color='white', linestyle='--', linewidth=1, alpha=0.5)
        self.ax_bar.axhline(y=0.6, color='white', linestyle='--', linewidth=1, alpha=0.5)
        # Añadir valores sobre las barras
        for bar, ent in zip(bars, entropias):
            self.ax_bar.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                             f'{ent:.2f}', ha='center', va='bottom', fontsize=9, color='white')

        # --- Mini gráfico de tendencia de la entropía del sistema ---
        self.ax_trend.clear()
        hist = list(self.monitor.entropy_history)
        if hist:
            self.ax_trend.plot(hist, color='cyan', linewidth=2)
            self.ax_trend.fill_between(range(len(hist)), hist, alpha=0.3, color='cyan')
        self.ax_trend.set_ylim(0, 1)
        self.ax_trend.set_title('Entropía sistema', fontsize=10)
        self.ax_trend.set_xlabel('Muestras')
        self.ax_trend.set_ylabel('Media')

        # --- Serie temporal de las variables (datos acumulados) ---
        self.ax_series.clear()
        for var in vars_list:
            datos = self.monitor.datos_acumulados[var]
            if datos:
                self.ax_series.plot(datos, label=self.nombres[var],
                                    color=self.colores[var], linewidth=1.5)
        self.ax_series.set_title('Evolución de las variables', fontsize=12, weight='bold')
        self.ax_series.set_xlabel('Días')
        self.ax_series.set_ylabel('Valor')
        self.ax_series.legend(loc='upper right', framealpha=0.9)
        # Añadir una cuadrícula sutil
        self.ax_series.grid(True, alpha=0.3)

        # --- Tabla de métricas (con estilo mejorado) ---
        self.ax_table.clear()
        self.ax_table.axis('off')
        col_labels = ['Variable', 'Último valor', 'Media (ventana)', 'Desviación', 'Entropía']
        table_data = []
        for var in vars_list:
            ult = snapshot[var]['ultimo']
            media = snapshot[var]['media']
            std = snapshot[var]['std']
            ent = snapshot[var]['entropia']
            if var == 'temp':
                ult_str = f"{ult:.1f} °C"
                media_str = f"{media:.1f} °C"
            elif var == 'precip':
                ult_str = f"{ult:.1f} mm"
                media_str = f"{media:.1f} mm"
            else:
                ult_str = f"{ult:.1f} %"
                media_str = f"{media:.1f} %"
            table_data.append([self.nombres[var], ult_str, media_str, f"{std:.2f}", f"{ent:.3f}"])

        # Crear tabla con colores personalizados
        tabla = self.ax_table.table(cellText=table_data, colLabels=col_labels,
                                    loc='center', cellLoc='center',
                                    colWidths=[0.2, 0.2, 0.2, 0.2, 0.2])
        tabla.auto_set_font_size(False)
        tabla.set_fontsize(10)
        # Dar formato a celdas
        for (i, j), cell in tabla.get_celld().items():
            if i == 0:  # encabezados
                cell.set_facecolor('#1f618d')
                cell.set_text_props(color='white', weight='bold')
            else:
                cell.set_facecolor('#2c3e50')
                cell.set_text_props(color='white')
                # Alternar color de fondo sutilmente para mejorar legibilidad
                if i % 2 == 0:
                    cell.set_facecolor('#3a4a5a')
        self.ax_table.set_title('Métricas detalladas (ventana deslizante)', fontsize=12, weight='bold', pad=10)

        # Actualizar texto informativo
        self.info_text.set_text(f"Día: {self.monitor.indice}   |   Entropía sistema: {snapshot['sistema']:.3f}")

        plt.tight_layout()

    def start(self):
        ani = animation.FuncAnimation(self.fig, self.update, interval=self.update_interval,
                                      cache_frame_data=False)
        plt.show()

# -------------------------------------------------------------------
# EJECUCIÓN
# -------------------------------------------------------------------
if __name__ == "__main__":
    # Si no tienes matplotlib instalado: pip install matplotlib numpy
    monitor = ClimateMonitor(ventana=30, dias_totales=365)
    dashboard = ClimateDashboard(monitor)
    dashboard.start()