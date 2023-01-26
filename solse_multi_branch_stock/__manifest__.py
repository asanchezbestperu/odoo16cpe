# -*- coding: utf-8 -*-
# Copyright (c) 2021 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
{
	'name': "Multi Sucursal Stock",

	'summary': """
		Multi Sucursal Stock
		""",

	'description': """
		Multi Sucursal Stock
	""",

	'author': "F & M Solutions Service S.A.C",
	'website': "https://www.solse.pe",

	'category': 'Uncategorized',
	'version': '15.0.1.1',
	'depends': ['solse_multi_branch', 'stock'],
	'data': [
		'security/security.xml',
		'views/stock_view.xml',
		#'views/sale_order_view.xml',
	],
	'demo': [],
	'installable': True,
	'auto_install': False,
	'application': True,
	"sequence": 1,
}