{
    'name': 'sid_sale_order_amount_control',
    'version': '1.0',
    'category': 'Sales',
    'license': 'AGPL-3',
    'summary': 'Control de Base Imponible',
    'description': 'Campos para ver cantidades facturadas, pendiente de entrega o de factura',
    'author': 'oscarsidsa81',
    'depends': ['base','sale_management'],
    'data': [
        'views/sid_sale_order_amount_control.xml'
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}