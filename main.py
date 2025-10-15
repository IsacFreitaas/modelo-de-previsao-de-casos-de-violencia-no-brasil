import flet as ft
import pandas as pd
import joblib
import plotly.graph_objects as go
from flet.plotly_chart import PlotlyChart
from pathlib import Path

# --- Configurações Iniciais ---
PROJECT_ROOT = Path(__file__).parent 

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
        'estado': ['SP'] * 20,
        'categoria_violencia': ['Física'] * 20,
        'faixa_etaria': ['20-29 anos'] * 20,
        'genero': (['Mulher']*10 + ['Homem']*10),
        'orientacao_sexual': ['Heterossexual'] * 20,
        'casos': [100, 110, 120, 115, 130, 50, 55, 60, 58, 65] * 2,
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
    if previsoes is not None:
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
        paper_bgcolor='rgba(255,255,255,1)',
        plot_bgcolor='rgba(245,245,245,1)',
        font=dict(color="black")
    )
    return fig


def main(page: ft.Page):
    page.title = "Previsão de Violência no Brasil"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.window_width = 1200
    page.window_height = 800

    # --- Componentes da UI ---
    titulo = ft.Text("Painel de Análise e Previsão de Violência", size=32, weight=ft.FontWeight.BOLD)
    
    # Filtros
    dd_categoria_violencia = ft.Dropdown(
        label="Categoria de Violência",
        options=[ft.dropdown.Option(v) for v in df['categoria_violencia'].unique()],
        value=df['categoria_violencia'].unique()[0],
        width=250
    )
    dd_estado = ft.Dropdown(
        label="Estado",
        options=[ft.dropdown.Option(e) for e in df['estado'].unique()],
        value=df['estado'].unique()[0],
        width=150
    )
    dd_faixa_etaria = ft.Dropdown(
        label="Faixa Etária",
        options=[ft.dropdown.Option(f) for f in df['faixa_etaria'].unique()],
        value=df['faixa_etaria'].unique()[0],
        width=200
    )
    dd_genero = ft.Dropdown(
        label="Gênero",
        options=[ft.dropdown.Option("Ambos")] + [ft.dropdown.Option(g) for g in df['genero'].unique()],
        value="Ambos",
        width=150
    )
    dd_orientacao = ft.Dropdown(
        label="Orientação Sexual",
        options=[ft.dropdown.Option("Todas")] + [ft.dropdown.Option(o) for o in df['orientacao_sexual'].unique()],
        value="Todas",
        width=200
    )
    dd_ano = ft.Dropdown(
        label="Ano (para simulação)",
        options=[ft.dropdown.Option(str(y)) for y in sorted(df['ano'].dt.year.unique(), reverse=True)],
        value=str(df['ano'].dt.year.max()),
        width=200
    )

    # Gráfico
    chart = PlotlyChart(expand=True)

    # Controles de Simulação
    sim_button = ft.ElevatedButton(text="Simular Cenário", icon=ft.Icons.INSIGHTS_ROUNDED)
    slider_renda = ft.Slider(min=0.5, max=1.5, divisions=20, value=1.0, label="Renda Média ({value}x)")
    slider_desemprego = ft.Slider(min=0.5, max=1.5, divisions=20, value=1.0, label="Desemprego ({value}x)")
    texto_resultado_simulacao = ft.Text("", size=16, weight=ft.FontWeight.W_500, color=ft.Colors.BLUE_GREY_700)

    # --- Lógica de Atualização ---
    def atualizar_grafico(e):
        """Atualiza apenas o gráfico com base nos filtros principais."""
        filtros = (
            (df['categoria_violencia'] == dd_categoria_violencia.value) &
            (df['estado'] == dd_estado.value) &
            (df['faixa_etaria'] == dd_faixa_etaria.value)
        )
        if dd_genero.value != "Ambos":
            filtros &= (df['genero'] == dd_genero.value)
        if dd_orientacao.value != "Todas":
            filtros &= (df['orientacao_sexual'] == dd_orientacao.value)

        df_filtrado = df[filtros]

        # Agrupar por ano para o gráfico de série temporal
        df_agrupado = df_filtrado.groupby(df_filtrado['ano'].dt.year)['casos'].sum().reset_index()
        df_agrupado['ano'] = pd.to_datetime(df_agrupado['ano'], format='%Y')

        if df_agrupado.empty:
            chart.figure = go.Figure().update_layout(title="Sem dados para a seleção atual", paper_bgcolor='rgba(255,255,255,1)', plot_bgcolor='rgba(245,245,245,1)', font=dict(color="black"))
        else:
            chart.figure = criar_grafico_previsao(df_agrupado)
        
        page.update()

    def executar_simulacao(e):
        """Executa a simulação e atualiza o texto de resultado."""
        # 1. Filtrar dados para obter a base da simulação
        df_filtrado = df[
            (df['categoria_violencia'] == dd_categoria_violencia.value) &
            (df['estado'] == dd_estado.value) &
            (df['faixa_etaria'] == dd_faixa_etaria.value) &
            (df['ano'].dt.year == int(dd_ano.value))
        ]

        if df_filtrado.empty:
            texto_resultado_simulacao.value = f"Não há dados para simulação no ano de {dd_ano.value}."
            texto_resultado_simulacao.color = ft.Colors.RED_700
            page.update()
            return

        # 2. Preparar dados para previsão
        # Usar os valores mais recentes como base para a simulação
        # Usamos a média dos indicadores do ano selecionado para a simulação
        last_known_data = df_filtrado[['idhm', 'taxa_desemprego', 'renda_media']].mean()

        renda_simulada = last_known_data['renda_media'] * slider_renda.value
        desemprego_simulado = last_known_data['taxa_desemprego'] * slider_desemprego.value
        idhm_simulado = last_known_data['idhm'] # Simplificação: IDHM mantido constante

        # Criar features para o próximo ano
        features_previsao = pd.DataFrame({
            'idhm': [idhm_simulado],
            'taxa_desemprego': [desemprego_simulado],
            'renda_media': [renda_simulada]
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
            # Evitar divisão por zero
            variacao_percentual = ((previsao_simulada - previsao_base) / previsao_base) * 100 if previsao_base != 0 else 0
            
            cor_texto = ft.Colors.GREEN_700 if variacao_percentual < 0 else ft.Colors.RED_700
            sinal = "redução" if variacao_percentual < 0 else "aumento"
            texto_resultado_simulacao.value = f"A simulação prevê uma {sinal} de {abs(variacao_percentual):.2f}% nos casos."
            texto_resultado_simulacao.color = cor_texto
        else:
            texto_resultado_simulacao.value = "Modelo não carregado. Simulação indisponível."
            texto_resultado_simulacao.color = ft.Colors.ORANGE_700

        page.update()

    # --- Layout da Página ---
    dd_categoria_violencia.on_change = atualizar_grafico
    dd_estado.on_change = atualizar_grafico
    dd_faixa_etaria.on_change = atualizar_grafico
    dd_genero.on_change = atualizar_grafico
    dd_orientacao.on_change = atualizar_grafico
    sim_button.on_click = executar_simulacao

    page.add(
        titulo,
        ft.Row([dd_categoria_violencia, dd_estado, dd_faixa_etaria, dd_genero, dd_orientacao], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
        ft.Divider(),
        ft.Column([chart], expand=True),
        ft.Divider(),
        ft.Text("Simulador de Cenários", size=20, weight=ft.FontWeight.BOLD),
        ft.Text("Ajuste os indicadores e clique em 'Simular' para ver o impacto na previsão do próximo ano."),
        ft.Row([
            ft.Column([
                ft.Row([ft.Text("Renda Média:", width=120), slider_renda], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Row([ft.Text("Desemprego:", width=120), slider_desemprego], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], expand=True),
            ft.Column([dd_ano, sim_button, texto_resultado_simulacao], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
    )

    # Carga inicial
    atualizar_grafico(None)

ft.app(target=main)