# Este arquivo contém a função para criar um evento
from datetime import datetime, timedelta
import pytz
#from servico_calendario import pegar_servico_calendario
from EventosAgendaGoogle.exemplos_de_uso import corEvento

def criar_evento(calendar_id, title, description, start_time, end_time, color_id=None):
    #service = pegar_servico_calendario()
    event_body = {
        'summary': title,
        'description': description,
        'start': {'dateTime': start_time, 'timeZone': 'America/Sao_Paulo'},
        'end': {'dateTime': end_time, 'timeZone': 'America/Sao_Paulo'},
    }
    if color_id:
        event_body['colorId'] = color_id

    #event = service.events().insert(calendarId=calendar_id, body=event_body).execute()
    #print('Evento criado: %s' % (event.get('htmlLink')))


def criar_evento_chatgpt(argumentos):
    calendar_id = argumentos.get("calendar_id")
    title = argumentos.get("title")
    description = argumentos.get("description")
    start_time = argumentos.get("start_time")
    end_time = argumentos.get("end_time")
    nome_cor = argumentos.get("color_id")

    if not time_min:
        time_min = datetime.utcnow()
    if not time_max:
        time_max = datetime.utcnow()
    
    # Converte as datas para o formato correto
    time_min = time_min.isoformat() + 'Z'  # 'Z' indica UTC
    time_max = time_max.isoformat() + 'Z'

    if nome_cor:
        if nome_cor in corEvento:
            print(f"A cor {nome_cor} tem o ID {corEvento[nome_cor]}")
            nome_cor = corEvento[nome_cor]
        else:
            # Se a cor escolhida não estiver no dicionário, sugira a primeira opção
            primeira_cor = next(iter(corEvento))
            print(f"A cor {nome_cor} não está disponível. Sugerimos usar a cor {primeira_cor}, que tem o ID {corEvento[primeira_cor]}")
            nome_cor = corEvento[primeira_cor]

    service = pegar_servico_calendario()
    event_body = {
        'summary': title,
        'description': description,
        'start': {'dateTime': start_time, 'timeZone': 'America/Sao_Paulo'},
        'end': {'dateTime': end_time, 'timeZone': 'America/Sao_Paulo'},
        'color_Id': corEvento[nome_cor]
    }


    event = service.events().insert(calendarId=calendar_id, body=event_body).execute()
    print('Evento criado: %s' % (event.get('htmlLink')))