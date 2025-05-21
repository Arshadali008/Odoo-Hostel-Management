# -*- coding: utf-8 -*-
{
    'name': "Hostel Management",
    'version': '1.0',
    'depends': ['base', 'mail', 'purchase', 'account', 'website', 'website_sale'],
    'website': "cybrosys:8018/odoo/hostel_management",
    'author': "Alex",
    'category': 'All',
    'description': """
    Description text
    """,
    # data files always loaded at installation
    'data': [
        'data/hostel_management_sequence.xml',
        'data/hostel_facility_record.xml',
        'data/mail_data.xml',
        'data/ir_cron_data.xml',
        'data/user_automated_action.xml',
        'data/hostel_management_web_templates.xml',
        # 'data/hostel_website_cart_buttons.xml',
        'data/product_data.xml',
        'views/hostel_management_snippets.xml',
        'views/hostel_management_views.xml',
        'views/account_move_views.xml',
        'views/room_management_views.xml',
        'views/student_information_views.xml',
        'views/hostel_facility_views.xml',
        'views/leave_request_views.xml',
        'views/hostel_management_search_views.xml',
        'views/cleaning_service_views.xml',
        'views/hostel_management_menu_views.xml',
        'report/hostel_management_reports_views.xml',
        'report/hostel_management_templates.xml',
        'wizard/student_report_wizard_views.xml',
        'wizard/leave_report_wizard_views.xml',
        'security/hostel_management_groups.xml',
        'security/ir_rules.xml',
        'security/ir.model.access.csv',
    ],
    # data files containing optionally loaded demonstration data
    'demo': [
        'demo/demo_data.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'assets': {
        'web.assets_frontend': [
            'hostel_management/static/src/js/hostel_management_snippets.js',
            'hostel_management/static/src/js/website_cart.js',
            'hostel_management/static/src/xml/snippet_templates.xml',
        ],
        'web.assets_backend': [
            'hostel_management/static/src/js/action_manager.js'
        ],
    }
}
