from calendar import monthrange

import pandas as pd

from balanco_hidrico_reservatorios.serie_temporal import (
    Frequencia,
    _checa_falhas_nas_datas_da_serie_temporal,
    _checa_indice_da_serie_temporal,
    _checa_nome_das_colunas,
)


def gera_taxa_mensal_de_qturbinada_em_funcao_da_qafluente(
    serie_temporal: pd.DataFrame,
    coluna_vazao_turbinada: str,
    coluna_vazao_afluente: str,
    freq: Frequencia
) -> dict[int, float]:
    
    colunas_df = [coluna_vazao_afluente, coluna_vazao_turbinada]
    
    _checa_indice_da_serie_temporal(serie_temporal, freq=freq)
    _checa_falhas_nas_datas_da_serie_temporal(serie_temporal, freq=freq)
    _checa_nome_das_colunas(serie_temporal, colunas_df)
    
    df = serie_temporal[colunas_df].copy()
    df_mean = df.groupby(df.index.month).mean()  # type: ignore
    df_mean['taxa'] = (df_mean[coluna_vazao_turbinada] / df_mean[coluna_vazao_afluente])
    
    dicionario = df_mean[['taxa']].to_dict()
    
    if list(dicionario.keys()).sort() != list(range(1, 13)).sort():
        raise ValueError(
            "Dicionário gerado não retornou valores para todos os meses do ano. \n"
            f"Valores gerados: {dicionario}"
        )
    
    return  dicionario['taxa']


def insere_qturbinada_na_serie_temporal_com_taxa_mensal(
    serie_temporal: pd.DataFrame,
    taxa_mensal_da_vazao_turbinada: dict[int, float],
    coluna_vazao_turbinada: str,
    coluna_vazao_afluente: str,
) -> pd.DataFrame:
    
    df_serie = serie_temporal.copy()
    
    for mes in range(1, 13):
        qturb = df_serie[df_serie.index.month == mes][coluna_vazao_afluente] \
            * taxa_mensal_da_vazao_turbinada[mes]
        df_serie.loc[df_serie.index.month == mes, [coluna_vazao_turbinada]] = qturb
    
    return df_serie
    
    
def gera_serie_pandas_a_partir_de_vetor_mensal(
    serie_temporal: pd.DataFrame,
    vetor_mensal: dict[int, float],
    freq: Frequencia
) -> pd.Series:
    
    if list(vetor_mensal.keys()).sort() != list(range(1, 13)).sort():
        raise ValueError(
            "Dicionário gerado não retornou valores para todos os meses do ano. \n"
            f"Valores gerados: {vetor_mensal}"
        )
    
    df_serie = serie_temporal.copy()
    df_serie['vetor'] = None
    
    
    if freq == "D":
        df_serie['num_dias_no_mes'] = [monthrange(i.year, i.month)[1] for i in df_serie.index]
                
        for mes in range(1, 13):
            df_serie.loc[df_serie.index.month == mes, ['vetor']] = \
                vetor_mensal[mes] / df_serie.loc[df_serie.index.month == mes]['num_dias_no_mes']  # type: ignore
    
    if freq == "M":
        for mes in range(1, 13):
            df_serie.loc[df_serie.index.month == mes, ['vetor']] = vetor_mensal[mes]  # type: ignore
    
    return df_serie['vetor']

