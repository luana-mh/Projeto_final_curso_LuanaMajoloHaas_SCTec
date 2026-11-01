import pandas as pd

def ler_2022(caminho):
    bruto = pd.read_csv(caminho, sep=";", header=None, names=range(33), encoding="utf-8-sig")
    dados = bruto.iloc[6:105]
    sexo = bruto.iloc[4, 3:].ffill()
    faixa = bruto.iloc[5, 3:]
    return dados, sexo, faixa

def ler_2010(caminho):
    bruto = pd.read_csv(caminho, sep=";", header=None, names=range(543), encoding="utf-8-sig")
    dados = bruto.iloc[7:40]
    alfabetizacao = bruto.iloc[4, 3:].ffill()
    sexo = bruto.iloc[5, 3:].ffill()
    faixa = bruto.iloc[6, 3:]
    return dados, alfabetizacao, sexo, faixa

def ler_2000(caminho):
    bruto = pd.read_csv(caminho, sep=";", header=None, names=range(12), encoding="utf-8-sig")
    dados = bruto.iloc[6:3372]
    situacao = bruto.iloc[4, 3:].ffill()
    sexo = bruto.iloc[5, 3:]
    return dados, situacao, sexo

def ler_1991(caminho):
    bruto = pd.read_csv(caminho, sep=";", header=None, names=range(11), encoding="utf-8-sig")
    dados = bruto.iloc[6:1062]
    alfabetizacao = bruto.iloc[4, 2:].ffill()
    situacao = bruto.iloc[5, 2:]
    return dados, alfabetizacao, situacao