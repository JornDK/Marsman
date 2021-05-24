# -*- coding: utf-8 -*-
{
    'name': 'BQ Core GRC Management',
    'version': '14.0.1.0.0',
    'summary': 'Core GRC management module',
    'price': 99,
    'currency': 'EUR',
    'support':'support@beqome.be',
    'sequence': -120,
    'description': """Manage risks, controls and assets""",
    'category': '',
    'author': 'info@beqome.be',
    'website': 'https://beqome.be',
    'images': [''],
    'depends': ['base', 'mail'],
    'data': [
        'views/grc_menu.xml',
        'views/control_views.xml',
        'views/control_type_views.xml',
        'views/risk_views.xml',
        'views/risk_type_views.xml',
        'views/risk_assessment_views.xml',
        'views/policy_views.xml',
        'views/asset_views.xml',
        'views/asset_type_views.xml',
        'security/ir.model.access.csv',
        'security/grc_risk_user_groups.xml',
        'data/grc.control.type.csv',
        'data/grc.risk.type.csv',
        'data/grc.risk.severity.csv',
        'data/grc.risk.likelihood.csv',
        'data/grc.risk.threat.csv',
        'data/grc.risk.vulnerability.csv',
        'data/grc.asset.type.csv',
        'data/risk_sequence.xml',
        'data/control_sequence.xml',
        'data/policy_sequence.xml',
        'data/asset_sequence.xml'
    ],
    'demo': [
        'demo/risk_demo.xml'
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'Other proprietary'
}
