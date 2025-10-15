from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from typing import List


class GoogleSheetsClient:
    """
    Клиент Google Sheets API через сервисный аккаунт.
    Требует credentials-файл сервис-аккаунта (формат JSON), созданный в Google Cloud Console.
    Для доступа к таблице её надо расшарить на email сервис-аккаунта.
    """

    def __init__(self, credentials_path: str, scopes=None):
        if scopes is None:
            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        self.creds = Credentials.from_service_account_file(
            credentials_path, scopes=scopes)
        self.service = build("sheets", "v4", credentials=self.creds)

    def read_range(self, sheet_id: str, range_: str) -> List[List[str]]:
        """
        Читает диапазон из Google Sheets.
        :param sheet_id: ID Google таблицы
        :param range_: диапазон (например, 'Лист1!A1:C10')
        :return: двумерный список значений
        """
        sheet = self.service.spreadsheets()
        result = sheet.values().get(spreadsheetId=sheet_id, range=range_).execute()
        return result.get('values', [])

    def write_range(self, sheet_id: str, range_: str, values: List[List[str]]):
        """
        Записывает значения в заданный диапазон Google Sheets.
        :param sheet_id: ID Google таблицы
        :param range_: диапазон (например, 'Лист1!A1')
        :param values: двумерный список значений (например, [["one", "two"], ["three", "four"]])
        """
        sheet = self.service.spreadsheets()
        body = {'values': values}
        result = sheet.values().update(
            spreadsheetId=sheet_id,
            range=range_,
            valueInputOption="RAW",
            body=body
        ).execute()
        return result

    def append_row(self, sheet_id: str, values: List[str], sheet_name: str = None):
        """
        Добавляет строку в конец листа Google Sheets.
        :param sheet_id: ID таблицы
        :param values: список значений (одна строка)
        :param sheet_name: имя листа (по умолчанию - первый лист)
        :return: результат операции
        """
        sheet = self.service.spreadsheets()
        range_ = f"{sheet_name}!A1" if sheet_name else "A1"
        body = {'values': [values]}
        result = sheet.values().append(
            spreadsheetId=sheet_id,
            range=range_,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()
        return result
