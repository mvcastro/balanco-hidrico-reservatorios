from typing import TypedDict

import numpy as np
import pandas as pd

from balanco_hidrico_reservatorios.balanco_hidrico import calcula_balanco_hidrico
from balanco_hidrico_reservatorios.reservatorios import Reservatorio
from balanco_hidrico_reservatorios.serie_temporal import SerieTemporal

class Regularizacao(TypedDict):
    vazao: float
    percentual_atendido: float


def gera_curva_de_regularizacao(
    reservatorio: Reservatorio,
    serie_temporal: SerieTemporal,
    faixa_de_vazoes: tuple[float, float],
    percentual_volume_inicial: int = 50,
) -> list[Regularizacao]:
    
    nome_das_colunas = serie_temporal.nome_das_colunas
    df_serie = serie_temporal.dataframe
    df_serie[nome_das_colunas['vazao_turbinada']] = 0
    
    curva_de_regularizacao: list[Regularizacao] = []
    for vazao in np.linspace(start=faixa_de_vazoes[0], stop=faixa_de_vazoes[1], num=100)[::-1]:
        df_serie[nome_das_colunas['vazao_retirada']] = vazao
        
        balanco_hidrico = calcula_balanco_hidrico(
            reservatorio=reservatorio,
            serie_temporal=SerieTemporal(
                dataframe=df_serie,
                nome_das_colunas=nome_das_colunas, 
                freq=serie_temporal.freq
            ),
            percentual_volume_inicial=percentual_volume_inicial,
            prioridade_de_atendimento='Vazão das Demandas'
        )
        
        percentual_atendido = np.sum(
            [1 for i in balanco_hidrico if i["vazao_demandas_m3_s"] >= vazao]
            ) * 100 / len(balanco_hidrico)
        
        curva_de_regularizacao.append({
            'vazao': vazao,
            'percentual_atendido': percentual_atendido
        })
        
        if percentual_atendido >= 100:
            break
          
    return curva_de_regularizacao


def localiza_faixa_de_vazoes_por(*, 
    curva_de_regularizacao: list[Regularizacao],
    percentual_atendido: float
) -> tuple[Regularizacao, Regularizacao] | None:
    
    for i, dado in enumerate(curva_de_regularizacao):
        if dado["percentual_atendido"] > percentual_atendido:
            return (
                curva_de_regularizacao[i-1],
                curva_de_regularizacao[i]
            )


def calcula_curva_de_regularizada(
    reservatorio: Reservatorio,
    serie_temporal: SerieTemporal | None,
    percentual_volume_inicial: int = 50,
) -> list[Regularizacao]:
    
    percentuais_de_atendimento = list(range(1, 100))
    
    if serie_temporal is None:
        serie_temporal = reservatorio.serie_temporal
    
    nome_das_colunas = serie_temporal.nome_das_colunas
    df_serie = serie_temporal.dataframe
    vazao_media = df_serie[nome_das_colunas['vazao_afluente']].mean()

    curva_reg_inicial = gera_curva_de_regularizacao(
        reservatorio=reservatorio,
        serie_temporal=serie_temporal,
        faixa_de_vazoes=(0, vazao_media * 5)
    )
    
    curva_de_regularizacao: list[Regularizacao] = []
    for percentual in percentuais_de_atendimento:
        
        faixa_de_vazoes = localiza_faixa_de_vazoes_por(
            curva_de_regularizacao=curva_reg_inicial,
            percentual_atendido=percentual
        )
        
        if faixa_de_vazoes:
            vazao_inf = faixa_de_vazoes[0]['vazao']
            perc_inf = faixa_de_vazoes[0]['percentual_atendido']
            vazao_sup = faixa_de_vazoes[1]['vazao']
            perc_sup = faixa_de_vazoes[1]['percentual_atendido']
            vazao = vazao_inf + (vazao_sup - vazao_inf) * (percentual - perc_inf) / (perc_sup - perc_inf)
            curva_de_regularizacao.append({'vazao': vazao, "percentual_atendido": percentual})
            
    return curva_de_regularizacao