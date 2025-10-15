import flet as ft
import pandas as pd
import joblib
import plotly.graph_objects as go
from flet.plotly_chart import PlotlyChart
from pathlib import Path

# --- Configurações Iniciais ---
# Construir caminhos robustos a partir da localização do script
APP_DIR = Path(__file__).parent
PROJECT_ROOT = APP_DIR.parent

# Carregar o modelo e os dados (simulados para este exemplo)
# Em um cenário real, estes seriam os arquivos gerados pelo notebook de modelagem.
try:
    model = joblib.load(PROJECT_ROOT / 'model.pkl')
    df = pd.read_csv(PROJECT_ROOT / 'data/processed/violencia_tratado.csv')
    df['ano'] = pd.to_datetime(df['ano'], format='%Y')
except FileNotFoundError:
    # Criar dados dummy caso os arquivos não existam
    print("AVISO: Arquivo model.pkl ou dados tratados não encontrados. Usando dados simulados.")
    model = None
    data = {
        'ano': pd.to_datetime(['2018', '2019', '2020', '2021', '2022']),
        'estado': ['SP', 'SP', 'SP', 'SP', 'SP'],
        'tipo_violencia': ['Doméstica', 'Doméstica', 'Doméstica', 'Doméstica', 'Doméstica'],
        'faixa_etaria': ['20-29 anos', '20-29 anos', '20-29 anos', '20-29 anos', '20-29 anos'],
        'casos': [100, 110, 120, 115, 130],
        'idhm': [0.78, 0.79, 0.80, 0.81, 0.82],
        'taxa_desemprego': [12.0, 11.5, 13.0, 14.0, 11.0],
        'renda_media': [1500, 1550, 1600, 1580, 1650]
    }
    df = pd.DataFrame(data)


# --- Funções Auxiliares ---
def criar_grafico_previsao(df_filtrado, previsoes=None):
    """Cria um gráfico Plotly com dados históricos e previsões."""
    fig = go.Figure()

    # Linha de dados históricos
    fig.add_trace(go.Scatter(
        x=df_filtrado['ano'],
        y=df_filtrado['casos'],
        mode='lines+markers',
        name='Histórico de Casos',
        line=dict(color='#1f77b4')
    ))

    # Linha de previsão
    if previsoes:
        anos_previsao = pd.to_datetime([df_filtrado['ano'].max() + pd.DateOffset(years=i) for i in range(1, len(previsoes) + 1)])
        fig.add_trace(go.Scatter(
            x=anos_previsao,
            y=previsoes,
            mode='lines+markers',
            name='Previsão',
            line=dict(color='#ff7f0e', dash='dash')
        ))

    fig.update_layout(
        title="Histórico e Previsão de Casos de Violência",
        xaxis_title="Ano",
        yaxis_title="Número de Casos",
        legend_title="Legenda",
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white")
    )
    return fig


