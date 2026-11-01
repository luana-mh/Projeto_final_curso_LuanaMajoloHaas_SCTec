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

def ler_2010(caminho):
    bruto = pd.read_csv(caminho, sep=";", header=None, names=range(543), encoding="utf-8-sig")
    dados = bruto.iloc[7:40]
    alfabetizacao = bruto.iloc[4, 3:].ffill()
    sexo = bruto.iloc[5, 3:].ffill()
    faixa = bruto.iloc[6, 3:]
    return dados, alfabetizacao, sexo, faixa

def transformar_2010(caminho):
    dados, alfabetizacao, sexo, faixa = ler_2010(caminho)
    dados = dados.copy()
    dados.columns = ["territorio", "quesito", "localizacao"] + [
        f"{a}|{s}|{f}" for a, s, f in zip(alfabetizacao, sexo, faixa)
    ]
    longo = dados.melt(
        id_vars=["territorio", "quesito", "localizacao"],
        var_name="chave",
        value_name="pessoas",
    )
    longo[["alfabetizacao", "sexo", "faixa_etaria"]] = longo["chave"].str.split("|", expand=True)
    longo = longo.drop(columns="chave")
    longo["pessoas"] = pd.to_numeric(longo["pessoas"], errors="coerce")
    longo = longo.drop(columns=["quesito", "localizacao"])
    diretas = ["Total", "20 a 24 anos", "25 a 34 anos", "35 a 44 anos",
               "45 a 54 anos", "55 a 64 anos", "65 anos ou mais", "75 anos ou mais"]
    somas = {"15 a 17 anos": ["15 anos", "16 anos", "17 anos"],
             "18 e 19 anos": ["18 anos", "19 anos"]}
    partes = [longo[longo["faixa_etaria"].isin(diretas)]]
    for novo, idades in somas.items():
        soma = (longo[longo["faixa_etaria"].isin(idades)]
                .groupby(["territorio", "alfabetizacao", "sexo"], as_index=False)["pessoas"].sum())
        soma["faixa_etaria"] = novo
        partes.append(soma)
    longo = pd.concat(partes, ignore_index=True)
    largo = longo.pivot_table(
        index=["territorio", "sexo", "faixa_etaria"],
        columns="alfabetizacao",
        values="pessoas",
    ).reset_index()
    largo["sem_declaracao"] = largo["Total"] - largo["Alfabetizadas"] - largo["Não alfabetizadas"]
    largo["taxa_analfabetismo"] = (
        100 * largo["Não alfabetizadas"] / (largo["Alfabetizadas"] + largo["Não alfabetizadas"])
    ).round(2)
    largo["ano"] = 2010
    largo["situacao"] = "Total"
    largo["nivel"] = largo["territorio"].map(classificar_nivel)
    return largo