from openpyxl import load_workbook
from openpyxl import utils
from datetime import datetime
from tabulate import tabulate

class SpreadsheetParser():
    def __init__(self, grade):
        self.book_name = "schedule1.xlsx"
        self.weekdays = {
            "Понедельник" : 0,
            "Вторник" : 1,
            "Среда" : 2,
            "Четверг" : 3,
            "Пятница" : 4
        }
        self.weekday = datetime.today().weekday()+1
        if self.weekday in [5, 6, 7]:
            self.weekday = 0
        self.grade = grade

    def process_sheet(self, filename):
        wb = load_workbook(filename=filename, read_only=False)
        ws = wb.active
        for row in ws['A134':'BJ182']:
            for cell in row:
                if len(str(cell.value)) > 60:
                    large_text = str(cell.value)
                    i = cell.row + 1
                    mergecell = type(ws[cell.row+1][cell.column-1])
                    while type(ws[i + 1][cell.column-1]) == mergecell:
                        i += 1
                    if type(ws[i][cell.column]) == mergecell:
                        last_cell = ws[i][cell.column]
                    else:

                        last_cell = ws[i][cell.column-1]
                    start_cell = cell
                    try:
                        ws.unmerge_cells(start_row=start_cell.row, start_column=start_cell.column, end_row=last_cell.row, end_column=last_cell.column)
                    except ValueError:
                        last_cell = ws[i][cell.column-1]
                        ws.unmerge_cells(start_row=start_cell.row, start_column=start_cell.column, end_row=last_cell.row, end_column=last_cell.column)
                    i = start_cell.row
                    while i <= last_cell.row:
                        ws[i][start_cell.column-1].value = large_text
                        ws.merge_cells(start_row=i, start_column=start_cell.column, end_row=i+3, end_column=last_cell.column)
                        i+=4
                    #thestr = cell.value
                    #ws.merge_cells(start_row=cell.row, start_column=cell.column, end_row=cell.row+3, end_column=cell.column+1)
                    #ws.merge_cells(start_row=cell.row+4, start_column=cell.column, end_row=cell.row+7, end_column=cell.column+1)

        wb.save(filename)

    def parse_sheet(self, weekday, grade):
        wb = load_workbook(filename='spreadsheets\\'+self.book_name, read_only=True)
        ws = wb.active
        final_ans = ""
        for cell in ws[3]:
            if cell.value is not None and self.weekdays[str(cell.value)] == weekday:
                final_ans += f"Расписание для класса {grade} на день: {str(cell.value)}\n"
                col_bounds = cell.column_letter, ws[3][cell.column + 10].column_letter
                break
        for row in ws:
            if str(row[0].value).startswith(grade):
                row_bounds = (row[0].row, row[0].row+3)
        data_rows = []
        bad_strings = ['']
        std_bad_strings = ['']
        for row in ws[col_bounds[0]+str(row_bounds[0]):col_bounds[1]+str(row_bounds[1])]:
            data_cols = []
            for cell in row:
                if len(str(cell.value)) > 60:
                    if cell.value.startswith("Стандарт"):
                        std_bad_strings.append(cell.value)
                        data_cols.append("Стандарт")
                    else:
                        bad_strings.append(f'Профили{len(bad_strings)}: {cell.value}')
                        data_cols.append(f'Профили{len(bad_strings) - 1}')
                    continue
                data_cols.append(cell.value)
            data_rows.append(data_cols)
        for i in reversed(range(len(data_cols))):
            isRowEmpty = 0
            for j in range(len(data_rows)):
                if data_rows[j][i] is not None:
                    isRowEmpty = 1
            if isRowEmpty == 0:
                for j in range(len(data_rows)):
                    del data_rows[j][i]
        arr_cnt = len(data_rows[0])
        for i in range(arr_cnt):
            copy_data_rows = []
            copy_data_rows.append([f'{i+1} Урок'])
            for j in range(len(data_rows)):
                if data_rows[j][i] is None:
                    continue
                if len(data_rows[j][i]) > 30:
                    names = data_rows[j][i].split(',')
                    copy_data_rows.append([names[0]])
                    copy_data_rows.append([names[1]])
                    continue
                copy_data_rows.append([data_rows[j][i]])
            final_ans += tabulate(copy_data_rows, headers='firstrow', tablefmt='grid') + '\n'
        #final_ans += tabulate(data_rows)
        final_ans += '\n'.join(std_bad_strings)
        final_ans += '\n'.join(bad_strings)
        return final_ans

    @property
    def sheet(self):
        return self.parse_sheet(self.weekday, self.grade)#self.weekday, self.grade)


if __name__ == '__main__':
    sp = SpreadsheetParser("11E")
    print(sp.sheet)
    #sp.process_sheet('spreadsheets\\schedule1.xlsx')
