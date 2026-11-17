from openpyxl import load_workbook


def get_chat_names(file_path):
    workbook = load_workbook(file_path, read_only=True, data_only=True)
    sheet = workbook["15 региональных"]

    chat_names = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        name = row[3]

        if name and str(name).strip():
            chat_names.append(str(name).strip())

    workbook.close()

    return list(dict.fromkeys(chat_names))