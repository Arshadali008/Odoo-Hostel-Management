# -*- coding: utf-8 -*-
import io
import xlsxwriter
import json
from odoo import fields, models, _
from odoo.exceptions import UserError


class StudentReportWizard(models.TransientModel):
    """This model is used for sending student report through Odoo."""
    _name = 'student.report.wizard'
    _description = "Student report wizard"

    room_id = fields.Many2one('room.management', string="Room")
    student_id = fields.Many2one('student.information', string="Student")

    def student_data_fetching(self):
        """This function is used to get data as per condition from table for student report"""
        query = """SELECT si.id, si.name, si.room_id, si.pending_amount, si.invoice_status, rm.room_no
                FROM student_information si JOIN room_management rm ON si.room_id = rm.id WHERE 1=1"""
        params = []
        if self.room_id:
            query += """ AND si.room_id = %s"""
            params.append(self.room_id.id)
        if self.student_id:
            query += """ AND si.id = %s"""
            params.append(self.student_id.id)
        self.env.cr.execute(query, params)
        report = self.env.cr.dictfetchall()
        if not report:
            raise UserError("Sorry there are no data available for selected result")
        data = {'report': report}
        return data

    def action_student_report_request(self):
        """This function is to retrieve the data and print the PDF student report """
        return self.env.ref('hostel_management.action_student_report').report_action(self,
                                                                                     data=self.student_data_fetching())

    def student_report_excel(self):
        """This function is to retrieve the data and invoke js for Excel student report"""
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'student.report.wizard',
                     'options': json.dumps(self.student_data_fetching()),
                     'output_format': 'xlsx',
                     'report_name': 'Students Excel Report',
                     },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        """This function is to retrieve the data and print the Excel student report"""
        tb_heading_line = 5
        rooms = set()
        for record in data['report']:
            rooms.add(record['room_id'])
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        cell_format = workbook.add_format(
            {'font_size': '12px', 'align': 'center', 'bold': True})
        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '20px'})
        txt = workbook.add_format({'font_size': '10px', 'align': 'center'})
        sheet.merge_range('A1:H2', 'STUDENT REPORT', head)
        if len(data['report']) == 1:
            sheet.merge_range('A4:B4', 'Student:', cell_format)
            sheet.merge_range('C4:E4', data['report'][0]['name'], txt)
        else:
            if len(rooms) == 1: tb_heading_line = 6
            sheet.merge_range(f'A{tb_heading_line}:B{tb_heading_line}', 'Students', cell_format)
        letter = 65
        if len(rooms) == 1:
            single_room_line = 4
            if len(data['report']) == 1:
                tb_heading_line = 7
                single_room_line = 5
            sheet.merge_range(f'{chr(letter)}{single_room_line}:{chr(letter + 1)}{single_room_line}', 'Room NO:',
                              cell_format)
            sheet.merge_range(f'{chr(letter + 2)}{single_room_line}:{chr(letter + 4)}{single_room_line}',
                              data['report'][0]['room_no'], txt)
            letter += 2
        else:
            sheet.merge_range(f'{chr(letter + 2)}{tb_heading_line}:{chr(letter + 3)}{tb_heading_line}', 'Room No',
                              cell_format)
            letter += 4
        if len(data['report']) == 1: letter = 65
        sheet.merge_range(f'{chr(letter)}{tb_heading_line}:{chr(letter + 1)}{tb_heading_line}', 'Pending Amount',
                          cell_format)
        sheet.merge_range(f'{chr(letter + 2)}{tb_heading_line}:{chr(letter + 3)}{tb_heading_line}', 'Invoice Status',
                          cell_format)
        for i, room in enumerate(data['report'], start=tb_heading_line + 1):
            letter = 65
            if not len(data['report']) == 1:
                sheet.merge_range(f'{chr(letter)}{i}:{chr(letter + 1)}{i}', room['name'], txt)
                letter += 2
            if not len(rooms) == 1:
                sheet.merge_range(f'{chr(letter)}{i}:{chr(letter + 1)}{i}', room['room_no'], txt)
                letter += 2
            sheet.merge_range(f'{chr(letter)}{i}:{chr(letter + 1)}{i}', room['pending_amount'], txt)
            sheet.merge_range(f'{chr(letter + 2)}{i}:{chr(letter + 3)}{i}', room['invoice_status'], txt)
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
