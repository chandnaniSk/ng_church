# -*- coding: utf-8 -*-
{
    'name': 'Church Management',
    'version': '13.0.1.0.1',
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'https://www.serpentcs.com',
    'summary': """
        Church Management""",
    'description': """
Church Management
=================
        """,
    'data': [
            'security/ir.model.access.csv',
            'security/ng_church_security.xml',
            'data/church_pledge_email.xml',
            'data/ng_church_follow_up.xml',
            'data/ng_church_data.xml',
            'data/member_sequence.xml',
            'wizard/ng_church_collections_wizard_view.xml',
            'report/reports.xml',
            'report/print_pledge_report.xml',
            'report/church_pledges_report.xml',
            'report/church_attendance_report.xml',
            'report/church_tithe_report.xml',
            'report/church_offering_report.xml',
            'report/church_donation_report.xml',
            'views/menus.xml',
            'views/actions.xml',
            'views/inherited/account_invoice_view.xml',
            'views/inherited/res_company_view.xml',
            'views/inherited/project.xml',
            'views/ng_church_program.xml',
            'views/ng_church_attendance_view.xml',
            'views/ng_church_church_collections_view.xml',
            'views/membership_view.xml',
            'views/ng_church_pastor_view.xml',
            'views/followup.xml',
            'views/ng_church_lodgement.xml'
    ],
    'depends': [
        'account',
        'event',
        'sale',
        'purchase',
        'crm',
        'project',
    ],
    'category': 'Human Resources',
    'application': True,
    'installable': True,
    'auto_install': False
}
