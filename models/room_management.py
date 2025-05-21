# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.fields import Datetime
from odoo import fields, models, api, _, Command


class RoomManagement(models.Model):
    """This class contains room_management Model"""
    _name = 'room.management'
    _rec_name = 'room_no'
    _inherit = 'mail.thread'
    _description = 'Room Management'

    room_no = fields.Char('Room Number', readonly=True, tracking=True, copy=False, default="New")
    room_type = fields.Selection(
        [('ac', 'Ac'), ('non_ac', 'Non Ac')], 'Room Type', required=True, tracking=True
    )
    no_of_bed = fields.Integer('Number of bed', copy=False, default=1)
    image = fields.Binary('Image')
    rent = fields.Float('Rent')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id)
    state = fields.Selection(
        [('empty', 'Empty'), ('partial', 'Partial'), ('full', 'Full'), ('cleaning', 'Cleaning')], 'Status',
        default='empty',
        copy=False, required=True, tracking=True, compute='_compute_state', store=True
    )
    company_id = fields.Many2one('res.company', string='Company', index=True)
    facility_ids = fields.Many2many('hostel.facility', string='Facility')
    student_ids = fields.One2many('student.information', string='Allocated students', inverse_name='room_id')
    total_rent = fields.Float('Total rent', compute='_compute_total_rent')
    pending_amount = fields.Float('Pending amount', compute='_compute_pending_amount', readonly=True)

    @api.depends('rent', 'facility_ids.charge')
    def _compute_total_rent(self):
        """This function calculate total rent amount"""
        for record in self:
            record.total_rent = sum(record.facility_ids.mapped('charge')) + record.rent

    @api.depends('pending_amount')
    def _compute_pending_amount(self):
        """Compute the pending amount"""
        for record in self:
            if record.student_ids:
                record.pending_amount = sum(record.env['account.move'].search(
                    [('student_id', 'in', record.student_ids.ids), ('payment_state', '!=', 'paid')]).mapped(
                    'amount_total'))
            else:
                record.pending_amount = 0
    @api.depends('state','student_ids')
    def _compute_state(self):
        """This function calculate total rent amount"""
        for record in self:
            if len(record.student_ids) == 0:
                record.state = 'empty'
            elif len(record.student_ids) == record.no_of_bed:
                record.state = 'full'
            else:
                record.state = 'partial'

    @api.model_create_multi
    def create(self, vals_list):
        """This function creates room no"""
        for vals in vals_list:
            if vals.get('room_no', _('New')) == _('New'):
                vals['room_no'] = (self.env['ir.sequence'].next_by_code('room.management'))
        return super().create(vals_list)

    def action_monthly_invoice(self):
        """This function create invoice for the rent and also handle the error exceptions"""
        total_rent = self.total_rent
        invoice_date_due = Datetime.today().replace(day=1) + relativedelta(months=+1)
        if self.student_ids:
            created_invoice = 0
            existing_invoice = self.env['account.move'].search([
                ('student_id', 'in', self.student_ids.ids),
                ('invoice_date_due', '=', invoice_date_due),
            ])
            for record in self.student_ids:
                if record.id in existing_invoice.student_id.ids:
                    created_invoice += 1
                    if created_invoice == len(self.student_ids):
                        raise UserError('Sorry, This month invoice has already initiated')
                    continue
                # Create the invoice only once per student
                invoice = {
                    'move_type': 'out_invoice',
                    'partner_id': record.partner_id.id,
                    'student_id': record.id,
                    'invoice_date': Datetime.today().replace(day=1),
                    'invoice_date_due': invoice_date_due,
                    'invoice_line_ids': [
                        Command.create({
                            'product_id': record.env.ref('hostel_management.product_product_rent').id,
                            'quantity': 1,
                            'price_unit': total_rent,
                            'tax_ids': False,
                        })
                    ],
                }
                record.env['account.move'].create(invoice)
            room_invoice = self.env['account.move'].search([
                ('student_id', 'in', self.student_ids.ids),
                ('invoice_date_due', '=', invoice_date_due),
            ], limit=1)
            if room_invoice:
                return {
                    'name': _('Create invoice/bill'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form' if len(self.student_ids) == 1 else 'list,form',
                    'domain': [
                        ('student_id', 'in', self.student_ids.ids),
                        ('invoice_date_due', '=', invoice_date_due),
                        ('line_ids.product_id', '=', self.env.ref('hostel_management.product_product_rent').id)
                    ],
                    'res_model': 'account.move',
                    'res_id': room_invoice.id
                }

    def _cron_create_invoice(self):
        """This function create automatic invoices and send mail for students at the first of every month"""
        students = self.env['room.management'].search([]).mapped('student_ids')
        invoice_date_due = Datetime.today().replace(day=1) + relativedelta(months=+1)
        if students:
            existing_invoice = self.env['account.move'].search([
                ('student_id', 'in', students.ids),
                ('invoice_date_due', '=', invoice_date_due),
            ])
            for student in students:
                if student.id in existing_invoice.student_id.ids:
                    continue
                # Create the invoice only once per student
                invoice = {
                    'move_type': 'out_invoice',
                    'partner_id': student.partner_id.id,
                    'student_id': student.id,
                    'invoice_date': Datetime.today().replace(day=1),
                    'invoice_date_due': invoice_date_due,
                    'invoice_line_ids': [
                        Command.create({
                            'product_id': student.env.ref('hostel_management.product_product_rent').id,
                            'quantity': 1,
                            'price_unit': student.room_id.total_rent,
                            'tax_ids': False,
                        })
                    ],
                }
                student.env['account.move'].create(invoice)
                if student.receive_mail:
                    email_values = {'email_to': student.email}
                    mail_template = student.env.ref('hostel_management.monthly_email_template')
                    mail_template.send_mail(self.id, email_values=email_values, force_send=True)
