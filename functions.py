
import numpy as np
import pandas as pd

class Inversion_pasiva:
    def __init__(self):
        pass
    def Inv_pasiva(self,historico: "dataframe with historico", pesos_p: "vector with pesos_p", cash: "capital_f of cash",
               initial_capital: "initial capital_f of money"):
        rend_pasivos = pd.DataFrame()
        Comisiones = lambda securitie, price: securitie * price * 0.00125
        Pesos = (initial_capital) * pesos_p
        n_sec = (Pesos / historico.iloc[0, :]).round(0)
        cash = cash - sum([Comisiones(n_sec[i], historico.iloc[0, i]) for i in range(len(n_sec))])
        capital_f = [(n_sec.to_numpy()).dot(historico.iloc[i, :].to_numpy()) for i in range(len(historico))]
        port_passive = pd.DataFrame(index=historico.index, columns=['Capital'], data=capital_f)
        port_passive['Capital'] = port_passive.Capital + cash # correction with the cash
        rend_pasivos['Capital'] = port_passive['Capital']
        rend_pasivos['Rend'] = port_passive.Capital.pct_change().fillna(0).round(6)
        rend_pasivos['Rend_acum'] = 100 * ((rend_pasivos.Rend + 1).cumprod() - 1).round(6)
        rend_pasivos['Rend'] = 100 * rend_pasivos.Rend
        return rend_pasivos

class Inversion_activa:

    def __init__(self):
        pass


