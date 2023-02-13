import plotly.express as px
def grafico_historico(table_returns):
    grafico = px.line(table_returns.Capital, title="Historico del portafolio")
    return grafico






