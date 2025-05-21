# -*- coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo import fields, models, api


class HostelFacility(models.Model):
    """This class contains hostel_facility Model"""
    _name = 'hostel.facility'
    _rec_name = 'facility_name'
    _description = 'Hostel Facility'

    facility_name = fields.Char('Name')
    charge = fields.Float('Charge')

    @api.constrains('charge')
    def _check_charge(self):
        """This Function check if there is any user error in charge field """
        if self.charge < 1:
            raise UserError('Field value cannot be 0 or negative!')
