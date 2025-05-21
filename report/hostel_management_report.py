# -*- coding: utf-8 -*-

from odoo import models, api


class StudentReport(models.AbstractModel):
    _name = 'report.hostel_management.form_student_report'
    _description = 'Student Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['student.report.wizard'].browse(docids)
        rooms = set()
        for record in data['report']:
            rooms.add(record['room_id'])
        data = data['report']
        return {
            'doc_ids': docids,
            'doc_model': 'student.report.wizard',
            'docs': docs,
            'rooms': rooms,
            'data': data,
        }


class LeaveReport(models.AbstractModel):
    _name = 'report.hostel_management.form_leave_report'
    _description = 'Leave Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['leave.report.wizard'].browse(docids)
        rooms = set()
        students = set()
        for record in data['report']:
            rooms.add(record['room_id'])
            students.add(record['student_id'])
        data = data['report']
        return {
            'doc_ids': docids,
            'doc_model': 'leave.report.wizard',
            'docs': docs,
            'students':students,
            'rooms': rooms,
            'data': data,
        }
