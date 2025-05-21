# -*- coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo import models, fields


class CleaningService(models.Model):
    _name = 'cleaning.service'
    _rec_name = 'room_id'
    _description = 'Cleaning Service'

    room_id = fields.Many2one('room.management', 'Room', required=True)
    start_time = fields.Datetime('Start time')
    user_id = fields.Many2one('res.users', 'Staff')
    cleaning_state = fields.Selection([
        ('new', 'New'), ('assigned', 'Assigned'), ('done', 'Done')
    ], default='new')
    company_id = fields.Many2one(
        'res.company', 'Company', related='room_id.company_id', readonly=True)

    def action_assign(self):
        """This function change the state and identifies the user"""
        if self.env.user.has_group('hostel_management.hostel_management_group_staff'):
            self.user_id = self.env.user.id
        elif not self.user_id:
            raise UserError('Please choose a staff')
        self.cleaning_state = 'assigned'
        self.room_id.state = 'cleaning'

    def action_complete(self):
        """This action changes the state to complete and change the state of the room"""
        self.write({'cleaning_state': 'done'})
        if len(self.room_id.student_ids) == 0:
            self.room_id.state = 'empty'
        elif len(self.room_id.student_ids) == self.room_id.no_of_bed:
            self.room_id.state = 'full'
        else:
            self.room_id.state = 'partial'
