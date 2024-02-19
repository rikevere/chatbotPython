from datetime import datetime, timedelta

def obter_intervalo_data(periodo, data_referencia):
    # Define a data de referência
    if not data_referencia:
        data_referencia = datetime.now()
    else:
        # Assume que data_referencia está no formato "dd/mm/aaaa"
        data_referencia = datetime.strptime(data_referencia, "%d/%m/%Y")
    
    if periodo.lower() == "hoje":
        dtini = dtfim = data_referencia.strftime("%m-%d-%Y")
    
    elif periodo.lower() == "semana":
        # Calcula o início da semana (segunda-feira)
        dtini = data_referencia - timedelta(days=data_referencia.weekday())
        # Calcula o fim da semana (domingo)
        dtfim = dtini + timedelta(days=6)
        dtini = dtini.strftime("%m-%d-%Y")
        dtfim = dtfim.strftime("%m-%d-%Y")
    
    elif periodo.lower() == "mês":
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
    
    else:
        return "Período não reconhecido."
    return dtini, dtfim

# Exemplo de uso
#data_referencia = "13/04/2023"  # Data de referência para os cálculos
#periodo = "MÊS"  # Pode ser "hoje", "semana", "mês", "ano"

#dtini, dtfim = obter_intervalo_data(periodo, data_referencia)
#print(f"Período: {periodo.capitalize()}, Data Inicial: '{dtini}', Data Final: {dtfim}")
