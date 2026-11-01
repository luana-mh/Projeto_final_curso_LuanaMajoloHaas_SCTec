import pandas as pd

REGIOES = ["Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]

def classificar_nivel(nome):
    if nome == "Brasil":
        return "Brasil"
    if nome in REGIOES:
        return "Região"
    return "UF"

def ler_2022(caminho):
    bruto = pd.read_csv(caminho, sep=";", header=None, names=range(33), encoding="utf-8-sig")
    dados = bruto.iloc[6:105]
    sexo = bruto.iloc[4, 3:].ffill()
    faixa = bruto.iloc[5, 3:]
    return dados, sexo, faixa

def transformar_2022(caminho):
    dados, sexo, faixa = ler_2022(caminho)
    dados = dados.copy()
    dados.columns = ["territorio", "localizacao", "situacao"] + [f"{s}|{f}" for s, f in zip(sexo, faixa)]
    longo = dados.melt(
        id_vars=["territorio", "localizacao", "situacao"],
        var_name="sexo_faixa",
        value_name="taxa_alfabetizacao",
    )
    longo[["sexo", "faixa_etaria"]] = longo["sexo_faixa"].str.split("|", expand=True)
    longo = longo.drop(columns="sexo_faixa")
    longo["taxa_alfabetizacao"] = pd.to_numeric(
        longo["taxa_alfabetizacao"].str.replace(",", "."), errors="coerce"
    )
    longo["taxa_analfabetismo"] = (100 - longo["taxa_alfabetizacao"]).round(2)
    longo["ano"] = 2022
    longo["nivel"] = longo["territorio"].map(classificar_nivel)
    longo = longo.drop(columns="localizacao")
    return longo