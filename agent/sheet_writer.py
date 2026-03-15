import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

SHEET_NAME = "Academic Conferences Agent"

def connect_sheet():

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "google.json", scope
    )

    client = gspread.authorize(creds)

    return client.open(SHEET_NAME).sheet1


def write_row(data):

    sheet = connect_sheet()

    sheet.append_row([
        "",
        "",
        "",
        "",
        "",
        "",
        data["names"],
        "",
        "",
        "",
        data["link"],
        "",
        str(datetime.date.today())
    ])
