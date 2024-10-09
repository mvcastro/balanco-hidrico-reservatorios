from dataclasses import dataclass
from datetime import date
from calendar import monthrange
from typing import Literal, TypedDict, Annotated

import pandas as pd

from balanco_hidrico_reservatorios.conversor import converte_para
from balanco_hidrico_reservatorios.evaporacao_do_lago import (
    calcula_volume_evaporado_do_lago as calc_evp,
)
from balanco_hidrico_reservatorios.reservatorios import Reservatorio
from balanco_hidrico_reservatorios.serie_temporal import (
    SerieTemporal,
    _checa_falhas_nas_datas_da_serie_temporal,
    _checa_indice_da_serie_temporal,
    _checa_nome_das_colunas,
)

class ResultadoBHNoPeriodo(TypedDict):
    periodo: pd.Period
    cota_inicial: float
    cota_final: float
    vazao_afluente_m3_s: float
    vazao_turbinada_m3_s: float
    vazao_demandas_m3_s: float
    precipitacao_mm: float
    evaporacao_mm: float
    area_lago_km2: float
    volume_afluente_hm3: float
    volume_turbinado_hm3: float
    volume_inicial_hm3: float
    volume_final_hm3:  float
    volume_vertido_hm3: float
    volume_evaporado_hm3: float
    volume_precipitado_hm3: float

PrioridadeDeAtendimento = Literal["Vazão Turbinada", "Vazão das Demandas"]


