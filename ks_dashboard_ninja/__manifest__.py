# -*- coding: utf-8 -*-
{
	'name': "Dashboard Ninja",

	'summary': """
		Revamp your Odoo Dashboard like never before! It is one of the best dashboard odoo apps in the market.
	""",

	'description': """
		Dashboard Ninja v16.0,
		Odoo Dashboard,
		Dashboard,
		Dashboards,
		Odoo apps,
		Dashboard app,
		HR Dashboard,
		Sales Dashboard,
		inventory Dashboard,
		Lead Dashboard,
		Opportunity Dashboard,
		CRM Dashboard,
		POS,
		POS Dashboard,
		Connectors,
		Web Dynamic,
		Report Import/Export,
		Date Filter,
		HR,
		Sales,
		Theme,
		Tile Dashboard,
		Dashboard Widgets,
		Dashboard Manager,
		Debranding,
		Customize Dashboard,
		Graph Dashboard,
		Charts Dashboard,
		Invoice Dashboard,
		Project management,
		ksolves,
		ksolves apps,
		Ksolves India Ltd.
		Ksolves India  Limited,
		odoo dashboard apps
		odoo dashboard app
		odoo dashboard module
		odoo modules
		dashboards
		powerful dashboards
		beautiful odoo dashboard
		odoo dynamic dashboard
		all in one dashboard
		multiple dashboard menu
		odoo dashboard portal
		beautiful odoo dashboard
		odoo best dashboard
		dashboard for management
		Odoo custom dashboard
		odoo dashboard management
		odoo dashboard apps
		create odoo dashboard
		odoo dashboard extension
		odoo dashboard module
	""",

	'author': "Ksolves India Ltd.",
	'license': 'OPL-1',
	'currency': 'EUR',
	'price': 363.0,
	'website': "https://www.ksolves.com",
	'maintainer': 'Ksolves India  Limited',
	'live_test_url': 'https://dashboardninja14.kappso.com/web/demo_login',
	'category': 'Tools',
	'version': '16.0.0.0.0',
	'support': 'sales@ksolves.com',
	'images': ['static/description/dasboard_ninja.gif'],

	'depends': ['base', 'web', 'base_setup', 'bus'],

	'assets': {
		'web.assets_qweb': [
			
		],
		'web.assets_backend': [
			"/ks_dashboard_ninja/static/src/xml/ks_widget_toggle.xml",
			"/ks_dashboard_ninja/static/src/xml/ks_dn_global_filter.xml",
			"/ks_dashboard_ninja/static/src/xml/ks_dashboard_ninja_templates.xml",
			"/ks_dashboard_ninja/static/src/xml/ks_dashboard_pro.xml",
			"/ks_dashboard_ninja/static/src/xml/ks_import_list_view_template.xml",
			"/ks_dashboard_ninja/static/src/xml/ks_dashboard_ninja_item_templates.xml",
			"/ks_dashboard_ninja/static/src/xml/ks_dashboard_ninja_item_theme.xml",
			"/ks_dashboard_ninja/static/src/xml/ks_to_do_template.xml",
			"/ks_dashboard_ninja/static/src/xml/ks_quick_edit_view.xml",

			"/ks_dashboard_ninja/static/src/css/ks_dashboard_ninja.scss",
			"/ks_dashboard_ninja/static/src/css/ks_dashboard_ninja_item.css",
			"/ks_dashboard_ninja/static/src/css/ks_icon_container_modal.css",
			"/ks_dashboard_ninja/static/src/css/ks_dashboard_item_theme.css",
			"/ks_dashboard_ninja/static/src/css/ks_dn_filter.css",
			"/ks_dashboard_ninja/static/src/css/ks_toggle_icon.css",
			"/ks_dashboard_ninja/static/src/css/ks_dashboard_options.css",
			"/ks_dashboard_ninja/static/src/js/ks_global_functions.js",
			"/ks_dashboard_ninja/static/src/js/ks_dashboard_ninja.js",
			"/ks_dashboard_ninja/static/src/js/ks_to_do_dashboard.js",
			"/ks_dashboard_ninja/static/src/js/ks_filter_props.js",
			"/ks_dashboard_ninja/static/src/js/ks_color_picker.js",
			"/ks_dashboard_ninja/static/src/js/ks_dashboard_ninja_item_preview.js",
			"/ks_dashboard_ninja/static/src/js/ks_image_basic_widget.js",
			"/ks_dashboard_ninja/static/src/js/ks_dashboard_item_theme.js",
			"/ks_dashboard_ninja/static/src/js/ks_widget_toggle.js",
			"/ks_dashboard_ninja/static/src/js/ks_import_dashboard.js",
			"/ks_dashboard_ninja/static/src/js/ks_domain_fix.js",
			"/ks_dashboard_ninja/static/src/js/ks_quick_edit_view.js",
			"/ks_dashboard_ninja/static/src/js/ks_dashboard_ninja_kpi_preview.js",
			"/ks_dashboard_ninja/static/src/js/ks_date_picker.js",
			"/ks_dashboard_ninja/static/lib/css/gridstack.min.css",
			"/ks_dashboard_ninja/static/src/css/ks_dashboard_ninja_pro.css",
			"/ks_dashboard_ninja/static/src/css/ks_dashboard_gridstack.css",
			"/ks_dashboard_ninja/static/src/css/ks_to_do_item.css",
			"/ks_dashboard_ninja/static/src/scss/ks_dn_gridstack.scss",
			"/ks_dashboard_ninja/static/src/js/ks_dashboard_ninja_graph_preview.js",
			"/ks_dashboard_ninja/static/src/js/ks_dashboard_ninja_list_view_preview.js",
			"/ks_dashboard_ninja/static/src/js/ks_to_do_preview.js",

			
		],
	},

	'data': [
		'security/ir.model.access.csv',
		'security/ks_security_groups.xml',
		'data/ks_default_data.xml',
		'views/ks_dashboard_ninja_view.xml',
		'views/ks_dashboard_ninja_item_view.xml',
		'views/ks_dashboard_action.xml',
	],

	'qweb': [],
	'demo': [
		'demo/ks_dashboard_ninja_demo.xml',
	],

	'uninstall_hook': 'uninstall_hook',

}
