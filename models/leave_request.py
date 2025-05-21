# -*- coding: utf-8 -*-
from datetime import timedelta
from email.policy import default

from odoo.exceptions import UserError
from odoo.fields import Datetime
from odoo import models, fields, api, _


class LeaveRequest(models.Model):
    """This class is used to create leave_request Model"""
    _name = 'leave.request'
    _description = 'Leave Description'
    _rec_name = 'student_id'

    start_date = fields.Date('Leave Date', required=True)
    arrival_date = fields.Date('Arrival Date', required=True)
    status = fields.Selection(selection=[
        ('new', 'New'), ('approved', 'Approved')
    ])
    student_id = fields.Many2one(
        'student.information', string='Student', required=True, ondelete='cascade')
    company_id = fields.Many2one(
        'res.company', 'Company', related='student_id.company_id', readonly=True)
    leave_duration = fields.Float(string='Leave Duration', compute='_compute_leave_duration', store=True, default=0)

    @api.constrains('arrival_date')
    def _check_arrival_date(self):
        start_date = self.start_date.strftime('%Y-%m-%d')
        arrival_date = self.arrival_date.strftime('%Y-%m-%d')
        if start_date > arrival_date:
            raise UserError("Sorry, Please enter a valid date")

    @api.depends('leave_duration','start_date','arrival_date')
    def _compute_leave_duration(self):
        """This Function calculates leave duration of students """
        for record in self:
            if record.start_date and record.arrival_date:
                start_date = record.start_date
                end_date = record.arrival_date
                delta = timedelta(days=1)
                count = 0
                while start_date <= end_date:
                    start_date += delta
                    if not start_date.weekday() in [5, 6]: count += 1
                record.leave_duration = count

    def action_approve(self):
        """This Function change the status into approve"""
        self.write({'status': "approved"})
        if len(self.student_id.room_id.student_ids) - 1 == 0:
            self.env['cleaning.service'].create([{
                'room_id': self.student_id.room_id.id,
                'start_time': Datetime.now()
            }])
            self.student_id.room_id.state = 'cleaning'

    def action_new(self):
        """This Function change the status into approve"""
        self.write({'status': "new"})