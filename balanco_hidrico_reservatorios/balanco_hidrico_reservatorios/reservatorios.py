from abc import ABC
from dataclasses import dataclass, field

import pandas as pd

from balanco_hidrico_reservatorios.cavs import CAV, CavReservatorio, CavReservatorioONS
from balanco_hidrico_reservatorios.serie_temporal import SerieTemporal


@dataclass
class PropsCota:
    maxima: float
    minima: float
    
    def __checa_valores_das_propriedades(self) -> None:
        if self.minima > self.maxima:
            raise ValueError("Volume mínimo dever ser menor qu eo Volume máximo!")

@dataclass
class PropsVolume:
    util_total: float | None
    maximo: float
    minimo: float
    util: float | None
    
    def __post_init__(self):
        self.__checa_valores_das_propriedades()
        if self.util_total is None:
            self.util_total = self.maximo - self.minimo

    def __checa_valores_das_propriedades(self) -> None:
        if self.minimo > self.maximo:
            raise ValueError("Volume mínimo dever ser menor qu eo Volume máximo!")
        

@dataclass
class Reservatorio(ABC):
    nome: str 
    esp_cd: int | None
    cod_sar: int | None
    area_ha: float | None
    latitude: float | None
    longitude: float | None
    volume: PropsVolume
    cota: PropsCota
    cav: CAV
    serie_temporal: SerieTemporal

    def __post_init__(self):
        if self.__class__ == Reservatorio:
            raise TypeError("Cannot instantiate abstract class.")


@dataclass
class ReservatorioSAR(Reservatorio):
    capacidade: float | None
    cav: CavReservatorio = field(repr=False)
    


@dataclass
class ReservatorioONS(Reservatorio):
    cod_ons: str | None
    nome_longo: str | None
    cav: CavReservatorioONS = field(repr=False)

    
    