import streamlit as st
import pandas as pd
import geopandas as gpd
from planilha import Planilha
import calendar
import numpy as np
import requests
import time

USUARIOS_VALIDOS = st.secrets["USUARIOS_VALIDOS"]


def login_screen():
    st.header("Faça o log in para acessar o aplicativo")
    st.button("Login com Google", on_click=st.login)


if not st.user.is_logged_in:
    login_screen()
elif st.user.email in USUARIOS_VALIDOS:
    # image ID
    file_id = st.secrets["logo_image"]

    # URL
    url = f"https://drive.google.com/uc?export=view&id={file_id}"
    response = requests.get(url)

    st.markdown("""
            <style>
                .st-emotion-cache-7czcpc img{
                    border-radius: 50%;
                    margin-bottom: 4rem;
                }
            </style>
        """, unsafe_allow_html=True)

    pg_geral = st.Page(
        page="views/geral.py",
        title="Geral",
        icon=":material/home:",
        default=True
    )

    pg_vendas = st.Page(
        page="views/vendas.py",
        title="Vendas/Comissão",
        icon=":material/paid:"
    )


    def buscar_vendas():
        if not "planilha_obj" in st.session_state or not st.session_state.planilha_obj:
            st.session_state.planilha_obj = Planilha()
        st.session_state.df_vendas = st.session_state.planilha_obj.buscar_vendas_df()
        return st.session_state.df_vendas


    if not "planilha_obj" in st.session_state or not "df_vendas" in st.session_state:
        df_vendas = buscar_vendas().copy()
    else:
        if st.session_state.df_vendas.empty:
            df_vendas = buscar_vendas().copy()
        else:
            df_vendas = st.session_state.df_vendas.copy()


    def buscar_despesas():
        if not "planilha_obj" in st.session_state or not st.session_state.planilha_obj:
            st.session_state.planilha_obj = Planilha()
        st.session_state.df_despesas = st.session_state.planilha_obj.buscar_despesas_df()
        return st.session_state.df_despesas


    if not "planilha_obj" in st.session_state or not "df_despesas" in st.session_state:
        df_despesas = buscar_despesas().copy()
    else:
        if st.session_state.df_despesas.empty:
            df_despesas = buscar_despesas().copy()
        else:
            df_despesas = st.session_state.df_despesas.copy()

    df_vendas["data"] = pd.to_datetime(df_vendas["data"])
    df_vendas["mes"] = df_vendas["data"].dt.month
    df_vendas["mes_nome"] = df_vendas["mes"].apply(lambda x: calendar.month_name[x].capitalize())
    df_vendas["ano"] = df_vendas["data"].dt.year

    # Ler geoJSON
    st.session_state.mapa_pb = gpd.read_file('files/geojson_pb.json')
    st.session_state.mapa_pe = gpd.read_file('files/geojson_pe.json')
    st.session_state.mapa_al = gpd.read_file('files/geojson_al.json')
    st.session_state.mapa_se = gpd.read_file('files/geojson_se.json')
    st.session_state.mapa_rn = gpd.read_file('files/geojson_rn.json')
    st.session_state.mapa_brasil = gpd.read_file('files/br_states.json')

    # Lista de estados
    ESTADOS_NORDESTE = [
        "AL",
        "PB",
        "PE",
        "RN",
        "SE"
    ]


    @st.dialog("Adicionar Venda")
    def formulario_venda():
        data_form = st.date_input(label="Data da venda*")
        loja_form = st.selectbox(label="Loja*", options=st.session_state.df_vendas["loja"].unique(),
                                 accept_new_options=True, index=None)

        loja_existente_df = st.session_state.df_vendas[st.session_state.df_vendas["loja"] == loja_form]
        if not loja_existente_df.empty:
            estado_loja_existente = loja_existente_df.iloc[0]["estado"]
            cidade_loja_existente = loja_existente_df.iloc[0]["cidade"]

            estado_default = next((i for i, estado in enumerate(ESTADOS_NORDESTE) if estado == estado_loja_existente),
                                  None)
        else:
            estado_default = None
            cidade_loja_existente = None

        estado_form = st.selectbox(label="Estado*", options=ESTADOS_NORDESTE, index=estado_default)
        if estado_form == "PE":
            cidade_opcoes = st.session_state.mapa_pe["name"].unique()
        elif estado_form == "PB":
            cidade_opcoes = st.session_state.mapa_pb["name"].unique()
        elif estado_form == "AL":
            cidade_opcoes = st.session_state.mapa_al["name"].unique()
        elif estado_form == "SE":
            cidade_opcoes = st.session_state.mapa_se["name"].unique()
        elif estado_form == "RN":
            cidade_opcoes = st.session_state.mapa_rn["name"].unique()
        else:
            cidade_opcoes = np.array([])

        if cidade_opcoes.size > 0:
            if cidade_loja_existente:
                cidade_default = np.where(cidade_opcoes == cidade_loja_existente)[0]
                print(cidade_default)
                if cidade_default.size > 0:
                    cidade_default = int(cidade_default[0])
                else:
                    cidade_default = None
            else:
                cidade_default = None

            cidade_form = st.selectbox(label="Cidade*", options=cidade_opcoes, index=cidade_default)

        fabrica_form = st.selectbox(label="Fábrica*", options=df_vendas["fabrica"].unique(), index=None,
                                    accept_new_options=True)

        valor_form = st.number_input(label="Valor em R$*")

        fabrica_existente_df = df_vendas[df_vendas["fabrica"] == fabrica_form]

        if not fabrica_existente_df.empty:
            percentual_fabrica_existente = float(fabrica_existente_df.iloc[0]["percentual_comissao"])
        else:
            percentual_fabrica_existente = 0.00

        percentual_comissao_form = st.number_input(label="Percentual da comissão*", value=percentual_fabrica_existente)

        st.markdown("**Campos Obrigatórios**")

        botao_enviar = st.button(label="Enviar")
        if botao_enviar:
            if not data_form or not loja_form or not estado_form or not cidade_form or not valor_form or not percentual_comissao_form:
                st.error("Preencher campos obrigatórios")
            else:
                valor_comissao = float(valor_form * percentual_comissao_form / 100)
                nova_venda = {
                    "data": pd.to_datetime(data_form),
                    "loja": loja_form,
                    "estado": estado_form,
                    "cidade": cidade_form,
                    "fabrica": fabrica_form,
                    "valor": valor_form,
                    "percentual_comissao": percentual_comissao_form,
                    "comissao": valor_comissao
                }
                nova_linha = pd.Series(nova_venda)
                df_inicial = st.session_state.df_vendas

                df_final = pd.concat([df_inicial, nova_linha.to_frame().T], ignore_index=True)

                st.session_state.planilha_obj.atualizar_aba_vendas(df=df_final)
                st.session_state.df_vendas = df_final
                st.rerun()


    @st.dialog("Adicionar Despesa")
    def formulario_despesa():
        data_despesa_form = st.date_input(label="Data da despesa*")
        descricao_despesa_form = st.selectbox(label="Descrição*",
                                              options=st.session_state.df_despesas["descricao"].unique(),
                                              accept_new_options=True, index=None)

        descricao_existente_index = st.session_state.df_despesas.index[
            st.session_state.df_despesas["descricao"] == descricao_despesa_form]

        if not descricao_existente_index.empty:
            categoria_existente_index = int(descricao_existente_index[0])
        else:
            categoria_existente_index = None

        categoria_despesa_form = st.selectbox(label="Categoria*",
                                              options=st.session_state.df_despesas["categoria"].unique(),
                                              accept_new_options=True, index=categoria_existente_index)

        valor_despesa_form = st.number_input(label="Valor em R$*")

        st.markdown("**Campos Obrigatórios**")

        botao_enviar_despesa = st.button(label="Enviar")
        if botao_enviar_despesa:
            if not data_despesa_form or not descricao_despesa_form or not categoria_despesa_form or not valor_despesa_form:
                st.error("Preencher campos obrigatórios")
            else:
                nova_venda = {
                    "data": pd.to_datetime(data_despesa_form),
                    "descricao": descricao_despesa_form,
                    "categoria": categoria_despesa_form,
                    "valor": valor_despesa_form
                }
                nova_linha = pd.Series(nova_venda)
                df_despesa_inicial = st.session_state.df_despesas

                df_despesa_final = pd.concat([df_despesa_inicial, nova_linha.to_frame().T], ignore_index=True)

                st.session_state.planilha_obj.atualizar_aba_despesas(df=df_despesa_final)
                st.session_state.df_despesas = df_despesa_final
                st.rerun()


    with st.sidebar:
        valor_venda_comissao = st.selectbox(label="Selecione o que deseja ver",
                                            options=["Valor da venda", "Valor da comissão"])
        if valor_venda_comissao == "Valor da venda":
            st.session_state.valor = "valor"
            st.session_state.titulo = "Vendas"
        else:
            st.session_state.valor = "comissao"
            st.session_state.titulo = "Comissão"
        st.button("Adicionar Venda", on_click=formulario_venda)
        st.button("Adicionar Despesa", on_click=formulario_despesa)
        st.divider()
        st.image(response.content)
        st.markdown("##")
        st.button("Logout", on_click=st.logout)

    pg = st.navigation({
        "Relatório de representação": [pg_geral, pg_vendas],
    })

    pg.run()

else:
    st.error("Usuário inválido")
    time.sleep(2)
    st.logout()
