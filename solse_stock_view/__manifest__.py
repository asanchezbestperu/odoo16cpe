# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

{
	'name': "Stock Productos",

	'summary': """
		Módulo para ver resumen stock""",

	'description': """
		Módulo para ver resumen stock
	""",

	'author': "F & M Solutions Service S.A.C",
	'website': "http://www.solse.pe",

	'category': 'Uncategorized',
	'version': '16.0.0.2',
	'license': 'Other proprietary',
	'depends': [
		'sale_management',
		'stock',
	],
	'data': [
		'security/ir.model.access.csv',
		'data/tareas_programadas.xml',
		'views/stock_view.xml',
	],
	'auto_install': False,
	'installable': True,
	'web_preload': True,
	'application': True,
	"sequence": 1,
}