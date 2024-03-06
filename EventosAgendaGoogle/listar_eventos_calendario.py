# retorna o ID dos eventos buscados
from datetime import datetime, timedelta
import pytz
from servico_calendario import pegar_servico_calendario

def lista_evento_encontra_id(calendar_id, search_summary=None, time_min=None, time_max=None):
    service = pegar_servico_calendario()
    # Se não forem fornecidas datas mínima e máxima, busca eventos da última semana até a próxima semana
    if not time_min:
        time_min = datetime.utcnow() - timedelta(days=7)
    if not time_max:
        time_max = datetime.utcnow() + timedelta(days=7)
    
    # Converte as datas para o formato correto
    time_min = time_min.isoformat() + 'Z'  # 'Z' indica UTC
    time_max = time_max.isoformat() + 'Z'
    
    print(f"Buscando eventos de {time_min} até {time_max}...")
    
    events_result = service.events().list(calendarId=calendar_id,
                                          timeMin=time_min,
                                          timeMax=time_max,
                                          singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('Nenhum evento encontrado.')
        return None

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        if search_summary and search_summary.lower() in event['summary'].lower():
            print(f"Evento encontrado: {event['summary']} (ID: {event['id']}) - Início em {start}")
            return event['id']
        elif not search_summary:
            print(f"{event['summary']} (ID: {event['id']}) - Início em {start}")
            return None