def main(page: ft.Page):
    page.title = "Previsão de Violência no Brasil"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.window_width = 1200
    page.window_height = 800

    # --- Componentes da UI ---
    titulo = ft.Text("Painel de Análise e Previsão de Violência", size=32, weight=ft.FontWeight.BOLD)
    
    # Filtros
    dd_tipo_violencia = ft.Dropdown(
        label="Tipo de Violência",
        options=[ft.dropdown.Option(v) for v in df['tipo_violencia'].unique()],
        value=df['tipo_violencia'].unique()[0],
        width=250
    )
    dd_estado = ft.Dropdown(
        label="Estado",
        options=[ft.dropdown.Option(e) for e in df['estado'].unique()],
        value=df['estado'].unique()[0],
        width=250
    )
    dd_faixa_etaria = ft.Dropdown(
        label="Faixa Etária",
        options=[ft.dropdown.Option(f) for f in df['faixa_etaria'].unique()],
        value=df['faixa_etaria'].unique()[0],
        width=250
    )

    # Gráfico
    chart = PlotlyChart(expand=True)

    # Controles de Simulação
    slider_renda = ft.Slider(min=0.5, max=1.5, divisions=20, value=1.0, label="Renda Média ({value}x)")
    slider_desemprego = ft.Slider(min=0.5, max=1.5, divisions=20, value=1.0, label="Desemprego ({value}x)")
    texto_resultado_simulacao = ft.Text("", size=16, weight=ft.FontWeight.W_500, color=ft.Colors.YELLOW_ACCENT)

    # --- Lógica de Atualização ---
    def atualizar_interface(e):
        # 1. Filtrar dados com base nos dropdowns
        df_filtrado = df[
            (df['tipo_violencia'] == dd_tipo_violencia.value) &
            (df['estado'] == dd_estado.value) &
            (df['faixa_etaria'] == dd_faixa_etaria.value)
        ].sort_values('ano')

        if df_filtrado.empty:
            chart.figure = go.Figure().update_layout(title="Sem dados para a seleção atual", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
            texto_resultado_simulacao.value = ""
            page.update()
            return

        # 2. Preparar dados para previsão
        # Usar os valores mais recentes como base para a simulação
        last_known_data = df_filtrado.iloc[-1]
        renda_simulada = last_known_data['renda_media'] * slider_renda.value
        desemprego_simulado = last_known_data['taxa_desemprego'] * slider_desemprego.value
        idhm_simulado = last_known_data['idhm'] # Simplificação: IDHM mantido constante

        # Criar features para os próximos 3 anos
        features_previsao = pd.DataFrame({
            'idhm': [idhm_simulado] * 3,
            'taxa_desemprego': [desemprego_simulado] * 3,
            'renda_media': [renda_simulada] * 3
        })

        # 3. Fazer a previsão
        previsoes = None
        if model:
            previsoes = model.predict(features_previsao)
            # Lógica de simulação
            previsao_base = model.predict(pd.DataFrame({
                'idhm': [last_known_data['idhm']],
                'taxa_desemprego': [last_known_data['taxa_desemprego']],
                'renda_media': [last_known_data['renda_media']]
            }))[0]
            
            previsao_simulada = previsoes[0]
            variacao_percentual = ((previsao_simulada - previsao_base) / previsao_base) * 100
            
            cor_texto = ft.Colors.GREEN_ACCENT if variacao_percentual < 0 else ft.Colors.RED_ACCENT
            sinal = "redução" if variacao_percentual < 0 else "aumento"
            texto_resultado_simulacao.value = f"A simulação prevê uma {sinal} de {abs(variacao_percentual):.2f}% nos casos."
            texto_resultado_simulacao.color = cor_texto

        # 4. Atualizar o gráfico
        chart.figure = criar_grafico_previsao(df_filtrado, previsoes)
        page.update()

    # --- Layout da Página ---
    dd_tipo_violencia.on_change = atualizar_interface
    dd_estado.on_change = atualizar_interface
    dd_faixa_etaria.on_change = atualizar_interface
    slider_renda.on_change_end = atualizar_interface
    slider_desemprego.on_change_end = atualizar_interface

    page.add(
        titulo,
        ft.Row([dd_tipo_violencia, dd_estado, dd_faixa_etaria], alignment=ft.MainAxisAlignment.CENTER),
        ft.Divider(),
        ft.Column([chart], expand=True),
        ft.Divider(),
        ft.Text("Simulador de Cenários", size=20, weight=ft.FontWeight.BOLD),
        ft.Text("Ajuste os indicadores socioeconômicos para ver o impacto na previsão do próximo ano."),
        ft.Row([ft.Text("Renda Média:", width=120), slider_renda], vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ft.Row([ft.Text("Desemprego:", width=120), slider_desemprego], vertical_alignment=ft.CrossAxisAlignment.CENTER),
        texto_resultado_simulacao
    )

    # Carga inicial
    atualizar_interface(None)

ft.app(target=main)