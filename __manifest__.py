{
    'name': 'Notify & Cancel Expired Quotations',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Notify to the clients their expired quotations and cancel them automatically',
    'sequence': 10,
    'author': 'Frainer Encarnación',
    'maintainer': 'fraineralex2001@gmail.com',
    'website': 'https://fraineralex.dev',
    'depends': ['sale'],
    'data': [
        'data/ir_cron.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
