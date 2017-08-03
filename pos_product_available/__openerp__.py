# -*- coding: utf-8 -*-
{
    'name': 'Available quantity of products in POS:Nivas',
    'version': '1.0.3',
    'author': 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'LGPL-3',
    'category': 'Point Of Sale',
    'website': 'https://twitter.com/yelizariev',
    'depends': ['point_of_sale', 'stock'],
    'data': [
        'data.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
        'static/src/xml/pos_report.xml',
    ],
    'installable': True,
}
