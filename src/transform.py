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

def ler_2000(caminho):
    bruto = pd.read_csv(caminho, sep=";", header=None, names=range(12), encoding="utf-8-sig")
    dados = bruto.iloc[6:3372]
    situacao = bruto.iloc[4, 3:].ffill()
    sexo = bruto.iloc[5, 3:]
    return dados, situacao, sexo

def transformar_2000(caminho):
    dados, situacao, sexo = ler_2000(caminho)
    dados = dados.copy()
    dados.columns = ["territorio", "alfabetizacao", "faixa_etaria"] + [
        f"{s}|{x}" for s, x in zip(situacao, sexo)
    ]
    longo = dados.melt(
        id_vars=["territorio", "alfabetizacao", "faixa_etaria"],
        var_name="chave",
        value_name="pessoas",
    )
    longo[["situacao", "sexo"]] = longo["chave"].str.split("|", expand=True)
    longo = longo.drop(columns="chave")
    longo["pessoas"] = pd.to_numeric(longo["pessoas"], errors="coerce")
    longo["sexo"] = longo["sexo"].replace({"Homem": "Homens", "Mulher": "Mulheres"})
    grupos = {
        "Total": ["15 anos ou mais"],
        "15 a 17 anos": ["15 anos", "16 anos", "17 anos"],
        "18 e 19 anos": ["18 anos", "19 anos"],
        "20 a 24 anos": ["20 a 24 anos"],
        "25 a 34 anos": ["25 a 29 anos", "30 a 34 anos"],
        "35 a 44 anos": ["35 a 39 anos", "40 a 44 anos"],
        "45 a 54 anos": ["45 a 49 anos", "50 a 54 anos"],
        "55 a 64 anos": ["55 a 59 anos", "60 a 64 anos"],
        "65 anos ou mais": ["65 a 69 anos", "70 a 74 anos", "75 a 79 anos", "80 anos ou mais"],
        "75 anos ou mais": ["75 a 79 anos", "80 anos ou mais"],
    }
    partes = []
    for novo, antigos in grupos.items():
        sub = (longo[longo["faixa_etaria"].isin(antigos)]
               .groupby(["territorio", "alfabetizacao", "situacao", "sexo"], as_index=False)["pessoas"].sum())
        sub["faixa_etaria"] = novo
        partes.append(sub)
    longo = pd.concat(partes, ignore_index=True)

    largo = longo.pivot_table(
        index=["territorio", "situacao", "sexo", "faixa_etaria"],
        columns="alfabetizacao",
        values="pessoas",
    ).reset_index()
    largo["sem_declaracao"] = largo["Total"] - largo["Alfabetizadas"] - largo["Não alfabetizadas"]
    largo["taxa_analfabetismo"] = (
        100 * largo["Não alfabetizadas"] / (largo["Alfabetizadas"] + largo["Não alfabetizadas"])
    ).round(2)
    largo["ano"] = 2000
    largo["nivel"] = largo["territorio"].map(classificar_nivel)
    return largo

def ler_1991(caminho):
    bruto = pd.read_csv(caminho, sep=";", header=None, names=range(11), encoding="utf-8-sig")
    dados = bruto.iloc[6:1062]
    alfabetizacao = bruto.iloc[4, 2:].ffill()
    situacao = bruto.iloc[5, 2:]
    return dados, alfabetizacao, situacao

def transformar_1991(caminho):
    dados, alfabetizacao, situacao = ler_1991(caminho)
    dados = dados.copy()
    dados.columns = ["territorio", "faixa_etaria"] + [
        f"{a}|{s}" for a, s in zip(alfabetizacao, situacao)
    ]
    longo = dados.melt(
        id_vars=["territorio", "faixa_etaria"],
        var_name="chave",
        value_name="pessoas",
    )
    longo[["alfabetizacao", "situacao"]] = longo["chave"].str.split("|", expand=True)
    longo = longo.drop(columns="chave")
    longo["pessoas"] = pd.to_numeric(longo["pessoas"], errors="coerce")
    grupos = {
        "Total": ["15 a 19 anos", "20 a 24 anos", "25 a 29 anos", "30 a 34 anos",
                  "35 a 39 anos", "40 a 44 anos", "45 a 49 anos", "50 a 54 anos",
                  "55 a 59 anos", "60 a 64 anos", "65 a 69 anos", "70 a 74 anos",
                  "75 a 79 anos", "80 anos ou mais"],
        "15 a 17 anos": ["15 anos", "16 anos", "17 anos"],
        "18 e 19 anos": ["18 anos", "19 anos"],
        "20 a 24 anos": ["20 a 24 anos"],
        "25 a 34 anos": ["25 a 29 anos", "30 a 34 anos"],
        "35 a 44 anos": ["35 a 39 anos", "40 a 44 anos"],
        "45 a 54 anos": ["45 a 49 anos", "50 a 54 anos"],
        "55 a 64 anos": ["55 a 59 anos", "60 a 64 anos"],
        "65 anos ou mais": ["65 a 69 anos", "70 a 74 anos", "75 a 79 anos", "80 anos ou mais"],
        "75 anos ou mais": ["75 a 79 anos", "80 anos ou mais"],
    }
    partes = []
    for novo, antigos in grupos.items():
        sub = (longo[longo["faixa_etaria"].isin(antigos)]
               .groupby(["territorio", "alfabetizacao", "situacao"], as_index=False)["pessoas"].sum())
        sub["faixa_etaria"] = novo
        partes.append(sub)
    longo = pd.concat(partes, ignore_index=True)

    largo = longo.pivot_table(
        index=["territorio", "situacao", "faixa_etaria"],
        columns="alfabetizacao",
        values="pessoas",
    ).reset_index()
    largo["sem_declaracao"] = largo["Total"] - largo["Alfabetizadas"] - largo["Não alfabetizadas"]
    largo["taxa_analfabetismo"] = (
        100 * largo["Não alfabetizadas"] / (largo["Alfabetizadas"] + largo["Não alfabetizadas"])
    ).round(2)
    largo["sexo"] = "Total"
    largo["ano"] = 1991
    largo["nivel"] = largo["territorio"].map(classificar_nivel)
    return largo