import numpy as np
import pandas as pd
from numpy.typing import NDArray


def converte_para(variable_volume_curve: pd.DataFrame, variable: float, variable_name="cota") -> float:

    if variable_name == 'cota':
        arr_variable = variable_volume_curve['cota_m'].to_numpy()
        arr_target = variable_volume_curve['volume_hm3'].to_numpy()

    if variable_name == 'volume':
        arr_variable = variable_volume_curve['volume_hm3'].to_numpy()
        arr_target = variable_volume_curve['cota_m'].to_numpy()

    idx = np.searchsorted(arr_variable, variable)

    if variable <= arr_variable[0]:
        idxLeft = idx
        idxRight = idx + 1
    elif variable >= arr_variable[len(arr_variable) - 1]:
        idxLeft = idx - 2
        idxRight = idx - 1
    else:
        idxLeft = idx - 1
        idxRight = idx

    variableLeft = arr_variable[idxLeft]
    variableRight = arr_variable[idxRight]
    volumeLeft = arr_target[idxLeft]
    volumeRight = arr_target[idxRight]

    volume = volumeRight - (variableRight - variable) * \
        (volumeRight - volumeLeft) / (variableRight - variableLeft)

    return volume


def _calcula_interpolacao_por_variaveis(
    dados_cav: pd.DataFrame,
    coluna_dados_interp: str,
    coluna_dados_ref: str,
    valor: NDArray
) -> NDArray:

    arr_variable = dados_cav[coluna_dados_ref].to_numpy()
    arr_target = dados_cav[coluna_dados_interp].to_numpy()

    idx = np.searchsorted(arr_variable, valor)
    idx_corrigido = np.where(idx < arr_target.size - 1, idx, arr_target.size - 1)
    idx_esq = np.where(idx_corrigido < arr_target.size - 1, idx_corrigido, idx_corrigido - 1)
    idx_dir = np.where(idx_corrigido < arr_target.size - 2, idx_corrigido + 1, arr_target.size - 1)

    variavel_esq = arr_variable[idx_esq]
    variavel_dir = arr_variable[idx_dir]
    valor_esq = arr_target[idx_esq]
    valor_dir = arr_target[idx_dir]

    valor_resultante = valor_dir - (variavel_dir - valor) * \
        (valor_dir - valor_esq) / (variavel_dir - variavel_esq)

    return valor_resultante