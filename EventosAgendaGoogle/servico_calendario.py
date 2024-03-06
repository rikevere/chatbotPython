# Este arquivo contém a função para autenticar e criar o serviço do Google Calendar.

from google.oauth2 import service_account
import googleapiclient.discovery

def pegar_servico_calendario():
    SERVICE_ACCOUNT_FILE = 'limalimao-contaservico-calendar-385623-1dc70aea7637.json'
    SCOPES = ['https://www.googleapis.com/auth/calendar']

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
    return service
