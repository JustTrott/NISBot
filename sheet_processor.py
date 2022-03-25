from openpyxl import load_workbook
from openpyxl.utils.cell import range_boundaries
from config import Config

class SpreadsheetProcessor():
    def __init__(self, filename : str):
        self.book_name = filename

    def get_grade_letters(self) -> dict[str, str]:
        wb = load_workbook(filename=self.book_name, read_only=True)        
        ws = wb.active
        grades = {}
        for row in ws['A6':'A182']:
            if row[0].value is None:
                continue
            parallel = row[0].value[:-4]
            letter = row[0].value[len(parallel):-3]
            grades[parallel] = grades[parallel] + letter if parallel in grades else letter
        return grades

    def unmerge_and_fill_sheet(self):
        wb = load_workbook(filename=self.book_name, read_only=False)
        ws = wb.active
        mcr_coord_list = [mcr.coord for mcr in ws.merged_cells.ranges]
        for mcr in mcr_coord_list:
            min_col, min_row, max_col, max_row = range_boundaries(mcr)
            if min_col < 3 or min_row < 6:
                continue
            top_left_cell_value = ws.cell(row=min_row, column=min_col).value
            ws.unmerge_cells(mcr)
            for row in ws.iter_rows(min_col=min_col, min_row=min_row, max_col=max_col, max_row=max_row):
                for cell in row:
                    cell.value = top_left_cell_value
        wb.save(self.book_name)
    
if __name__ == '__main__':
    sp = SpreadsheetProcessor('schedule.xlsx')
    sp.unmerge_and_fill_sheet()