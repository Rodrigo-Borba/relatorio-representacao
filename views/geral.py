import streamlit as st
import locale
import pandas as pd
import calendar
from datetime import datetime
import plotly.express as px

locale.setlocale(locale.LC_ALL, 'pt_BR')

st.set_page_config(page_title="Geral",
                   layout="wide")

st.title(":material/home: Geral")
st.markdown("##")

df_vendas = st.session_state.df_vendas.copy()
df_despesas = st.session_state.df_despesas.copy()

df_vendas["data"] = pd.to_datetime(df_vendas["data"])
df_vendas["mes"] = df_vendas["data"].dt.month
df_vendas["mes_nome"] = df_vendas["mes"].apply(lambda x: calendar.month_name[x].capitalize())
df_vendas["ano"] = df_vendas["data"].dt.year

df_despesas["data"] = pd.to_datetime(df_despesas["data"])
df_despesas["mes"] = df_despesas["data"].dt.month
df_despesas["mes_nome"] = df_despesas["mes"].apply(lambda x: calendar.month_name[x].capitalize())
df_despesas["ano"] = df_despesas["data"].dt.year

mes_atual = datetime.now().strftime("%B")
mes_atual = mes_atual.capitalize()
ano_atual = datetime.now().year

vendas_mes_atual = df_vendas[(df_vendas["mes_nome"] == mes_atual) & (df_vendas["ano"] == ano_atual)]["comissao"].sum()
despesas_mes_atual = df_despesas[(df_despesas["mes_nome"] == mes_atual) & (df_despesas["ano"] == ano_atual)][
    "valor"].sum()

saldo_mes_atual = vendas_mes_atual - despesas_mes_atual
saldo_mes_atual = round(saldo_mes_atual, 2)
saldo_mes_atual = locale.currency(saldo_mes_atual, grouping=True)

with st.container(border=True):
    st.header("Saldo atual")
    st.subheader(saldo_mes_atual)

st.divider()

# Despesa mensal
df_valor_mes = df_despesas[["mes", "mes_nome", "valor"]]
df_valor_mes = df_valor_mes.groupby(["mes_nome", "mes"], as_index=False).sum()
df_valor_mes.sort_values("mes", inplace=True)

col1, col2 = st.columns(2)

fig_valor_mes_linha = px.line(df_valor_mes, x="mes_nome", y="valor",
                              title="Despesa mensal",
                              labels={"mes_nome": "Mês", "valor": "Valor (R$)"})

col1.plotly_chart(fig_valor_mes_linha)

fig_valor_mes_barra = px.bar(df_valor_mes, x="mes_nome", y="valor", title="Despesa Mensal",
                             color='mes_nome',
                             color_discrete_sequence=px.colors.sequential.Plasma,
                             labels={"mes_nome": "Mês", "valor": "Valor (R$)"})

col2.plotly_chart(fig_valor_mes_barra)

st.divider()

VISUALIZACAO_GRAFICOS = [
    "Período",
    "Mensal",
    "Percentual"
]

# Despesas por categoria
st.subheader("Despesas por categoria")

filtro_col1, filtro_col2 = st.columns(2)

with filtro_col1:
    ano_filtro = st.selectbox("Ano", df_despesas["ano"].unique())

with filtro_col2:
    meses_filtro = st.multiselect("Mês", [calendar.month_name[x].capitalize() for x in range(1, 13)],
                                  placeholder="Escolher os meses", default=[mes_atual])

df_despesas_filtradas = df_despesas[(df_despesas["mes_nome"].isin(meses_filtro)) & (df_despesas["ano"] == ano_filtro)]

meses_selecionados = df_despesas_filtradas["mes_nome"].unique()

df_categoria_total = df_despesas_filtradas[["categoria", "valor"]]
df_categoria_mes = df_despesas_filtradas[["mes", "mes_nome", "categoria", "valor"]]

df_categoria_total = df_categoria_total.groupby(["categoria"], as_index=False).sum()
df_categoria_total.sort_values("categoria", inplace=True)

df_categoria_mes = df_categoria_mes.groupby(["mes", "mes_nome", "categoria"], as_index=False).sum()
df_categoria_mes.sort_values("mes", inplace=True)

df_categoria_perc = df_categoria_total
valor_categoria_tot = df_categoria_total["valor"].sum()
df_categoria_perc["percentual"] = df_categoria_perc["valor"].apply(
    lambda x: round((100 * float(x) / float(valor_categoria_tot)), 2))

fig_categoria_total = px.bar(df_categoria_mes, x="categoria", y="valor", title="Soma por categoria - Período",
                             color='categoria', color_discrete_sequence=px.colors.sequential.Plasma,
                             labels={"categoria": "Categoria", "valor": "Valor (R$)"})

fig_categoria_mes = px.histogram(df_categoria_mes, x="mes_nome", y="valor", title="Soma por categoria - Mensal",
                                 color='categoria', barmode="group",
                                 color_discrete_sequence=px.colors.sequential.Plasma,
                                 category_orders={
                                     "mes_nome": meses_selecionados},
                                 labels={"mes_nome": "Mês", "categoria": "Categoria", "valor": "Valor (R$)"})

fig_categoria_perc = px.pie(df_categoria_perc, values="percentual", names="categoria",
                            title="Percentual categoria - período",
                            color_discrete_sequence=px.colors.sequential.Plasma,
                            labels={"percentual": "Percentual", "categoria": "Categoria"})

vis_categoria = st.selectbox(label="Selecionar visualização - Categoria", options=VISUALIZACAO_GRAFICOS)
if vis_categoria == "Período":
    st.plotly_chart(fig_categoria_total)
elif vis_categoria == "Mensal":
    st.plotly_chart(fig_categoria_mes)
else:
    st.plotly_chart(fig_categoria_perc)

st.divider()
