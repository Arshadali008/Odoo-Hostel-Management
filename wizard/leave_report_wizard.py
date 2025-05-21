# -*- coding: utf-8 -*-
import json
import io
import xlsxwriter
from odoo.tools import date_utils, json_default
from odoo import fields, models
from odoo.exceptions import UserError


class StudentReportWizard(models.TransientModel):
    _name = 'leave.report.wizard'
    _description = 'Leave Report Wizard'

    student_id = fields.Many2one('student.information', 'Student')
    room_id = fields.Many2one('room.management', 'Room')
    start_date = fields.Date(string='Start Date')
    arrival_date = fields.Date(string='End Date')

    def leave_request_data_fetching(self):
        """This function is used to get data as per condition from table for leave report"""
        query = """SELECT lr.id, lr.start_date, lr.arrival_date, lr.leave_duration,
                si.name as student_name, si.id as student_id, rm.room_no, rm.id as room_id
                FROM leave_request lr JOIN student_information si ON lr.student_id = si.id
                LEFT JOIN room_management rm ON si.room_id = rm.id WHERE 1=1"""
        params = []
        if self.room_id:
            query += """ AND si.room_id = %s"""
            params.append(self.room_id.id)
        if self.student_id:
            query += """ AND lr.student_id = %s"""
            params.append(self.student_id.id)
        if self.start_date:
            query += """ AND lr.start_date >= %s"""
            params.append(self.start_date)
        if self.arrival_date:
            query += """ AND lr.arrival_date <= %s"""
            params.append(self.arrival_date)
        self.env.cr.execute(query, params)
        report = self.env.cr.dictfetchall()
        if not report:
            raise UserError("Sorry there are no data available for selected result")
        data = {'report': report}
        return data

    def action_leave_report_request(self):
        """This function is to retrieve the data and print the PDF  leave report """
        return (self.env.ref('hostel_management.action_leave_report').
                report_action(self, data=self.leave_request_data_fetching()))

    def leave_report_excel(self):
        """This function is to retrieve the data and invoke js for Excel leave report """
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'leave.report.wizard',
                     'options': json.dumps(self.leave_request_data_fetching(), default=json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Leave Excel Report',
                     },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        """This function is to retrieve the data and print the Excel leave report """
        tb_heading_line = 5
        rooms = set()
        for record in data['report']:
            rooms.add(record['room_id'])
        students = set()
        for record in data['report']:
            students.add(record['student_id'])
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        cell_format = workbook.add_format(
            {'font_size': '12px', 'align': 'center', 'bold': True})
        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '20px'})
        txt = workbook.add_format({'font_size': '10px', 'align': 'center'})
        sheet.merge_range('A1:J2', 'LEAVE REPORT', head)
        if len(students) == 1:
            sheet.merge_range('A4:B4', 'Student', cell_format)
            sheet.merge_range('C4:E4', data['report'][0]['student_name'], txt)
        else:
            if len(rooms) == 1: tb_heading_line = 6
            sheet.merge_range(f'A{tb_heading_line}:B{tb_heading_line}', 'Students', cell_format)
        if len(data['report']) == 1:
            sheet.merge_range('A5:B5', 'Room No', cell_format)
            sheet.merge_range(f'C5:E5', data['report'][0]['room_no'], txt)
            sheet.merge_range('A6:B6', 'Start Date', cell_format)
            sheet.merge_range(f'C6:E6', data['report'][0]['start_date'], txt)
            sheet.merge_range('A7:B7', 'Arrival Date', cell_format)
            sheet.merge_range(f'C7:E7', data['report'][0]['arrival_date'], txt)
            sheet.merge_range('A8:B8', 'Leave Duration', cell_format)
            sheet.merge_range(f'C8:E8', data['report'][0]['leave_duration'], txt)
        else:
            letter = 65  # -*- coding: utf-8 -*-
            if len(rooms) == 1:
                single_room_line = 4
                if len(students) == 1:
                    single_room_line = 5
                    tb_heading_line = 7
                sheet.merge_range(f'{chr(letter)}{single_room_line}:{chr(letter + 1)}{single_room_line}', 'Room No',
                                  cell_format)
                sheet.merge_range(f'{chr(letter + 2)}{single_room_line}:{chr(letter + 4)}{single_room_line}',
                                  data['report'][0]['room_no'], txt)
                letter += 2
            else:
                sheet.merge_range(f'{chr(letter + 2)}{tb_heading_line}:{chr(letter + 3)}{tb_heading_line}', 'Room No',
                                  cell_format)
                letter += 4
            if len(rooms) == 1 and len(students) == 1: letter = 65
            sheet.merge_range(f'{chr(letter)}{tb_heading_line}:{chr(letter + 1)}{tb_heading_line}', 'Start Date',
                              cell_format)
            sheet.merge_range(f'{chr(letter + 2)}{tb_heading_line}:{chr(letter + 3)}{tb_heading_line}', 'Arrival Date',
                              cell_format)
            sheet.merge_range(f'{chr(letter + 4)}{tb_heading_line}:{chr(letter + 5)}{tb_heading_line}',
                              'Leave Duration',
                              cell_format)
            for i, leave in enumerate(data['report'], start=tb_heading_line + 1):
                letter = 65
                if not len(students) == 1:
                    sheet.merge_range(f'{chr(letter)}{i}:{chr(letter + 1)}{i}', leave['student_name'], txt)
                    letter += 2
                if not len(rooms) == 1:
                    sheet.merge_range(f'{chr(letter)}{i}:{chr(letter + 1)}{i}', leave['room_no'], txt)
                    letter += 2
                sheet.merge_range(f'{chr(letter)}{i}:{chr(letter + 1)}{i}', leave['start_date'], txt)
                sheet.merge_range(f'{chr(letter + 2)}{i}:{chr(letter + 3)}{i}', leave['arrival_date'], txt)
                sheet.merge_range(f'{chr(letter + 4)}{i}:{chr(letter + 5)}{i}', leave['leave_duration'], txt)
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
