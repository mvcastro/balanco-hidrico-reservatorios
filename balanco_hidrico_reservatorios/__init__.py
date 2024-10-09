from typing import TypedDict


MESES: dict[int, str] = {
    1: 'jan',
    2: 'fev',
    3: 'mar',
    4: 'abr',
    5: 'mai',
    6: 'jun',
    7: 'jul',
    8: 'ago',
    9: 'set',
    10: 'out',
    11: 'nov',
    12: 'dez'
}

class DadoMedioMensal(TypedDict):
    jan: float
    fev: float
    mar: float
    abr: float
    mai: float
    jun: float
    jul: float
    ago: float
    set: float
    out: float
    nov: float
    dez: float
