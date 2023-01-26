# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

{
	'name': "Multi Codigos de barras",

	'summary': """
		Multi Codigos de barras""",

	'description': """
		Multi Codigos de barras, asigna una unidad de medida y precio por cada codigo de barra
	""",

	'author': "F & M Solutions Service S.A.C",
	'website': "http://www.solse.pe",
	'category': 'Operations',
	'version': '16.0.0.2',
	'license': 'Other proprietary',
	'depends': [
		'solse_pe_edi',
		'solse_pe_cpe',
		'point_of_sale',
		'sale_management',
		'pos_sale',
	],
	'data': [
		'security/ir.model.access.csv',
		'views/product_view.xml',
	],
	'assets': {
		'point_of_sale.assets': [
			'solse_multi_barcodes/static/src/js/models.js',
			#'solse_multi_barcodes/static/src/js/ProductScreen.js',
			'solse_multi_barcodes/static/src/js/ProductScreenAleternativo.js',
			'solse_multi_barcodes/static/src/js/pos_scan.js',
		],
	},
	'installable': True,
	'price': 150,
	'currency': 'USD',
}