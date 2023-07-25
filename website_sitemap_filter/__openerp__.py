# -*- coding: utf-8 -*-

{
    'name': 'Website Sitemap Filter',
	'summary': 'Remove unwanted URL from sitemap.xml',
    'version': '9.0.1.0.0',
    'author': 'DarbTech',
	'website': 'https://darbtech.net',
	'support': 'support@darbtech.net',
	'price': 0.00,
    'currency': 'EUR',
    'license': 'AGPL-3',
    'category': 'website',
    'depends': ['website'],
    "description": """
        Website SiteMap serve as the directory for pages of a web site accessible to users.
        This plug-in allow you to filter sitemap entries.
    """,
    'data': [
        'views/res_config.xml',
    ],
    'images': ['static/website_sitemap_filter.png'],
    'qweb': [],
    'installable': True,
    'auto_install': False,
}
