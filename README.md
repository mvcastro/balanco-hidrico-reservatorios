# Balanço Hídrico de Reservatórios

Este pacote foi desenvolvido para possibilitar a excução do balanço hídrico de um reservtório\
considerando as entradas e saídas do reservatório e gerando uma planilha com os resultados.

## Exemplo de aplicação para um reservatório do ONS

Primeiramente, é necessário criar um objeto do tipo ReservatorioONS, em que vamos inserir todas\
as propriedades de volume, cota, curva Cota-Área-Volume e vetor de evaporação  do reservatório:

```python

from balanco_hidrico_reservatorios.cavs import CavReservatorioONS, CurvaCotaVolumeONS
from balanco_hidrico_reservatorios.reservatorios import (
    PropsCota, PropsVolume, ReservatorioONS
)
from balanco_hidrico_reservatorios.serie_temporal import (
    ColunasSerieTemporal, SerieTemporal
)

propriedades_volume = PropsVolume(util_total=17217.0, maximo=22950.0, minimo=5733.0, util=None)
propiedades_cota = PropsCota(maxima=768.00, minima=750.00)



````
