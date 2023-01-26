# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

{
	'name': "Multi Sucursal",

	'summary': """
		Multi Sucursal
		""",

	'description': """
		Multi Sucursal
	""",

	'author': "F & M Solutions Service S.A.C",
	'website': "https://www.solse.pe",

	'category': 'Uncategorized',
	'version': '16.0.0.2',
	'license': 'Other proprietary',
	'depends': ['base', 'web','sale_management', 'account', 'solse_pe_edi', 'solse_pe_cpe'],
	'data': [
		'data/res_branch_data.xml',
		'security/security.xml',
		'security/ir.model.access.csv',
		'views/res_branch_view.xml',
		'views/sale_view.xml',
		'views/account_view.xml',
		'views/product_view.xml',
		'views/purchase_view.xml',
		'report/sale_report_template.xml',
		'report/report_invoice.xml',
	],
	'assets': {
		'web.assets_backend': [
			'solse_multi_branch/static/src/js/branch_session.js',
			'solse_multi_branch/static/src/scss/branch_menu.scss',
			'solse_multi_branch/static/src/js/branch_service.js',
			'solse_multi_branch/static/src/js/switch_branch_menu.js',
			'solse_multi_branch/static/src/js/switch_company.js',
			'solse_multi_branch/static/src/xml/SwitchBranchMenu.xml',
		],
	},
	'demo': [],
	'installable': True,
	'auto_install': False,
	'application': True,
	"sequence": 1,
}