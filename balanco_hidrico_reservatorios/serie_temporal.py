from dataclasses import dataclass, field
from typing import Literal, TypedDict

import pandas as pd

Frequencia = Literal['D', 'M']


class SerieTemporalInvalida(Exception):
    def __init__(self, message):
        self.message = message

class SequenciaDaSerieTemporalComFalha(Exception):
    def __init__(self, message):
        self.message = message

class NomeDaColunaInvalida(Exception): 
    def __init__(self, message):
        self.message = message


def _checa_indice_da_serie_temporal(serie_temporal: pd.DataFrame, freq: Frequencia) -> None:
    indice_serie = serie_temporal.index
    
    if freq == 'D':
        if not isinstance(indice_serie, pd.DatetimeIndex):
            raise SerieTemporalInvalida(
                "O DataFrame da série temporal com frequeência diária deve ser do Tipo "
                f"DatetimeIndex -> tipo atual: {type(indice_serie)}"
            )
            
    if freq == 'M':
        if not isinstance(indice_serie, pd.PeriodIndex):
            raise SerieTemporalInvalida(
            "O DataFrame da série temporal com frequência mensal deve ser do Tipo "
            f"PeriodIndex -> tipo atual: {type(indice_serie)}")
        
        
def _checa_falhas_nas_datas_da_serie_temporal(serie_temporal: pd.DataFrame, freq: Frequencia = 'M') -> None:
    indice_serie = serie_temporal.index
    
    if freq == 'D':
        date_range = pd.date_range(indice_serie.min(), indice_serie.max(), freq=freq)
    if freq == 'M':
        date_range = pd.period_range(indice_serie.min(), indice_serie.max(), freq=freq)
    
    if not indice_serie.equals(date_range):
        datas_ausentes = [i for i in indice_serie if i not in date_range]
        raise SequenciaDaSerieTemporalComFalha(
            "A série temporal não está completa -> Datas ausentes: \n"
            f"{datas_ausentes}"
        )


def _checa_nome_das_colunas(serie_temporal: pd.DataFrame, nome_das_colunas: list[str]) -> None:
    colunas_do_dataframe = serie_temporal.columns
    
    for nome_da_coluna in nome_das_colunas:
        if nome_da_coluna not in colunas_do_dataframe:
            raise NomeDaColunaInvalida(
                f"Coluna '{nome_da_coluna}' não existe no DataFrame -> colunas do DataFrame: \n"
                f"{colunas_do_dataframe}"
            )


class ColunasSerieTemporal(TypedDict):
    vazao_afluente: str
    vazao_turbinada: str
    vazao_retirada: str
    evaporacao: str
    precipitacao: str


@dataclass
class SerieTemporal:
    dataframe: pd.DataFrame = field(repr=False)
    nome_das_colunas: ColunasSerieTemporal
    freq: Frequencia

