import pandas as pd

from balanco_hidrico_reservatorios.reservatorios import ReservatorioONS
from balanco_hidrico_reservatorios.serie_temporal import SerieTemporal
from balanco_hidrico_reservatorios.balanco_hidrico import calcula_balanco_hidrico


def calcula_vazao_regularizada(
    reservatorio: ReservatorioONS,
    serie_temporal: SerieTemporal,
) -> pd.DataFrame:

    df_serie = serie_temporal.dataframe.copy()
    nome_das_colunas = serie_temporal.nome_das_colunas
    
    vazao_media_afluente = df_serie[nome_das_colunas['vazao_afluente']].mean()
    df_serie[nome_das_colunas['vazao_turbinada']] = vazao_media_afluente
    serie_historica = SerieTemporal(
        dataframe=df_serie,
        nome_das_colunas=nome_das_colunas,
        freq="M")
    
    resultado = calcula_balanco_hidrico(
        reservatorio=reservatorio,
        serie_temporal=serie_historica,
        percentual_volume_inicial=50,
        prioridade_de_atendimento="Vazão Turbinada"
    )
    
    return pd.DataFrame(resultado)
    