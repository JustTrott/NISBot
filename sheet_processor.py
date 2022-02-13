from openpyxl import load_workbook

class SpreadsheetProcessor():
    def __init__(self, filename):
        self.book_name = filename

    def process_sheet(self):
        wb = load_workbook(filename=self.book_name, read_only=False)
        ws = wb.active
        for row in ws['A134':'BJ182']:
            for cell in row:
                if len(str(cell.value)) < 60:
                    continue
                target_content = str(cell.value)
                i = cell.row + 1
                j = cell.column - 1
                mergecell = type(ws[i][j])
                while type(ws[i + 1][j]) == mergecell:
                    i += 1
                if type(ws[i][cell.column]) == mergecell:
                    last_cell = ws[i][j + 1]
                else:
                    last_cell = ws[i][j]
                start_cell = cell
                try:
                    ws.unmerge_cells(f"{start_cell.coordinate}:{last_cell.coordinate}")
                except ValueError:
                    last_cell = ws[i][j]
                    ws.unmerge_cells(f"{start_cell.coordinate}:{last_cell.coordinate}")
                for k in range(start_cell.row, last_cell.row + 1, 4):
                    for l in range(start_cell.column-1, last_cell.column):
                        ws[k][l].value = target_content
                        ws.merge_cells(f"{ws[k][l].coordinate}:{ws[k+3][l].coordinate}")
        for row in ws['C6':'BJ182']:
            for i in range(len(row) - 1):
                if type(row[i+1]) != mergecell:
                    continue
                try:
                    ws.unmerge_cells(f"{row[i].coordinate}:{row[i+1].coordinate}")
                    ws[row[i+1].coordinate].value = row[i].value
                except (ValueError, IndexError):
                    continue
        wb.save(self.book_name)

if __name__ == '__main__':
    sp = SpreadsheetProcessor('schedule.xlsx')
    sp.process_sheet()
