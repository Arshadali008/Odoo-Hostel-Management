# -*- coding: utf-8 -*-
from odoo.http import request, Controller, route

class WebFormController(Controller):
    @route('/webform', auth='public', website=True)
    def web_form(self, **kwargs):
        rooms = request.env['room.management'].search([])
        return request.render('hostel_management.web_form_template', {
            'rooms': rooms.filtered(lambda r: r.state == 'partial' or r.state == 'empty')
        })

    @route('/webform/submit', type='http', auth='public', website=True, methods=['POST'])
    def web_form_submit(self, **post):
        user_emails = request.env['res.users'].search([('login', '=', post.get('email'))])
        rooms = request.env['room.management'].search([])
        if user_emails:
            values = {
                'existing_email': True
            }
            return request.render('hostel_management.web_form_template', {
                'rooms': rooms.filtered(lambda r: r.state == 'partial' or r.state == 'empty')
            }, values)
        else:
            request.env['student.information'].sudo().create({
                'name': post.get('student_name'),
                'date_of_birth': post.get('date_of_birth'),
                'email': post.get('email'),
                'receive_mail': post.get('receive_mail'),
                'room_id': rooms.filtered(lambda r: r.room_no == post.get('room')).id,
            })
            return request.render('hostel_management.web_success_template')
