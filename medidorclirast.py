"""
DASHBOARD CLIMÁTICO CON DASH (actualización en tiempo real)
Requiere: pip install dash dash-bootstrap-components plotly
"""

import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import numpy as np
from collections import deque
import threading
import time

# Mismo monitor que antes (adaptado para que sea accesible globalmente)
monitor = ClimateMonitor(ventana=30, dias_totales=365)

# Inicializar la app Dash
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Monitor de Entropía Climática", style={'textAlign': 'center'}),
    dcc.Graph(id='live-graph', style={'height': '80vh'}),
    dcc.Interval(id='graph-update', interval=1000, n_intervals=0)  # actualiza cada 1s
])

@app.callback(
    Output('live-graph', 'figure'),
    [Input('graph-update', 'n_intervals')]
)
def update_graph(n):
    snapshot = monitor.snapshot()
    if snapshot is None:
        return dash.no_update

    vars_list = ['temp', 'precip', 'humedad']
    nombres = {'temp': 'Temperatura', 'precip': 'Precipitación', 'humedad': 'Humedad'}
    colores = {'temp': '#e74c3c', 'precip': '#3498db', 'humedad': '#2ecc71'}

    # Crear figura con subplots
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{'type': 'bar'}, {'type': 'scatter'}],
               [{'type': 'scatter'}, {'type': 'table'}]],
        subplot_titles=('Entropía actual', 'Serie temporal',
                        'Evolución entropía sistema', 'Métricas'),
        column_widths=[0.5, 0.5],
        row_heights=[0.5, 0.5]
    )

    # Barras de entropía
    entropias = [snapshot[var]['entropia'] for var in vars_list]
    fig.add_trace(go.Bar(x=[nombres[var] for var in vars_list], y=entropias,
                         marker_color=[colores[var] for var in vars_list]), row=1, col=1)

    # Serie temporal (datos acumulados)
    for var in vars_list:
        fig.add_trace(go.Scatter(x=list(range(len(monitor.datos_acumulados[var]))),
                                  y=monitor.datos_acumulados[var],
                                  mode='lines', name=nombres[var],
                                  line=dict(color=colores[var])), row=1, col=2)

    # Evolución entropía sistema
    fig.add_trace(go.Scatter(x=list(range(len(monitor.entropy_history))),
                              y=list(monitor.entropy_history),
                              mode='lines', line=dict(color='cyan')), row=2, col=1)

    # Tabla
    ultimos = [snapshot[var]['ultimo'] for var in vars_list]
    medias = [snapshot[var]['media'] for var in vars_list]
    desviaciones = [snapshot[var]['std'] for var in vars_list]
    fig.add_trace(go.Table(
        header=dict(values=['Variable', 'Último', 'Media', 'Desviación', 'Entropía'],
                    fill_color='#2c3e50',
                    font=dict(color='white', size=12),
                    align='center'),
        cells=dict(values=[
            [nombres[var] for var in vars_list],
            [f"{ult:.1f} °C" if var=='temp' else f"{ult:.1f} mm" if var=='precip' else f"{ult:.1f} %" for var, ult in zip(vars_list, ultimos)],
            [f"{med:.1f}" for med in medias],
            [f"{std:.2f}" for std in desviaciones],
            [f"{ent:.3f}" for ent in entropias]
        ],
        fill_color='#34495e',
        font=dict(color='white', size=11),
        align='center')
    ), row=2, col=2)

    fig.update_layout(template='plotly_dark', height=800, showlegend=False)
    fig.update_xaxes(title_text='Días', row=1, col=2)
    fig.update_yaxes(title_text='Valor', row=1, col=2)
    fig.update_xaxes(title_text='Muestras', row=2, col=1)
    fig.update_yaxes(title_text='Entropía media', row=2, col=1, range=[0,1])

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)