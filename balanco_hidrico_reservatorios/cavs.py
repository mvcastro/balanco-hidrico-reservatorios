from typing import Protocol, TypedDict

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from balanco_hidrico_reservatorios.conversor import _calcula_interpolacao_por_variaveis

class DataFrameCavInvalidoErro(Exception):
    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem)


def __checa_validade_dataframe(cav: pd.DataFrame, col_cota: str, col_area: str | None, col_vol: str) -> None:
    colunas = [col_cota, col_area, col_vol] if col_area else [col_cota, col_vol]
    checagem = [col in cav.columns for col in colunas]
    if not all(checagem):
        raise DataFrameCavInvalidoErro(f"Nome das Colunas Inválidas! - Colunas Válidas: {list(cav.columns)}")
    if cav[colunas].isnull().values.any():
        raise DataFrameCavInvalidoErro("Dados da CAV não podem ter valores nulos!")
    if (cav[colunas].sort_values(col_cota).diff() < 0).values.any():
        raise DataFrameCavInvalidoErro(
            "Existem dados da CAV que não estão em ordem!\n"
            "Cota[i] < Cota[i+1] - Area[i] < Area[i+1] - Vol[i] < Vol[i+1]"
    )

def checa_validade_dataframe_da_cav(cav: pd.DataFrame, col_cota: str, col_area: str, col_vol: str) -> None:
    __checa_validade_dataframe(cav=cav, col_cota=col_cota, col_area=col_area, col_vol=col_vol)
     
   
def checa_validade_dataframe_da_curva_cota_volume(cav: pd.DataFrame, col_cota: str, col_vol: str) -> None:
    __checa_validade_dataframe(cav=cav, col_cota=col_cota, col_area=None, col_vol=col_vol)


class ParametrosPolinomiosONS(TypedDict):
    a: float
    b: float
    c: float
    d: float
    e: float


class CAV(Protocol):

    def calcula_area_por(self, *, cota: float) -> float:
        ...

    def calcula_areas_por(self, *, cotas: NDArray) -> NDArray:
        ...
        
    def calcula_volume_por(self, *, cota: float) -> float:
        ...

    def calcula_volumes_por(self, *, cotas: NDArray) -> NDArray:
        ...
    
    def calcula_cota_por(self, *, volume: float) -> float:
        ...

    def calcula_cotas_por(self, *, volumes: NDArray) -> NDArray:
        ...


class CavReservatorio:
    """Classe que representa a Curva Cota-Área-Volume de um Reservatório"""

    def __init__(self, cav: pd.DataFrame, col_cota: str, col_area: str, col_vol: str) -> None:
        checa_validade_dataframe_da_cav(cav, col_cota, col_area, col_vol)
        self.col_cota = col_cota
        self.col_area = col_area
        self.col_vol = col_vol
        self.cav = cav.copy().sort_values(col_cota)

    def calcula_area_por(self, cota: float) -> float:
        area = _calcula_interpolacao_por_variaveis(
            dados_cav=self.cav,
            coluna_dados_interp=self.col_area,
            coluna_dados_ref=self.col_cota,
            valor=np.array([cota]))
        return area[0]

    def calcula_areas_por(self, cotas: NDArray) -> NDArray:
        areas = _calcula_interpolacao_por_variaveis(
            dados_cav=self.cav,
            coluna_dados_interp=self.col_area,
            coluna_dados_ref=self.col_cota,
            valor=cotas)
        return areas
    
    def calcula_volume_por(self, *, cota: float) -> float:
        volumes = _calcula_interpolacao_por_variaveis(
            dados_cav=self.cav,
            coluna_dados_interp=self.col_vol,
            coluna_dados_ref=self.col_cota,
            valor=np.array([cota])
        )
        return volumes[0]

    def calcula_volumes_por(self, *, cotas: NDArray) -> NDArray:
        volumes = _calcula_interpolacao_por_variaveis(
            dados_cav=self.cav,
            coluna_dados_interp=self.col_vol,
            coluna_dados_ref=self.col_cota,
            valor=cotas
        )
        return volumes
    
    def calcula_cota_por(self, *, volume: float) -> float:
        cotas = _calcula_interpolacao_por_variaveis(
            dados_cav=self.cav,
            coluna_dados_interp=self.col_cota,
            coluna_dados_ref=self.col_vol,
            valor=np.array([volume])
        )
        return cotas[0]

    def calcula_cotas_por(self, *, volumes: NDArray) -> NDArray:
        cotas = _calcula_interpolacao_por_variaveis(
            dados_cav=self.cav,
            coluna_dados_interp=self.col_cota,
            coluna_dados_ref=self.col_vol,
            valor=volumes
        )
        return cotas


