
{
    'name': "Payment Provider: Thawani",
    'author': "Al-Kitani",
    'version': '1.0',
    'category': 'Accounting/Payment Providers',
    'sequence': 350,
    'summary': "An application that adds support for Thawani payment gateway to Odoo. More information can be found in https://github.com/kitaniman/thawani-odoo-app/tree/main/payment_thawani_gateway",
    'description': "An application that adds support for Thawani payment gateway to Odoo. More information can be found in https://github.com/kitaniman/thawani-odoo-app/tree/main/payment_thawani_gateway",
    'depends': ['payment'],
    'data': [
        'views/payment_thawani_templates.xml',
        'views/payment_provider_views.xml',

        'data/payment_provider_data.xml'
    ],
    'images': [
        'static/description/banner.jpg'
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
}
