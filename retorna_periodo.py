from datetime import datetime, timedelta



def obter_intervalo_data(periodo, data_referencia, anoref):
    # Define a data de referência
    if not data_referencia:
        data_referencia = datetime.now()
    else:
        # Assume que data_referencia está no formato "dd/mm/aaaa"
        data_referencia = datetime.strptime(data_referencia, "%d/%m/%Y")
    #verifica se foi informado ano na consulta
    if not anoref:
        ano = data_referencia.year
        print(f"Ano Sistema: {ano}")
    else:
        ano = int(anoref)
        print(f"anoref: {ano}")
    
    if periodo.lower() == "hoje":
        dtini = dtfim = data_referencia.strftime("%m-%d-%Y")
    
    elif periodo.lower() == "semana" or periodo.lower() == "semanal":
        # Calcula o início da semana (segunda-feira)
        dtini = data_referencia - timedelta(days=data_referencia.weekday())
        # Calcula o fim da semana (domingo)
        dtfim = dtini + timedelta(days=6)
        dtini = dtini.strftime("%m-%d-%Y")
        dtfim = dtfim.strftime("%m-%d-%Y")
    
    elif periodo.lower() == "mês" or periodo.lower() == "mes" or periodo.lower() == "mensal":
        # Primeiro dia do mês
        dtini = data_referencia.replace(day=1)
        # Último dia do mês
        if data_referencia.month == 12:
            dtfim = data_referencia.replace(day=31)
        else:
            dtfim = data_referencia.replace(month=data_referencia.month+1, day=1) - timedelta(days=1)
        dtini = dtini.strftime("%m-%d-%Y")
        dtfim = dtfim.strftime("%m-%d-%Y")
    
    elif periodo.lower() == "ano":
        # Primeiro dia do ano
        dtini = data_referencia.replace(month=1, day=1)
        # Último dia do ano
        dtfim = data_referencia.replace(month=12, day=31)
        dtini = dtini.strftime("%m-%d-%Y")
        dtfim = dtfim.strftime("%m-%d-%Y")

    elif periodo.lower() == "primeiro bimestre":
        dtini = datetime(ano, 1, 1)
        dtfim = datetime(ano, 2, 28)
        dtini = dtini.strftime("%m-%d-%Y")
        dtfim = dtfim.strftime("%m-%d-%Y")

    elif periodo.lower() == "segundo bimestre":
        dtini = datetime(ano, 3, 1)
        dtfim = datetime(ano, 4, 30)
        dtini = dtini.strftime("%m-%d-%Y")
        dtfim = dtfim.strftime("%m-%d-%Y")

    elif periodo.lower() == "terceiro bimestre":
        dtini = datetime(ano, 5, 1)
        dtfim = datetime(ano, 6, 30)
        dtini = dtini.strftime("%m-%d-%Y")
        dtfim = dtfim.strftime("%m-%d-%Y")    

    elif periodo.lower() == "quarto bimestre":
        dtini = datetime(ano, 6, 1)
        dtfim = datetime(ano, 8, 31)
        dtini = dtini.strftime("%m-%d-%Y")
        dtfim = dtfim.strftime("%m-%d-%Y")    
    
    elif periodo.lower() == "quinto bimestre":
        dtini = datetime(ano, 9, 1)
        dtfim = datetime(ano, 10, 31)
        dtini = dtini.strftime("%m-%d-%Y")
        dtfim = dtfim.strftime("%m-%d-%Y")   

    elif periodo.lower() == "sexto bimestre":
        dtini = datetime(ano, 11, 1)
        dtfim = datetime(ano, 12, 31)
        dtini = dtini.strftime("%m-%d-%Y")
        dtfim = dtfim.strftime("%m-%d-%Y")   

    elif periodo.lower() == "primeiro trimestre":
        dtini = datetime(ano, 1, 1)
        dtfim = datetime(ano, 3, 31)
        dtini = dtini.strftime("%m-%d-%Y")
        dtfim = dtfim.strftime("%m-%d-%Y")
    
    elif periodo.lower() == "segundo trimestre":
        dtini = datetime(ano, 4, 1)
        dtfim = datetime(ano, 6, 30)
        dtini = dtini.strftime("%m-%d-%Y")
        dtfim = dtfim.strftime("%m-%d-%Y")

    elif periodo.lower() == "terceiro trimestre":
        dtini = datetime(ano, 7, 1)
        dtfim = datetime(ano, 9, 30)
        dtini = dtini.strftime("%m-%d-%Y")
        dtfim = dtfim.strftime("%m-%d-%Y")

    elif periodo.lower() == "quarto trimestre":
        dtini = datetime(ano, 10, 1)
        dtfim = datetime(ano, 12, 31)
        dtini = dtini.strftime("%m-%d-%Y")
        dtfim = dtfim.strftime("%m-%d-%Y")
    
    elif periodo.lower() == "primeiro semestre":
        dtini = datetime(ano, 1, 1)
        dtfim = datetime(ano, 6, 30)
        dtini = dtini.strftime("%m-%d-%Y")
        dtfim = dtfim.strftime("%m-%d-%Y")
    
    elif periodo.lower() == "segundo semestre":
        dtini = datetime(ano, 7, 1)
        dtfim = datetime(ano, 12, 31)
        dtini = dtini.strftime("%m-%d-%Y")
        dtfim = dtfim.strftime("%m-%d-%Y")
    
    elif periodo.lower() == "primeiro quatrimestre":
        dtini = datetime(ano, 1, 1)
        dtfim = datetime(ano, 4, 30)
        dtini = dtini.strftime("%m-%d-%Y")
        dtfim = dtfim.strftime("%m-%d-%Y")
    
    elif periodo.lower() == "segundo quatrimestre":
        dtini = datetime(ano, 5, 1)
        dtfim = datetime(ano, 8, 31)   
        dtini = dtini.strftime("%m-%d-%Y")
        dtfim = dtfim.strftime("%m-%d-%Y")

    elif periodo.lower() == "terceiro quatrimestre":
        dtini = datetime(ano, 9, 1)
        dtfim = datetime(ano, 12, 31)   
        dtini = dtini.strftime("%m-%d-%Y")
        dtfim = dtfim.strftime("%m-%d-%Y")
    
    else:
        dtini = data_referencia
        dtfim = data_referencia
        dtini = dtini.strftime("%m-%d-%Y")
        dtfim = dtfim.strftime("%m-%d-%Y")
        return dtini, dtfim
    return dtini, dtfim

# Exemplo de uso
#data_ludwig = None  # Data de referência para os cálculos
#anoteste = '2023'
#periodo = "Semestre"  # Pode ser "hoje", "semana", "mês", "ano"


#dtini, dtfim = obter_intervalo_data(periodo, data_ludwig, anoteste)
#print(f"Período: {periodo.capitalize()}, Data Inicial: '{dtini}', Data Final: {dtfim}")
