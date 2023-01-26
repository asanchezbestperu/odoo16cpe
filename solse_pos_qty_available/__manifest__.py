# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

{
	'name': "Stock Productos en POS",

	'summary': """
		Módulo para ver stock de productos en POS""",

	'description': """
		Módulo para ver stock de productos en POS
	""",

	'author': "F & M Solutions Service S.A.C",
	'website': "http://www.solse.pe",

	'category': 'Point of Sale',
	'version': '16.0.0.1',
	'license': 'Other proprietary',
	'depends': [
		'sale_management',
		'stock',
		'point_of_sale',
	],
	'data': [],
	'assets': {
		'point_of_sale.assets': [
			'solse_pos_qty_available/static/src/css/qty_available.css',
			'solse_pos_qty_available/static/src/js/ProductsWidget.js',
			'solse_pos_qty_available/static/src/xml/**/*',
		],
	},
	'auto_install': False,
	'installable': True,
	'web_preload': True,
	'application': True,
	"sequence": 1,
}