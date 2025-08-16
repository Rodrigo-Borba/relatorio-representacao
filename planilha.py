# coding: cp1252

import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection


class Planilha:
    def __init__(self):
        self.conexao = st.connection("gsheets", type=GSheetsConnection)

    def buscar_vendas_df(self):
        # # Lê os dados
        df = self.conexao.read(worksheet="Vendas")
        df["data"] = pd.to_datetime(df["data"])
        return df

    def buscar_despesas_df(self):
        # # Lê os dados
        df = self.conexao.read(worksheet="Despesas")
        df["data"] = pd.to_datetime(df["data"])
        return df

    def atualizar_aba_vendas(self, df: pd.DataFrame):
        df.sort_values("data", inplace=True)
        df["data"] = df["data"].apply(lambda x: str(pd.to_datetime(x))[0:10])
        self.conexao.update(worksheet="Vendas", data=df)

    def atualizar_aba_despesas(self, df: pd.DataFrame):
        df.sort_values("data", inplace=True)
        df["data"] = df["data"].apply(lambda x: str(pd.to_datetime(x))[0:10])
        self.conexao.update(worksheet="Despesas", data=df)
