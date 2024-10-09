from calendar import monthrange
from typing import TypedDict

import pandas as pd

from balanco_hidrico_reservatorios.reservatorios import Reservatorio
from balanco_hidrico_reservatorios.serie_temporal import ColunasSerieTemporal


class ResultadoEvaporacaoNoPeriodo(TypedDict):
    cota_final: float
    area_lago_km2: float
    volume_evaporado_hm3: float
    volume_precipitado_hm3: float


def calcula_volume_evaporado_do_lago(
    reservatorio: Reservatorio,
    volume_inicial: float,
    row: pd.Series,
    factor_q_to_vol: float
) -> ResultadoEvaporacaoNoPeriodo:
    

    nome_colunas = reservatorio.serie_temporal.nome_das_colunas
    vazao_afluente = row[nome_colunas['vazao_afluente']]
    vazao_turbinada = row[nome_colunas['vazao_turbinada']]
    vazao_retirada = row[nome_colunas['vazao_retirada']]
    evaporacao = row[nome_colunas['evaporacao']]
    precipitacao = row[nome_colunas['precipitacao']]

    volume_afluente = vazao_afluente * factor_q_to_vol
    volume_turbinado = vazao_turbinada * factor_q_to_vol
    volume_retirada = vazao_retirada * factor_q_to_vol
    
    cota_inicial = reservatorio.cav.calcula_cota_por(volume=volume_inicial)
    area_corresp_inicial = reservatorio.cav.calcula_area_por(cota=cota_inicial)

    volume_sem_evap = volume_inicial + volume_afluente - volume_retirada - volume_turbinado

    volume_evap_lago = 0
    volume_prec_lago = 0
    diferenca = 99999.0
    while (diferenca > 0.1):
        volume_final = volume_sem_evap - volume_evap_lago + volume_prec_lago
        cota_final = reservatorio.cav.calcula_cota_por(volume=volume_final)
        area_corresp_final = reservatorio.cav.calcula_area_por(cota=cota_final)
        area_media = (area_corresp_inicial + area_corresp_final) / 2
        diferenca = abs((volume_prec_lago - volume_evap_lago) - area_media * (precipitacao - evaporacao) / 1_000)
        volume_evap_lago = area_media * evaporacao / 1_000
        volume_prec_lago = area_media * precipitacao / 1_000

    return  {
        'cota_final': cota_final,
        'area_lago_km2': area_media,
        'volume_evaporado_hm3': volume_evap_lago,
        'volume_precipitado_hm3': volume_prec_lago
    }