def calcula_balanco_hidrico(
    reservatorio: Reservatorio,
    serie_temporal: SerieTemporal | None,
    percentual_volume_inicial: int,
    prioridade_de_atendimento: PrioridadeDeAtendimento 
) -> list[ResultadoBHNoPeriodo]:
    
    if percentual_volume_inicial < 0 or percentual_volume_inicial > 100:
        raise ValueError("Percentual do Volume Inicial deve estar entre 0 e 100")
    
    serie_temporal = reservatorio.serie_temporal if serie_temporal is None else serie_temporal
    resultado: list[ResultadoBHNoPeriodo] = []
    df_serie = serie_temporal.dataframe
    freq = serie_temporal.freq
    nome_das_colunas = serie_temporal.nome_das_colunas
    
    _checa_indice_da_serie_temporal(df_serie, freq=freq)
    _checa_falhas_nas_datas_da_serie_temporal(df_serie, freq=freq)
    _checa_nome_das_colunas(df_serie, list(nome_das_colunas.values())) # type: ignore
    
    volume_maximo = reservatorio.volume.maximo
    volume_minimo = reservatorio.volume.minimo
    volume_inicial = volume_minimo + (volume_maximo - volume_minimo) * percentual_volume_inicial / 100

    
    for index, row in df_serie.iterrows():
        if freq == "D":
            periodo = pd.to_datetime(index)  # type: ignore
        if freq == "M":
            periodo = pd.Period(index)  # type: ignore
        
        nome_colunas = reservatorio.serie_temporal.nome_das_colunas
        vazao_afluente = row[nome_colunas['vazao_afluente']]
        vazao_turbinada = row[nome_colunas['vazao_turbinada']]
        vazao_retirada = row[nome_colunas['vazao_retirada']]
        evaporacao = row[nome_colunas['evaporacao']]
        precipitacao = row[nome_colunas['precipitacao']]
        
        if freq == "D":
            factor_q_to_vol = 0.086400
        if freq == "M":
            factor_q_to_vol = 0.086400 * monthrange(periodo.year, periodo.month)[1]
            
        volume_vertido = 0.0
        volume_afluente = vazao_afluente * factor_q_to_vol
        volume_turbinado = vazao_turbinada * factor_q_to_vol
        volume_retirada = vazao_retirada * factor_q_to_vol
        cota_inicial = reservatorio.cav.calcula_cota_por(volume=volume_inicial)
        area_corresp_inicial = reservatorio.cav.calcula_area_por(cota=cota_inicial)
        volume_final = volume_inicial + volume_afluente - volume_turbinado - volume_retirada\
            + area_corresp_inicial * (precipitacao - evaporacao) / 1_000
    
        if volume_final  > volume_maximo:
            volume_vertido = volume_final - volume_maximo
            cota_max = reservatorio.cav.calcula_cota_por(volume=volume_maximo)
            area_max = reservatorio.cav.calcula_area_por(cota=cota_max)
            volume_evap_lago = area_max * evaporacao / 1_000
            volume_prec_lago = area_max * precipitacao / 1_000
            volume_final = min(volume_maximo,  volume_inicial + volume_afluente - volume_turbinado\
                - volume_retirada + area_max * (precipitacao - evaporacao) / 1_000)
            
            bal_hidrico_periodo: ResultadoBHNoPeriodo = {
                'periodo': periodo,
                'cota_inicial': cota_inicial,
                'cota_final': cota_max,
                'vazao_afluente_m3_s': vazao_afluente,
                'vazao_turbinada_m3_s': vazao_turbinada,
                'vazao_demandas_m3_s': vazao_retirada,
                'precipitacao_mm': precipitacao,
                'evaporacao_mm': evaporacao,
                'area_lago_km2': area_max,
                'volume_afluente_hm3': volume_afluente,
                'volume_turbinado_hm3': volume_turbinado,
                'volume_inicial_hm3': volume_inicial,
                'volume_final_hm3':  volume_final,
                'volume_vertido_hm3': volume_vertido,
                'volume_evaporado_hm3': volume_evap_lago,
                'volume_precipitado_hm3': volume_prec_lago
            }    

        elif volume_final <= volume_minimo:
            volume_final = volume_minimo
            volume_vertido = 0
            cota_final = reservatorio.cav.calcula_cota_por(volume=volume_final)
            area_corresp_final = reservatorio.cav.calcula_area_por(cota=cota_final)
            
            volume_evap_lago = area_corresp_final * evaporacao / 1_000
            volume_prec_lago = area_corresp_final * precipitacao / 1_000
            
            delta_vol = max(0, volume_inicial - volume_minimo - volume_evap_lago + volume_prec_lago)
        
            if prioridade_de_atendimento == "Vazão das Demandas":
                vazao_retirada = min(vazao_retirada, delta_vol / factor_q_to_vol)
                volume_retirada = vazao_retirada * factor_q_to_vol
                delta_vol = max(0, volume_inicial - volume_minimo + volume_afluente\
                    -volume_retirada - volume_evap_lago + volume_prec_lago)
                vazao_turbinada = min(vazao_turbinada, delta_vol / factor_q_to_vol)
                volume_turbinado = vazao_turbinada * factor_q_to_vol
                
            if prioridade_de_atendimento == "Vazão Turbinada":
                vazao_turbinada = min(vazao_turbinada, delta_vol / factor_q_to_vol)
                volume_turbinado = vazao_turbinada * factor_q_to_vol
                delta_vol = max(0, volume_inicial - volume_minimo + volume_afluente\
                    - volume_turbinado - volume_evap_lago + volume_prec_lago)
                vazao_retirada = min(vazao_retirada, delta_vol / factor_q_to_vol)
                volume_retirada = vazao_retirada * factor_q_to_vol
            
            bal_hidrico_periodo: ResultadoBHNoPeriodo = {
                'periodo': periodo,
                'cota_inicial': cota_inicial,
                'cota_final': cota_final,
                'vazao_afluente_m3_s': vazao_afluente,
                'vazao_turbinada_m3_s': vazao_turbinada,
                'vazao_demandas_m3_s': vazao_retirada,
                'precipitacao_mm': precipitacao,
                'evaporacao_mm': evaporacao,
                'area_lago_km2': area_corresp_final,
                'volume_afluente_hm3': volume_afluente,
                'volume_turbinado_hm3': volume_turbinado,
                'volume_inicial_hm3': volume_inicial,
                'volume_final_hm3':  volume_final,
                'volume_vertido_hm3': volume_vertido,
                'volume_evaporado_hm3': volume_evap_lago,
                'volume_precipitado_hm3': volume_prec_lago
            }    
            
        elif volume_minimo < volume_final <= volume_maximo:
            volume_vertido = 0
            dados_evapo = calc_evp(
                    reservatorio=reservatorio, 
                    volume_inicial=volume_inicial,
                    row=row,
                    factor_q_to_vol=factor_q_to_vol
                )
            
            cota_final = dados_evapo['cota_final']
            area_lago = dados_evapo['area_lago_km2']
            volume_evap_lago = dados_evapo['volume_evaporado_hm3']
            volume_prec_lago = dados_evapo['volume_precipitado_hm3']

            volume_final = volume_inicial + volume_afluente - volume_evap_lago + volume_prec_lago\
                - volume_retirada - volume_turbinado 
                
            bal_hidrico_periodo: ResultadoBHNoPeriodo = {
                'periodo': periodo,
                'cota_inicial': cota_inicial,
                'cota_final': cota_final,
                'vazao_afluente_m3_s': vazao_afluente,
                'vazao_turbinada_m3_s': vazao_turbinada,
                'vazao_demandas_m3_s': vazao_retirada,
                'evaporacao_mm': evaporacao,
                'precipitacao_mm': precipitacao,
                'area_lago_km2': area_lago,
                'volume_afluente_hm3': volume_afluente,
                'volume_turbinado_hm3': volume_turbinado,
                'volume_inicial_hm3': volume_inicial,
                'volume_final_hm3': volume_final,
                'volume_vertido_hm3': volume_vertido,
                'volume_evaporado_hm3': volume_evap_lago,
                'volume_precipitado_hm3': volume_prec_lago
            }

        resultado.append(bal_hidrico_periodo)
        volume_inicial = volume_final
        cota_inicial = cota_final
    return resultado