class CurvaCotaVolumeONS:

    def __init__(self, curva_cota_volume: pd.DataFrame, coluna_cota: str, coluna_volume: str) -> None:
        checa_validade_dataframe_da_curva_cota_volume(curva_cota_volume, coluna_cota, coluna_volume)
        self.coluna_cota = coluna_cota
        self.coluna_volume = coluna_volume
        self.curva_cota_volume = curva_cota_volume.copy().sort_values(coluna_cota)

    def calcula_volume_por(self, cota: float) -> float:
        volume = _calcula_interpolacao_por_variaveis(
            dados_cav=self.curva_cota_volume,
            coluna_dados_interp=self.coluna_volume,
            coluna_dados_ref=self.coluna_cota,
            valor=np.array([cota]))
        return volume[0]

    def calcula_volumes_por(self, cotas: NDArray) -> NDArray:
        volumes = _calcula_interpolacao_por_variaveis(
            dados_cav=self.curva_cota_volume,
            coluna_dados_interp=self.coluna_volume,
            coluna_dados_ref=self.coluna_cota,
            valor=cotas)
        return volumes
    
    def calcula_cota_por(self, volume: float) -> float:
        cota = _calcula_interpolacao_por_variaveis(
            dados_cav=self.curva_cota_volume,
            coluna_dados_interp=self.coluna_cota,
            coluna_dados_ref=self.coluna_volume,
            valor=np.array([volume]))
        return cota[0]

    def calcula_cotas_por(self, volumes: NDArray) -> NDArray:
        cotas = _calcula_interpolacao_por_variaveis(
            dados_cav=self.curva_cota_volume,
            coluna_dados_interp=self.coluna_volume,
            coluna_dados_ref=self.coluna_cota,
            valor=volumes)
        return cotas


class CavReservatorioONS:

    def __init__(
        self,
        params_area_fn_volume: ParametrosPolinomiosONS,
        # params_cota_fn_vol: ParametrosPolinomiosONS,
        curva_cota_volume: CurvaCotaVolumeONS
    ) -> None:
        
        self.curva_cota_volume = curva_cota_volume
        self.polinomial_area_fn_cota = self.__retorna_polinomial(params_area_fn_volume)
        # self.polinomial_cota_fn_volume = self.__retorna_polinomial(params_cota_fn_vol)

    def __retorna_polinomial(self, cav: ParametrosPolinomiosONS):
        params = [cav[i] for i in ('a', 'b', 'c', 'd')]
        return np.polynomial.Polynomial(params)

    def calcula_area_por(self, *, cota: float) -> float:
        return self.polinomial_area_fn_cota(cota)

    def calcula_areas_por(self, *, cotas: NDArray) -> NDArray:
        return self.polinomial_area_fn_cota(cotas)

    def calcula_volume_por(self, *, cota: float) -> float:
        return self.curva_cota_volume.calcula_volume_por(cota=cota)

    def calcula_volumes_por(self, *, cotas: NDArray) -> NDArray:
        return self.curva_cota_volume.calcula_volumes_por(cotas=cotas)
    
    def calcula_cota_por(self, *, volume: float) -> float:
        return self.curva_cota_volume.calcula_cota_por(volume=volume)

    def calcula_cotas_por(self, *, volumes: NDArray) -> NDArray:
        return self.calcula_cotas_por(volumes=volumes)