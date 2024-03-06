# update_event.py

from servico_calendario import pegar_servico_calendario

def atualizar_evento(calendar_id, event_id, updated_event):
    service = pegar_servico_calendario()
    updated_event_result = service.events().update(calendarId=calendar_id, eventId=event_id, body=updated_event).execute()
    print('Evento atualizado: %s' % (updated_event_result.get('htmlLink')))
