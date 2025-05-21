# -*- coding: utf-8 -*-
from datetime import timedelta
from email.policy import default

from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.fields import Datetime
from odoo import fields, models, api, _


class StudentInformation(models.Model):
    """This class contains student information Model"""
    _name = 'student.information'
    _description = 'Student information'
    _inherit = 'mail.thread'

    student_no = fields.Char('Student Id', readonly=True, tracking=True, copy=False, default="New")
    name = fields.Char(string='Name')
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street 2')
    city = fields.Char(string='City')
    state_id = fields.Many2one("res.country.state", string='State',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country')
    zip = fields.Char('Zip')
    date_of_birth = fields.Date('DOB')
    age = fields.Integer('Age')
    room_id = fields.Many2one(comodel_name='room.management', string='Room', readonly=True, copy=False)
    email = fields.Char('Email')
    image = fields.Binary('Image')
    receive_mail = fields.Boolean('Receive Mail')
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner', string='Partner', copy=False)
    leave_ids = fields.One2many('leave.request', string='allocated_students', inverse_name='student_id')
    invoice_count = fields.Integer(string='Invoice', compute='_compute_invoice_count', default=0)
    active = fields.Boolean(default=True)
    monthly_amount = fields.Float(string='Monthly Amount', compute='_compute_monthly_amount', default=0)
    invoice_status = fields.Selection([('pending', 'Pending'), ('done', 'Done')], string='Invoice status',
                                      compute='_compute_invoice_status', store=True)
    pending_amount = fields.Float(string='Pending Amount', compute='_compute_pending_amount', store=True, default=0)
    user_id = fields.Many2one('res.users', 'User')

    @api.depends('invoice_count')
    def _compute_invoice_count(self):
        """This function calculates invoice count"""
        for record in self:
            record.invoice_count = record.env['account.move'].search_count(
                [('student_id', '=', record.id)])

    @api.depends('monthly_amount')
    def _compute_monthly_amount(self):
        """This function calculates monthly invoice amount"""
        for record in self:
            record.monthly_amount = record.room_id.total_rent

    @api.depends('invoice_status')
    def _compute_invoice_status(self):
        """This function calculates invoice status of the student"""
        for record in self:
            invoice_status = record.env['account.move'].search(
                [('student_id', '=', record.id), ('payment_state', '!=', 'paid')], limit=1)
            record.write({'invoice_status': 'pending'})
            if not invoice_status:
                record.write({'invoice_status': 'done'})

    @api.depends('pending_amount')
    def _compute_pending_amount(self):
        """This Function calculates pending amount of students """
        for record in self:
            pending_invoices = record.env['account.move'].search(
                [('student_id.id', '=', record.id), ('payment_state', '!=', 'paid')]).mapped(
                'amount_total')
            student_pending_amount = 0
            for pending_invoice in pending_invoices:
                student_pending_amount += pending_invoice
            record.pending_amount = student_pending_amount

    @api.onchange('date_of_birth')
    def _onchange_date_of_birth(self):
        """This Function calculates age of the student """
        if self.date_of_birth and self.date_of_birth <= fields.Date.today():
            self.update({
                "age": relativedelta(fields.Date.from_string(fields.date.today()),
                                     fields.Date.from_string(self.date_of_birth)).years
            })
        else:
            self.age = False

    @api.model_create_multi
    def create(self, vals_list):
        """This function creates student no and also stores data to create a contact in res.partner"""
        for vals in vals_list:
            if vals.get('student_no', _('New')) == _('New'):
                vals['student_no'] = (self.env['ir.sequence'].next_by_code('student.information'))
                partner = self.env['res.partner'].create([{
                    'name': vals.get('name'),
                    'email': vals.get('email'),
                    'street': vals.get('street'),
                    'street2': vals.get('street2'),
                    'city': vals.get('city'),
                    'state_id': vals.get('state_id'),
                    'zip': vals.get('zip'),
                    'country_id': vals.get('country_id')
                }])
                vals['partner_id'] = partner.id
        return super().create(vals_list)

    def unlink(self):
        """This function delete the students records and their corresponding leave records"""
        # self.env['leave.request'].search([('student_id', 'in', self.ids)]).unlink()
        return super(StudentInformation, self).unlink()

    def action_alot_room(self):
        """This Function allocate rooms for students"""
        self.active = True
        available_room = self.env['room.management'].search([('state', '=', 'partial')], limit=1)
        if not available_room:
            available_room = self.env['room.management'].search([('state', '=', 'empty')], limit=1)
        if not available_room:
            raise UserError('Sorry! There is no Room available')
        student_count = self.env['student.information'].search_count([('room_id', '=', available_room.id)])
        if student_count + 1 < available_room.no_of_bed:
            available_room.state = 'partial'
        elif student_count + 1 == available_room.no_of_bed:
            available_room.state = 'full'
        self.write({'room_id': available_room})

    def action_vacate(self):
        """this function delocate the students in the room"""
        if self.room_id.id:
            selected_room = self.room_id
            self.write({'room_id': None, 'active': False})
            if len(selected_room.student_ids) == 0:
                self.env['cleaning.service'].create([{
                    'room_id': selected_room.id,
                    'start_time': Datetime.now()
                }])
                selected_room.state = 'cleaning'
            elif len(selected_room.student_ids) == selected_room.no_of_bed:
                selected_room.state = 'full'
            else:
                selected_room.state = 'partial'

    def action_get_invoice_record(self):
        """This function show invoices of the students"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'domain': [
                ('student_id', '=', self.id),
                ('invoice_date_due', '=', fields.Datetime.today().replace(day=1) + relativedelta(months=+1)),
                ('line_ids.product_id', '=', self.env.ref('hostel_management.product_product_rent').id)
            ],
            'context': "{'create': False}"
        }

    def automated_user(self):
        """This function create the user by automated action"""
        user = self.env['res.users'].create([{
            'name': self.name,
            'login': self.email,
            'partner_id': self.partner_id.id
        }])
        self.user_id = user.id
