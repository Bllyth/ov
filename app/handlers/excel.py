# import time
# from string import ascii_uppercase
# from openpyxl import Workbook
# from openpyxl.styles import Font, Border, Alignment, Side, PatternFill
# from openpyxl.drawing.image import Image
# from config import Config
# from datetime import datetime
#
#
# # DEFAULTS = {
# #   "has_header": True,
# #   "freeze_header": True,
# #   "col_width_fit_param_keys": True,
# #   "col_width_fit_ids": True,
# #   "minimum_col_width": 20,
# #   "maximum_row_height": 100,
# #   "wrap_text": True,
# #   "align_top": True,
# #   "bool_as_string": False,
# #   "merge_hidden_tables": True,
# #   "reset_height": False
# # }
#
#
# class ExcelReport(object):
#
#     def __init__(self, logo, title, header, records, img, excelName):
#         super(ExcelReport, self).__init__()
#
#         # self.logo = logo
#         self.title = title
#         self.header = header
#         self.records = records
#         # self.img = img
#         self.excelName = excelName
#
#     def Export(self):
#         workbook = Workbook()
#
#         sheet = workbook.active
#         # sheet.add_image(self.logo, 'B4')
#         # sheet.add_image(self.img, 'B14')
#         sheet.title = self.title
#         sheet.sheet_properties.tabColor = "1072BA"
#
#         # View grid lines
#         sheet.sheet_view.showGridLines = False
#
#         endCell = ascii_uppercase[len(self.header)]
#         rangeTitle = "B8:{}9".format(endCell)
#         headerRange = "B12:{}12".format(endCell)
#
#         centerText = Alignment(horizontal="center", vertical="center")
#
#         # =================== TITLE ==================
#
#         sheet.merge_cells(rangeTitle)
#         cellTitle = sheet.cell(row=8, column=2)
#         cellTitle.value = self.title.upper()
#         cellTitle.alignment = centerText
#         cellTitle.font = Font(color="FFFFFF", size=11, bold=True)
#
#         # ==================== EXTRA INFORMATION ====================
#
#         # fontInformationExtra = Font(color="707070", size=11, bold=False)
#
#         # sourceCell = sheet.cell(row=5, column=2)
#         # sourceCell.value = "Generated by: Calvin Muchira"
#         # sourceCell.font = fontInformationExtra
#         #
#         # cellDownloadDate = sheet.cell(row=6, column=2)
#         # cellDownloadDate.value = "Download date: {}".format(datetime.utcnow())
#         # cellDownloadDate.font = fontInformationExtra
#         #
#         # downloadCellQuantity = sheet.cell(row=8, column=2)
#         # downloadCellQuantity.value = "Downloaded records: {}".format(len(self.records))
#         # downloadCellQuantity.font = fontInformationExtra
#
#         # ====================== EDGE - COLOR (CELLS) =======================
#
#         thin = Side(border_style="thin", color="000000")
#         border = Border(top=thin, left=thin, right=thin, bottom=thin)
#         cellColor = PatternFill("solid", fgColor="196F63")
#
#         # ======================= EDGES - COLOR (TITLE) =======================
#
#         rowsTitle = sheet[rangeTitle]
#
#         initialCell = rowsTitle[0][0].row
#         for row in rowsTitle:
#             rowLeft = row[0]
#             rowRight = row[-1]
#             rowLeft.border = rowLeft.border + Border(left=border.left)
#             rowRight.border = rowRight.border + Border(right=border.right)
#
#             for cell in row:
#                 if cell.row == initialCell:
#                     cell.border = cell.border + Border(top=border.top)
#                 else:
#                     cell.border = cell.border + Border(bottom=border.bottom)
#
#                 cell.fill = cellColor
#
#         # =============== DATA - EDGES - COLOR (HEADBOARD - TABLE) =====================
#
#         for index, data in enumerate(self.header, start=2):
#             sheet.cell(row=12, column=index).value = data
#             sheet.cell(row=12, column=index).border = border
#             sheet.cell(row=12, column=index).alignment = centerText
#             sheet.cell(row=12, column=index).font = Font(color="FFFFFF", size=10, bold=True)
#
#         rowsHeader = sheet[headerRange]
#         for row in rowsHeader:
#             for cell in row:
#                 cell.fill = cellColor
#
#         # =============== RECORDS - EDGES - COLOR (RECORDS - TABLE) ===============
#
#         for rowIndex, records in enumerate(self.records, start=13):
#             for columnIndex, record in enumerate(records, start=2):
#                 sheet.cell(row=rowIndex, column=columnIndex).value = record
#                 sheet.cell(row=rowIndex, column=columnIndex).border = border
#                 sheet.cell(row=rowIndex, column=columnIndex).alignment = Alignment(horizontal="left",
#                                                                                    vertical="center")
#                 sheet.cell(row=rowIndex, column=columnIndex).font = Font(color="FF000000", size=10, bold=False)
#
#         # =================== ADJUST WIDTH (CELLS - TABLE) ==========================
#
#         for col in sheet.columns:
#             column = [(column.column_letter, column.value) for column in col
#                       if not column.value is None]
#
#             if column:
#                 maxLength = 0
#                 for cell in column:
#                     if len(str(cell[1])) > maxLength:
#                         maxLength = len(str(cell[1]))
#
#                 # fitWidth = (maxLength + 1) * 1.2
#                 fitWidth = 25
#                 sheet.column_dimensions[str(column[0][0])].width = fitWidth
#
#         #
#         # for r in sheet.rows:
#         #     rowl = [(rowl.row, rowl.value) for rowl in r
#         #             if rowl.value is not None]
#         #     if rowl:
#         #         maxHeight = 0
#         #         for cell in row:
#         #             for v in str(cell.value).split('\n'):
#         #                 # maxHeight += math.ceil(len(v) / col_width[j]) * cell.font.size
#         #                 maxHeight += (maxHeight + 1) * 1.2
#         #             if len(str(cell[1])) > maxHeight:
#         #                 maxHeight = len(str(cell[1]))
#         #
#         #         fitHeight = (maxHeight + 1) * 1.2
#         #         sheet.row_dimensions[row[0][0]].height = fitHeight
#
#         # sheet.merge_cells(imgRange)
#         # cellImg = sheet.cell(row=14, column=14)
#         # cellImg.value = self.img
#         sheet.add_image(self.img, 'B16')
#         # cellTitle.alignment = centerText
#         # cellTitle.font = Font(color="FF000000", size=11, bold=True)
#
#         try:
#             #     # Save the workbook under the given file name
#             workbook.save(Config.EXCEL_FOLDER + "{}.xls".format(self.excelName))
#
#         #     return_message = "Report generated successfully."
#         #
#         except PermissionError:
#             return_message = "Unexpected error: Permission denied"
#         #
#         except:
#             return_message = "Unknown error."
#
#         finally:
#             # Close the workbook
#             workbook.close()
#
#             return "success"
#
#
# def generateExcel(name, email, contact, building, house_number, package, last_payment_date, due_date,
#                   file_name):
#     """ Call the export function which is in the excelReport class
#         We pass the title, header , excel data and xls file name
#     """
#
#     title = name.upper() + " Details"
#     header = ("NAME", "EMAIL", "CONTACT", "BUILDING", "HOUSE NUMBER", "PACKAGE", "LAST PAYMENT DATE", "DUE DATE")
#     # Name, Email, phone_number, building, house_number, package, last_payment_date, due_date,
#
#     records = [(name, email, contact, building, house_number, package, last_payment_date, due_date)]
#
#     # img = Image(Config.RAPID_ID_FOLDER + id_photo)
#     # logo = Image(Config.RAPID_ASSETS_FOLDER + 'images/rapid-logo.png')
#     # logo.width = 200
#     # logo.height = 50
#
#     excelName = file_name
#
#     report = ExcelReport(title, header, records, excelName).Export()
#
#     print(report)
