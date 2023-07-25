# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'translations',
    'version': '1.0',
    'author': 'Serg Terihov',
    'summary': 'Depends and translations',
    'sequence': 30,
    'description': """
Kezem depends and translations
====================
Translated modules:
#	* account_cancel
#	* rating
#	* account_extra_reports
#	* web
#	* web_tip
#	* analytic
#	* website_sale
#	* sale_expense
#	* board
#	* mail
#	* marketing_campaign
#	* sale_stock
#	* hr_expense
#	* base_import
#	* theme_default
#	* web_view_editor
#	* crm_partner_assign
#	* website_livechat
#	* report
#	* hr_payroll_account
#	* sale_order_dates
#	* website_mail
#	* resource
#	* website_hr
#	* survey_crm
#	* hr_recruitment
#	* sale_crm
#	* crm
#	* fetchmail
#	* project_timesheet
#	* point_of_sale
#	* base_import_module
#	* calendar
#	* google_account
#	* website_partner
#	* website_theme_install
#	* website_slides
#	* web_editor
#	* web_settings_dashboard
#	* marketing
#	* im_livechat
#	* portal_sale
#	* account_test
#	* account_analytic_default
#	* sale_service
#	* link_tracker
#	* payment_transfer
#	* base
#	* website_google_map
#	* decimal_precision
#	* membership
#	* survey
#	* website_portal_sale
#	* website_portal
#	* rating_project
#	* procurement_jit
#	* account_bank_statement_import
#	* website_twitter
#	* website_links
#	* google_calendar
#	* sale_timesheet
#	* website_customer
#	* website_form
#	* product_expiry
#	* product_uos
#	* base_action_rule
#	* barcodes
#	* website_crm_claim
#	* base_geolocalize
#	* website_crm
#	* website
#	* hr
#	* bus
#	* hr_timesheet
#	* web_kanban_gauge
#	* im_odoo_support
#	* account
#	* web_diagram
#	* rating_project_issue
#	* web_kanban
#	* utm
#	* project
#	* hr_holidays
#	* auth_signup
#	* hr_contract
#	* account_asset
#	* warning
#	* claim_from_delivery
#	* crm_claim
#	* hr_payroll
#	* website_crm_partner_assign
#	* base_setup
#	* procurement
#	* website_project_issue
#	* website_hr_recruitment
#	* account_tax_cash_basis
#	* pad
#	* website_blog
#	* document
#	* stock
#	* product
#	* website_payment
#	* hr_attendance
#	* project_issue
#	* web_calendar
#	* account_tax_python
#	* portal
#	* payment
#	* purchase
#	* website_sale_stock
#	* web_planner
#	* sale
#	* hr_timesheet_sheet
#	* sales_team
#	* stock_account
# Import translate terms after installation by settigs menu.
# Select:
# Name: Russian / русский язык
# Code: ru_RU
# File: ru.po from i18n folder of module.
    """,
    'category': 'Localization',
    'website': 'https://www.odoo.com',
    'images' : [],
    'depends' : ['account_cancel',
        'project_kanban',
        'account_extra_reports',
        'project_team',
        'courier_tasks',
        'web',
        'web_tip',
        'analytic',
        'account_bank_statement_import_1c',
        'sale_expense',
        'board',
        'hr_public_holidays',
        'mail',
        'marketing_campaign',
        'sale_stock',
        'auth_totp',
        'auto_backup',
        'base_import',
        'theme_default',
        'web_view_editor',
        'crm_partner_assign',
        'l10n_ru_doc',
        'website_sitemap_filter',
        'website_livechat',
        'mail_base',
        'report',
        'hr_payroll_account',
        'sale_order_dates',
        'website_mail',
        'resource',
        'website_hr',
        'survey_crm',
        'hr_recruitment',
        'payment_transfer',
        'web_widget_many2many_tags_multi_selection',
        'crm',
        'rating',
        'fetchmail',
        'project_timesheet',
        'database_cleanup',
        'web_export_xls',
        'point_of_sale',
        'base_import_module',
        'calendar',
        'google_account',
        'mass_editing',
        'sale_contract',
        'website_theme_install',
        'website_slides',
        'web_editor',
        'web_settings_dashboard',
        'sale_service',
        'im_livechat',
        'portal_sale',
        'account_test',
        'account_analytic_default',
        'marketing',
        'link_tracker',
        'hr_expense',
        'hr_expense_ru_mod',
        'sale_crm',
        'base',
        'hr_holidays_compute_days',
        'decimal_precision',
        'membership',
        'website_google_map',
        'survey',
        'website_portal_sale',
        'website_crm',
        'website_portal',
        'rating_project',
        'procurement_jit',
        'account_bank_statement_import',
        'website_twitter',
        'website_links',
        'google_calendar',
        'sale_timesheet',
        'website_customer',
        'website_form',
        'product_expiry',
        'product_uos',
        'base_action_rule',
        'barcodes',
        'website_crm_claim',
        'base_geolocalize',
        'auth_crypt',
        'website_sale',
        'web_debranding',
        'sale_kits',
        'website',
        'hr',
        'bus',
        'hr_timesheet',
        'web_kanban_gauge',
        'im_odoo_support',
        'account',
        'web_diagram',
        'rating_project_issue',
        'web_kanban',
        'utm',
        'project',
        'hr_holidays',
        'partner_snils',
        'auth_signup',
        'hr_contract',
        'sale_bank_account',
        'access_apps',
        'access_restricted',
        'sale',
        'warning',
        'claim_from_delivery',
        'crm_claim',
        'hr_payroll',
        'website_crm_partner_assign',
        'base_setup',
        'hr_timesheet_sheet',
        'website_project_issue',
        'website_hr_recruitment',
        'account_tax_cash_basis',
        'pad',
        'website_blog',
        'sale_contract_fields',
        'document',
        'stock',
        'product',
        'website_payment',
        'access_settings_menu',
        'hr_attendance',
        'project_issue',
        'project_task_default_stage',
        'web_calendar',
        'account_tax_python',
        'portal',
        'ir_rule_protected',
        'payment',
        'purchase',
        'website_sale_stock',
        'auth_brute_force',
        'web_planner',
        'website_partner',
        'account_asset',
        'procurement',
        'sales_team',
        'stock_account',
        'account_extra_reports_rm',
        'account_ru_mod',
        'hr_expense_rm'],
    'data': [],
    'demo': [],
    'qweb': [],
    'installable': True,
    'auto_install': False,
}
