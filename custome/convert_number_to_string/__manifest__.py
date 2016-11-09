{
    'name' : 'Convert Number To String',
    'version' : '1.1',
    'sequence': 30,
    'depends' : ['base_setup', 'product', 'analytic', 'report', 'web_planner'],
    'data': [
        'views/convert_number_to_string_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}