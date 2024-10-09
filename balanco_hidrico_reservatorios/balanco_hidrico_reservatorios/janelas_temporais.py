from balanco_hidrico_reservatorios.balanco_hidrico import ResultadoBHNoPeriodo

JanelasTemporais = dict[str, list[ResultadoBHNoPeriodo]]

# def executa_janelas_temporais_mensais(
#     reservatorio: ReservatorioONS,
#     serie_temporal: SerieTemporal | None,
#     year: int,
#     janela_em_anos: int = 1
# ) -> JanelasTemporais:
    
#     janelas_temporais: JanelasTemporais = {}

#     serie_temporal = reservatorio.serie_temporal if serie_temporal is None else serie_temporal
#     df_serie = serie_temporal.dataframe
#     periodo_inicial = df_serie.index.max()
#     periodo_final = df_serie.index.min()
    
    
#     if mes_inicial <= 12:
#         period_ini = f"{year}-{mes_inicial}"
#         period_fin = f"{year + window_of_years}-{mes_inicial - 1}"
#     else:
#         period_ini = f"{year + 1}-{1}"
#         period_fin = f"{year + window_of_years}-{12}"

#     serie = SerieTemporal()
    
#     calcula_balanco_hidrico(
#         reservatorio=reservatorio,
        
        
#     )
