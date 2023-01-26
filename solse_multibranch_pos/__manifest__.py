# -*- coding: utf-8 -*-
{
	'name': "Multi Sucursal POS",

	'summary': """
		Multi Sucursal POS
		""",

	'description': """
		Multi Sucursal POS
	""",

	'author': "F & M Solutions Service S.A.C",
	'website': "https://www.solse.pe",

	'category': 'Uncategorized',
	'version': '16.0.0.3',
	'depends': ['base', 'solse_pe_edi', 'solse_pe_cpe', 'solse_pe_cpe_pos', 'solse_multi_branch','solse_pe_pos_report'],
	'data': [
		'security/security.xml',
		'views/res_branch_view.xml',
		'views/pos_config_view.xml',
	],
	'assets': {
		'point_of_sale.assets': [
			'solse_multibranch_pos/static/src/js/screen.js',
			'solse_multibranch_pos/static/src/js/TicketScreen.js',
			#'solse_multibranch_pos/static/src/xml/pos_report.xml',
		],
	},
	'demo': [],
	'installable': True,
	'auto_install': False,
	'application': True,
	"sequence": 1,
}