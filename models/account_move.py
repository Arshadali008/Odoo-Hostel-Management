# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountMove(models.Model):
    """This class inherit account.move model"""
    _inherit = 'account.move'

    student_id = fields.Many2one('student.information', 'Student')

    def action_post(self):
        # inherit of the function from account.move to validate an email and while the state changed to posted
        res = super(AccountMove, self).action_post()
        if self.student_id.receive_mail:
            mail_template = self.env.ref('hostel_management.posted_email_template')
            mail_template.send_mail(self.id, force_send=True)
        return res
