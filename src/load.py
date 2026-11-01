from pathlib import Path

import pandas as pd

from src.transform import (
    transformar_1991,
    transformar_2000,
    transformar_2010,
    transformar_2022,
)

RAIZ = Path(__file__).resolve().parent.parent
RAW = RAIZ / "data" / "raw"
PROCESSED = RAIZ / "data" / "processed"

COLUNAS = ["ano", "nivel", "territorio", "situacao", "sexo", "faixa_etaria", "taxa_analfabetismo"]

def montar_tabela():
    partes = [
        transformar_1991(RAW / "censo_1991_tab201.csv"),
        transformar_2000(RAW / "censo_2000_tab1553.csv"),
        transformar_2010(RAW / "censo_2010_tab7240.csv"),
        transformar_2022(RAW / "censo_2022_tab10091.csv"),
    ]
    return pd.concat([p[COLUNAS] for p in partes], ignore_index=True)

def validar(tabela):
    chave = ["ano", "territorio", "situacao", "sexo", "faixa_etaria"]
    assert not tabela.duplicated(chave).any(), "há linhas duplicadas"
    assert tabela["taxa_analfabetismo"].notna().all(), "há taxas vazias"
    assert tabela["taxa_analfabetismo"].between(0, 100).all(), "há taxa fora de 0 a 100"
    brasil = tabela[
        (tabela["territorio"] == "Brasil")
        & (tabela["situacao"] == "Total")
        & (tabela["sexo"] == "Total")
        & (tabela["faixa_etaria"] == "Total")
    ].set_index("ano")["taxa_analfabetismo"]
    esperado = {1991: 20.07, 2000: 13.63, 2010: 9.62, 2022: 7.0}
    for ano, valor in esperado.items():
        assert brasil[ano] == valor, f"Brasil {ano}: {brasil[ano]} em vez de {valor}"
    print("validação ok")

if __name__ == "__main__":
    tabela = montar_tabela()
    validar(tabela)
    tabela = montar_tabela()
    PROCESSED.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(PROCESSED / "analfabetismo_censos.csv", index=False, encoding="utf-8")
    print(tabela.shape)
    print(tabela.groupby("ano").size())