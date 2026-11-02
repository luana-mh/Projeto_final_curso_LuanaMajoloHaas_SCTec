from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Analfabetismo no Brasil", layout="wide")

CAMINHO = Path(__file__).resolve().parent.parent / "data" / "processed" / "analfabetismo_censos.csv"

@st.cache_data
def carregar():
    return pd.read_csv(CAMINHO)

df = carregar()

ORDEM_FAIXAS = ["Total", "15 a 17 anos", "18 e 19 anos", "20 a 24 anos", "25 a 34 anos",
                "35 a 44 anos", "45 a 54 anos", "55 a 64 anos", "65 anos ou mais", "75 anos ou mais"]

st.title("Analfabetismo no Brasil: Censos de 1991, 2000, 2010 e 2022")
st.write("Fonte: IBGE, Censo Demográfico. População de 15 anos ou mais.")

st.sidebar.header("Filtros")
st.sidebar.caption("Nem todos os censos detalham todos os filtros: o de 1991 não separa por sexo e o de 2010 não separa por situação do domicílio.")
ano = st.sidebar.selectbox("Censo", sorted(df["ano"].unique(), reverse=True))
dados_ano = df[df["ano"] == ano]

sexos = [s for s in ["Total", "Homens", "Mulheres"] if s in dados_ano["sexo"].unique()]
situacoes = [s for s in ["Total", "Urbana", "Rural"] if s in dados_ano["situacao"].unique()]
sexo = st.sidebar.selectbox("Sexo", sexos)
situacao = st.sidebar.selectbox("Situação do domicílio", situacoes)
faixa = st.sidebar.selectbox(
    "Faixa de idade", ORDEM_FAIXAS,
    format_func=lambda f: "15 anos ou mais (total)" if f == "Total" else f,
)

filtro = (
    (df["ano"] == ano) & (df["sexo"] == sexo)
    & (df["situacao"] == situacao) & (df["faixa_etaria"] == faixa)
)
ufs = df[filtro & (df["nivel"] == "UF")]
brasil = df[filtro & (df["territorio"] == "Brasil")]

if ufs.empty or brasil.empty:
    st.warning("Não há dados para essa combinação de filtros.")
    st.stop()

valor = brasil["taxa_analfabetismo"].iloc[0]
st.metric(f"Brasil, Censo {ano}", f"{valor:.2f}%".replace(".", ","))

maior = ufs.loc[ufs["taxa_analfabetismo"].idxmax()]
menor = ufs.loc[ufs["taxa_analfabetismo"].idxmin()]
amplitude = maior["taxa_analfabetismo"] - menor["taxa_analfabetismo"]

col1, col2, col3 = st.columns(3)
col1.metric(f"Maior taxa: {maior['territorio']}", f"{maior['taxa_analfabetismo']:.2f}%".replace(".", ","))
col2.metric(f"Menor taxa: {menor['territorio']}", f"{menor['taxa_analfabetismo']:.2f}%".replace(".", ","))
col3.metric("Amplitude entre UFs", f"{amplitude:.2f} p.p.".replace(".", ","))

fig = px.bar(
    ufs.sort_values("taxa_analfabetismo"), x="taxa_analfabetismo", y="territorio", orientation="h",
    title=f"Analfabetismo por UF, Censo {ano}",
    labels={"taxa_analfabetismo": "Analfabetismo (%)", "territorio": ""},
)
fig.update_layout(height=700)
st.plotly_chart(fig, width="stretch")
st.subheader("Evolução no Brasil")

evolucao = df[(df["territorio"] == "Brasil") & (df["sexo"] == sexo)
              & (df["situacao"] == situacao) & (df["faixa_etaria"] == faixa)].sort_values("ano")

fig_evolucao = px.line(evolucao, x="ano", y="taxa_analfabetismo", markers=True,
    labels={"taxa_analfabetismo": "Analfabetismo (%)", "ano": "Censo"})
fig_evolucao.update_xaxes(tickvals=[1991, 2000, 2010, 2022])
st.plotly_chart(fig_evolucao, width="stretch")

st.subheader("Perfil por idade no Brasil")

faixas_idade = [f for f in ORDEM_FAIXAS if f not in ("Total", "75 anos ou mais")]

perfil = df[(df["ano"] == ano) & (df["territorio"] == "Brasil") & (df["sexo"] == sexo)
            & (df["situacao"] == situacao) & (df["faixa_etaria"].isin(faixas_idade))]

fig_idade = px.bar(perfil, x="faixa_etaria", y="taxa_analfabetismo",
    category_orders={"faixa_etaria": faixas_idade},
    labels={"taxa_analfabetismo": "Analfabetismo (%)", "faixa_etaria": "Faixa de idade"})
st.plotly_chart(fig_idade, width="stretch")

st.subheader("Homens e mulheres ao longo dos censos")

por_sexo = df[(df["territorio"] == "Brasil") & (df["situacao"] == situacao)
              & (df["faixa_etaria"] == faixa) & (df["sexo"].isin(["Homens", "Mulheres"]))].sort_values("ano")

if por_sexo.empty:
    st.info("Não há dados por sexo para essa combinação de filtros.")
else:
    fig_sexo = px.line(por_sexo, x="ano", y="taxa_analfabetismo", color="sexo", markers=True,
        labels={"taxa_analfabetismo": "Analfabetismo (%)", "ano": "Censo", "sexo": "Sexo"})
    fig_sexo.update_xaxes(tickvals=[2000, 2010, 2022])
    st.plotly_chart(fig_sexo, width="stretch")