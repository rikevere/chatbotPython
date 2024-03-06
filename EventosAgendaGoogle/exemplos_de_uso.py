#Este arquivo contém exemplos de uso de cada método.

from criar_evento_calendario import criar_evento
from atualiza_evento_calendario import atualizar_evento
from chatbotPython.EventosAgendaGoogle.listar_eventos_calendario import lista_evento_encontra_id

IdAgenda = {'Ricardo': "rikevere@gmail.com"}
event_id = ''
corEvento = {'Lavanda': 1,
             'Sálvia': 2,
             'Uva': 3,
             'Flamingo': 4,
             'Banana': 5,
             'Tangerina': 6,
             'Pimenta': 7,
             'Azul': 8,
             'Grafite': 9,
             'Tomate': 10,
             'Turquesa': 11}


# Exemplo de uso para criar um evento
criar_evento(
    IdAgenda['Ricardo'],
    'Reunião de Planejamento',
    'Discussão sobre o projeto X',
    '2024-03-06T13:00:00-03:00',
    '2024-03-06T14:00:00-03:00',
    corEvento['Pimenta']
)

# Exemplo de uso para listar eventos e encontrar um ID
event_id = lista_evento_encontra_id(
    IdAgenda['Ricardo'],
    search_summary='Reunião de Planejamento'
)
print(event_id)

# Exemplo de uso para atualizar um evento (assumindo que você tenha o event_id)
if event_id:
    atualizar_evento(
        IdAgenda['Ricardo'],
        event_id,
            {
            'summary': 'Reunião Atualizada',  # Novo título do evento
            'description': 'Discussão sobre as atualizações do projeto',  # Nova descrição
            'start': {
                'dateTime': '2024-03-06T16:00:00-03:00',  # Novo horário de início
                'timeZone': 'America/Sao_Paulo',
            },
            'end': {
                'dateTime': '2024-03-06T17:00:00-03:00',  # Novo horário de término
                'timeZone': 'America/Sao_Paulo',
            },
            'colorId': corEvento['Tangerina']  # Novo colorId para o evento
            }
    )
    print('evento atualizado!')
