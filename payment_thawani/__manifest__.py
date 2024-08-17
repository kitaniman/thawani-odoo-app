
{
    'name': "Payment Provider: Thawani",
    'author': "Al-Kitani",
    'version': '1.0',
    'category': 'Accounting/Payment Providers',
    'sequence': 350,
    'summary': "A payment provider based in Oman covering most Omani payment methods.",
    'description': "An application that adds support for Thawani payment gateway to Odoo.",
    'depends': ['payment'],
    'data': [
        'views/payment_thawani_templates.xml',
        'views/payment_provider_views.xml',
        
        'data/payment_provider_data.xml'
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
}
