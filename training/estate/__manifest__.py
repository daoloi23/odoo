# __manifest__.py
{
    'name': 'Real estate',
    'version': '18.0.0.0.0',
    'summary': 'Simple To-Do List Module',
    'author': 'loidd',
    'license' : 'OEEL-1',
    'category': 'Productivity',
    'depends': ['crm'],
    'data': [
        # security
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        #view
        'views/estate_property_view.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_view.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_menus.xml',

    ],
    'demo': [
    'demo/demo.xml'
    ],
    'installable': True,
    'application': True,
}