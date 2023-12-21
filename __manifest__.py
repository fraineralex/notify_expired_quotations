{
    'name': 'Notify & Cancel Expired Quotations',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Notify to the clients their expired quotations and cancel them automatically',
    'sequence': 10,
    'author': 'Lifter',
    'maintainer': 'Frainer Encarnación',
    'website': 'lifterdo.com',
    'depends': ['sale'],
    'data': [
        'data/ir_cron.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
