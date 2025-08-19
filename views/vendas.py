import plotly.express as px
import pandas as pd
import streamlit as st
import calendar
from datetime import datetime
import locale
from planilha import Planilha

locale.setlocale(locale.LC_ALL, 'pt_BR')

st.markdown("""
    <style>
        .st-emotion-cache-7czcpc img{
            border-radius: 50%;
            margin-bottom: 4rem;
        }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title=st.session_state.titulo,
                   layout="wide")

df_vendas = st.session_state.df_vendas.copy()

df_vendas["data"] = pd.to_datetime(df_vendas["data"])
df_vendas["mes"] = df_vendas["data"].dt.month
df_vendas["mes_nome"] = df_vendas["mes"].apply(lambda x: calendar.month_name[x].capitalize())
df_vendas["ano"] = df_vendas["data"].dt.year

mes_atual = datetime.now().strftime("%B")
mes_atual = mes_atual.capitalize()
ano_atual = datetime.now().year

# TOP KPI's
st.title(f":material/paid: {st.session_state.titulo}")
st.markdown("##")

st.subheader("Filtro:")

filtro_col1, filtro_col2 = st.columns(2)

with filtro_col1:
    ano = st.selectbox("Ano", df_vendas["ano"].unique())

with filtro_col2:
    mes = st.multiselect("Mês", [calendar.month_name[x].capitalize() for x in range(1, 13)],
                         placeholder="Escolher os meses", default=[mes_atual])

st.markdown("---")

df_vendas_filtro = df_vendas[(df_vendas["mes_nome"].isin(mes)) & (df_vendas["ano"] == ano)]
df_vendas_filtro.sort_values("data", inplace=True)

meses_selecionados = df_vendas_filtro["mes_nome"].unique()

VISUALIZACAO_GRAFICOS = [
    "Período",
    "Mensal",
    "Percentual"
]

VISUALIZACAO_GRAFICOS_COM_MAPA = [
    "Período",
    "Mensal",
    "Percentual",
    "Mapa"
]

# Valores de venda no período selecionado
vendas_total = int(df_vendas_filtro[st.session_state.valor].sum())
if vendas_total > 0:
    vendas_media = round(vendas_total / len(mes), 2)
else:
    vendas_media = 0

vendas_total = locale.currency(vendas_total, grouping=True, symbol=None)
vendas_media = locale.currency(vendas_media, grouping=True, symbol=None)

coluna_esquerda, coluna_direita = st.columns(2)

with coluna_esquerda:
    with st.container(border=True):
        st.subheader(f"Total de {st.session_state.titulo}:")
        st.subheader(f"R$ {vendas_total}")
with coluna_direita:
    with st.container(border=True):
        st.subheader(f"Média de {st.session_state.titulo}:")
        st.subheader(f"R$ {vendas_media}")

st.divider()

if st.session_state.valor == "valor":
    st.subheader('Últimas compras por loja')

    with st.expander("Última compra"):
        selecao_loja = st.selectbox(label="Loja", options=df_vendas['loja'].unique(), index=None)
        if selecao_loja:
            df_lojas_ultimas_compras = df_vendas.iloc[df_vendas.groupby(['loja', 'fabrica'])['data'].idxmax()]
            df_fabricas_por_loja = df_lojas_ultimas_compras[df_lojas_ultimas_compras["loja"] == selecao_loja]
            selecao_fabrica = st.selectbox(label="Fábrica", options=df_fabricas_por_loja['fabrica'].unique(),
                                           index=None)

            if selecao_fabrica:
                data_ultima_compra = str(
                    df_fabricas_por_loja[df_fabricas_por_loja['fabrica'] == selecao_fabrica].data.dt.strftime(
                        "%d de %B de %Y").values[
                        0])
                fabrica_ultima_compra = str(
                    df_fabricas_por_loja[df_fabricas_por_loja['fabrica'] == selecao_fabrica].fabrica.values[0])
                valor_ultima_compra = \
                    df_fabricas_por_loja[df_fabricas_por_loja['fabrica'] == selecao_fabrica][
                        st.session_state.valor].values[0]
                valor_ultima_compra = locale.currency(valor_ultima_compra, grouping=True, symbol=None)
                st.subheader(f"Loja: {selecao_loja}")
                st.subheader(
                    f"Data da última compra: {data_ultima_compra}")
                st.subheader(f"Fábrica: {fabrica_ultima_compra}")
                st.subheader(f"Valor: R$ {valor_ultima_compra}")

    st.divider()

index_ultimas_compras = df_vendas.groupby('loja')['data'].idxmax()
df_ultimas_compras = df_vendas.iloc[index_ultimas_compras]

index_ultimas_vendas = df_vendas.groupby('fabrica')['data'].idxmax()
df_ultimas_vendas = df_vendas.iloc[index_ultimas_vendas]

if st.session_state.valor == "valor":
    st.subheader("Última compra/venda")

    ultima_compra_col, ultima_venda_col = st.columns(2)

    with ultima_compra_col:
        with st.expander("Última compra"):
            selecionar_loja = st.selectbox(label="Escolher loja:", options=df_vendas["loja"].unique())
            if selecionar_loja:
                data_ultima_compra = str(
                    df_ultimas_compras[df_ultimas_compras['loja'] == selecionar_loja].data.dt.strftime(
                        "%d de %B de %Y").values[
                        0])
                fabrica_ultima_compra = str(
                    df_ultimas_compras[df_ultimas_compras['loja'] == selecionar_loja].fabrica.values[0])
                valor_ultima_compra = \
                    df_ultimas_compras[df_ultimas_compras['loja'] == selecionar_loja][st.session_state.valor].values[0]
                valor_ultima_compra = locale.currency(valor_ultima_compra, grouping=True, symbol=None)
                st.subheader(f"Loja: {selecionar_loja}")
                st.subheader(
                    f"Data da última compra: {data_ultima_compra}")
                st.subheader(f"Fábrica: {fabrica_ultima_compra}")
                st.subheader(f"Valor: R$ {valor_ultima_compra}")

    with ultima_venda_col:
        with st.expander("Última venda"):
            selecionar_fabrica = st.selectbox(label="Escolher fábrica:", options=df_vendas["fabrica"].unique())
            if selecionar_fabrica:
                data_ultima_venda = str(
                    df_ultimas_vendas[df_ultimas_vendas['fabrica'] == selecionar_fabrica].data.dt.strftime(
                        "%d de %B de %Y").values[
                        0])
                loja_ultima_venda = str(
                    df_ultimas_vendas[df_ultimas_vendas['fabrica'] == selecionar_fabrica].loja.values[0])
                valor_ultima_venda = \
                    df_ultimas_vendas[df_ultimas_vendas['fabrica'] == selecionar_fabrica][
                        st.session_state.valor].values[0]
                valor_ultima_venda = locale.currency(valor_ultima_venda, grouping=True, symbol=None)
                st.subheader(f"Fábrica: {selecionar_fabrica}")
                st.subheader(
                    f"Data da última venda: {data_ultima_venda}")
                st.subheader(f"Loja: {loja_ultima_venda}")
                st.subheader(f"Valor: R$ {valor_ultima_venda}")

    st.markdown("---")

# Gasto total mensal
df_valor_mes = df_vendas_filtro[["mes", "mes_nome", st.session_state.valor]]
df_valor_mes = df_valor_mes.groupby(["mes_nome", "mes"], as_index=False).sum()
df_valor_mes.sort_values("mes", inplace=True)

col1, col2 = st.columns(2)

fig_valor_mes_linha = px.line(df_valor_mes, x="mes_nome", y=st.session_state.valor,
                              title="Soma mensal total por período",
                              labels={"mes_nome": "Mês", st.session_state.valor: "Valor (R$)"})

col1.plotly_chart(fig_valor_mes_linha)

fig_valor_mes_barra = px.bar(df_valor_mes, x="mes_nome", y=st.session_state.valor, title="Soma mensal total",
                             color='mes_nome',
                             color_discrete_sequence=px.colors.sequential.Plasma,
                             labels={"mes_nome": "Mês", st.session_state.valor: "Valor (R$)"})

col2.plotly_chart(fig_valor_mes_barra)

st.divider()

# Vendas por loja
st.subheader(f"{st.session_state.titulo} por loja")
df_loja_total = df_vendas_filtro[["loja", st.session_state.valor]]
df_loja_mes = df_vendas_filtro[["mes", "mes_nome", "loja", st.session_state.valor]]

df_loja_total = df_loja_total.groupby(["loja"], as_index=False).sum()
df_loja_total.sort_values("loja", inplace=True)

df_loja_mes = df_loja_mes.groupby(["mes", "mes_nome", "loja"], as_index=False).sum()
df_loja_mes.sort_values("mes", inplace=True)

df_loja_perc = df_loja_total
valor_loja_tot = df_loja_total[st.session_state.valor].sum()
df_loja_perc["percentual"] = df_loja_perc[st.session_state.valor].apply(
    lambda x: round((100 * float(x) / float(valor_loja_tot)), 2))

fig_loja_total = px.bar(df_loja_total, x="loja", y=st.session_state.valor, title="Soma por loja - Período",
                        color='loja', color_discrete_sequence=px.colors.sequential.Plasma,
                        labels={"loja": "Loja", st.session_state.valor: "Valor (R$)"})

fig_loja_mes = px.histogram(df_loja_mes, x="mes_nome", y=st.session_state.valor, title="Soma por loja - Mensal",
                            color='loja', barmode="group",
                            color_discrete_sequence=px.colors.sequential.Plasma,
                            category_orders={
                                "mes_nome": meses_selecionados},
                            labels={"mes_nome": "Mês", "loja": "Loja", st.session_state.valor: "Valor (R$)"})

fig_loja_perc = px.pie(df_loja_perc, values="percentual", names="loja",
                       title="Percentual loja - período",
                       color_discrete_sequence=px.colors.sequential.Plasma,
                       labels={"percentual": "Percentual", "loja": "Loja"})

vis_loja = st.selectbox(label="Selecionar visualização - Lojas", options=VISUALIZACAO_GRAFICOS)
if vis_loja == "Período":
    st.plotly_chart(fig_loja_total)
elif vis_loja == "Mensal":
    st.plotly_chart(fig_loja_mes)
else:
    st.plotly_chart(fig_loja_perc)

st.divider()

# Vendas por fábrica
st.subheader(f"{st.session_state.titulo} por fábrica")
df_fabrica_total = df_vendas_filtro[["fabrica", st.session_state.valor]]
df_fabrica_mes = df_vendas_filtro[["mes", "mes_nome", "fabrica", st.session_state.valor]]

df_fabrica_total = df_fabrica_total.groupby(["fabrica"], as_index=False).sum()
df_fabrica_total.sort_values("fabrica", inplace=True)

df_fabrica_mes = df_fabrica_mes.groupby(["mes", "mes_nome", "fabrica"], as_index=False).sum()
df_fabrica_mes.sort_values("mes", inplace=True)

df_fabrica_perc = df_fabrica_total
valor_fabrica_tot = df_fabrica_total[st.session_state.valor].sum()
df_fabrica_perc["percentual"] = df_fabrica_perc[st.session_state.valor].apply(
    lambda x: round((100 * float(x) / float(valor_fabrica_tot)), 2))

fig_fabrica_total = px.bar(df_fabrica_total, x="fabrica", y=st.session_state.valor, title="Soma por fábrica - Período",
                           color='fabrica', color_discrete_sequence=px.colors.sequential.Plasma,
                           labels={"fabrica": "Fábrica", st.session_state.valor: "Valor (R$)"})

fig_fabrica_mes = px.histogram(df_fabrica_mes, x="mes_nome", y=st.session_state.valor,
                               title="Soma por fábrica - Mensal",
                               color='fabrica', barmode="group",
                               color_discrete_sequence=px.colors.sequential.Plasma,
                               category_orders={
                                   "mes_nome": meses_selecionados},
                               labels={"mes_nome": "Mês", "fabrica": "Fábrica", st.session_state.valor: "Valor (R$)"})

fig_fabrica_perc = px.pie(df_fabrica_perc, values="percentual", names="fabrica",
                          title="Percentual fábrica - período",
                          color_discrete_sequence=px.colors.sequential.Plasma,
                          labels={"percentual": "Percentual", "fabrica": "Fábrica"})

vis_fabrica = st.selectbox(label="Selecionar visualização - Fábricas", options=VISUALIZACAO_GRAFICOS)
if vis_fabrica == "Período":
    st.plotly_chart(fig_fabrica_total)
elif vis_fabrica == "Mensal":
    st.plotly_chart(fig_fabrica_mes)
else:
    st.plotly_chart(fig_fabrica_perc)

st.markdown("---")

# ESTADO
df_soma_estado = df_vendas_filtro[["estado", st.session_state.valor]]
df_soma_estado = df_soma_estado.groupby(["estado"]).sum()

geo_df_estados_nordeste = st.session_state.mapa_brasil.merge(df_soma_estado, left_on="id", right_on="estado").set_index(
    "id")

# Vendas por estado
st.subheader(f"{st.session_state.titulo} por estado")
df_estado_total = df_vendas[["estado", st.session_state.valor]]
df_estado_mes = df_vendas[["mes", "mes_nome", "estado", st.session_state.valor]]

df_estado_total = df_estado_total.groupby(["estado"], as_index=False).sum()
df_estado_total.sort_values("estado", inplace=True)

df_estado_mes = df_estado_mes.groupby(["mes", "mes_nome", "estado"], as_index=False).sum()
df_estado_mes.sort_values("mes", inplace=True)

df_estado_perc = df_estado_total
valor_estado_tot = df_estado_total[st.session_state.valor].sum()
df_estado_perc["percentual"] = df_estado_perc[st.session_state.valor].apply(
    lambda x: round((100 * float(x) / float(valor_estado_tot)), 2))

fig_estado_total = px.bar(df_estado_total, x="estado", y=st.session_state.valor, title="Soma por estado - Período",
                          color='estado', color_discrete_sequence=px.colors.sequential.Plasma,
                          labels={"estado": "estado", st.session_state.valor: "Valor (R$)"})

fig_estado_mes = px.histogram(df_estado_mes, x="mes_nome", y=st.session_state.valor, title="Soma por estado - Mensal",
                              color='estado', barmode="group",
                              color_discrete_sequence=px.colors.sequential.Plasma,
                              category_orders={
                                  "mes_nome": meses_selecionados},
                              labels={"mes_nome": "Mês", "estado": "Estado", st.session_state.valor: "Valor (R$)"})

fig_estado_perc = px.pie(df_estado_perc, values="percentual", names="estado",
                         title="Percentual estado - período",
                         color_discrete_sequence=px.colors.sequential.Plasma,
                         labels={"percentual": "Percentual", "estado": "Estado"})

# Mapa Estado
fig_mapa_estado = px.choropleth_map(geo_df_estados_nordeste, geojson=geo_df_estados_nordeste.geometry,
                                    locations=geo_df_estados_nordeste.index, color=st.session_state.valor,
                                    map_style='carto-positron', color_continuous_scale="Viridis", height=800, zoom=5,
                                    center={"lat": -8.064949, "lon": -34.919630})

# Exibir
vis_estado = st.selectbox(label="Selecionar visualização - Estados", options=VISUALIZACAO_GRAFICOS_COM_MAPA)
if vis_estado == "Período":
    st.plotly_chart(fig_estado_total)
elif vis_estado == "Mensal":
    st.plotly_chart(fig_estado_mes)
elif vis_estado == "Percentual":
    st.plotly_chart(fig_estado_perc)
else:
    st.plotly_chart(fig_mapa_estado)

st.markdown("---")

# CIDADES
mapa_ne = pd.concat(
    [st.session_state.mapa_pe, st.session_state.mapa_pb, st.session_state.mapa_al, st.session_state.mapa_se,
     st.session_state.mapa_rn, st.session_state.mapa_ba, st.session_state.mapa_ce])

df_soma_cidade = df_vendas_filtro[["cidade", st.session_state.valor]]
df_soma_cidade = df_soma_cidade.groupby(["cidade"]).sum()

geo_df_cidades_nordeste = mapa_ne.merge(df_soma_cidade, left_on="name", right_on="cidade").set_index("name")

# Vendas por cidade
st.subheader(f"{st.session_state.titulo} por cidade")
df_cidade_total = df_vendas_filtro[["cidade", st.session_state.valor]]
df_cidade_mes = df_vendas_filtro[["mes", "mes_nome", "cidade", st.session_state.valor]]

df_cidade_total = df_cidade_total.groupby(["cidade"], as_index=False).sum()
df_cidade_total.sort_values("cidade", inplace=True)

df_cidade_mes = df_cidade_mes.groupby(["mes", "mes_nome", "cidade"], as_index=False).sum()
df_cidade_mes.sort_values("mes", inplace=True)

df_cidade_perc = df_cidade_total
valor_cidade_tot = df_cidade_total[st.session_state.valor].sum()
df_cidade_perc["percentual"] = df_cidade_perc[st.session_state.valor].apply(
    lambda x: round((100 * float(x) / float(valor_cidade_tot)), 2))

fig_cidade_total = px.bar(df_cidade_total, x="cidade", y=st.session_state.valor, title="Soma por cidade - Período",
                          color='cidade', color_discrete_sequence=px.colors.sequential.Plasma,
                          labels={"cidade": "Cidade", st.session_state.valor: "Valor (R$)"})

fig_cidade_mes = px.histogram(df_cidade_mes, x="mes_nome", y=st.session_state.valor, title="Soma por cidade - Mensal",
                              color='cidade', barmode="group",
                              color_discrete_sequence=px.colors.sequential.Plasma,
                              category_orders={
                                  "mes_nome": meses_selecionados},
                              labels={"mes_nome": "Mês", "cidade": "Cidade", st.session_state.valor: "Valor (R$)"})

fig_cidade_perc = px.pie(df_cidade_perc, values="percentual", names="cidade",
                         title="Percentual cidade - período",
                         color_discrete_sequence=px.colors.sequential.Plasma,
                         labels={"percentual": "Percentual", "cidade": "Cidade"})

fig_mapa_cidade = px.choropleth_map(geo_df_cidades_nordeste, geojson=geo_df_cidades_nordeste.geometry,
                                    locations=geo_df_cidades_nordeste.index, color=st.session_state.valor,
                                    map_style='carto-positron', color_continuous_scale="Viridis", height=800, zoom=8,
                                    center={"lat": -8.064949, "lon": -34.919630})

# Exibir
vis_cidade = st.selectbox(label="Selecionar visualização - Cidades", options=VISUALIZACAO_GRAFICOS_COM_MAPA)
if vis_cidade == "Período":
    st.plotly_chart(fig_cidade_total)
elif vis_cidade == "Mensal":
    st.plotly_chart(fig_cidade_mes)
elif vis_cidade == "Percentual":
    st.plotly_chart(fig_cidade_perc)
else:
    st.plotly_chart(fig_mapa_cidade)

if st.session_state.valor == "valor":
    with st.expander("Visualizar banco de dados de vendas"):
        df_vendas_editadas = st.data_editor(st.session_state.df_vendas)


        def recalcular_comissao():
            for linha in df_vendas_editadas.itertuples():
                df_vendas_editadas.at[linha.Index, 'comissao'] = float(linha.valor * linha.percentual_comissao / 100)
            st.session_state.df_vendas = df_vendas_editadas


        def atualizar_dados():
            recalcular_comissao()
            planilha_vendas = Planilha()
            planilha_vendas.atualizar_aba_vendas(df=st.session_state.df_vendas)
            st.session_state.df_vendas = df_vendas_editadas
            st.cache_data.clear()


        st.button("Atualizar dados", on_click=atualizar_dados)
