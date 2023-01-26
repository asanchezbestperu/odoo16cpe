# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import models
from itertools import groupby
from odoo.osv.expression import AND
import logging
_logging = logging.getLogger(__name__)

class PosSession(models.Model):
	_inherit = 'pos.session'

	def get_pos_ui_product_product_by_params(self, custom_search_params):
		"""
		:param custom_search_params: a dictionary containing params of a search_read()
		"""
		params = self._loader_params_product_product()
		# custom_search_params will take priority
		params['search_params'] = {**params['search_params'], **custom_search_params}
		products = self.env['product.product'].with_context(active_test=False).search_read(**params['search_params'])
		if len(products) > 0:
			self._process_pos_ui_product_product(products)
		return products

	def _loader_params_pos_order(self):
		res = super(PosSession, self)._loader_params_pos_order()
		res['search_params']['fields'].extend(['branch_id', 'branch_nombre', 'branch_direccion', 'branch_telefono'])
		return res

	def _loader_params_product_product(self):
		res = super(PosSession, self)._loader_params_product_product()
		domain = [('sale_ok', '=', True), ('available_in_pos', '=', True), ('company_id', 'in', [self.config_id.company_id.id, False])]
		if self.config_id.branch_id:
			domain = AND([domain, [('branch_id', 'in', [self.config_id.branch_id.id, False])]])
		if self.config_id.limit_categories and self.config_id.iface_available_categ_ids:
			domain = AND([domain, [('pos_categ_id', 'in', self.config_id.iface_available_categ_ids.ids)]])
		if self.config_id.iface_tipproduct:
			domain = OR([domain, [('id', '=', self.config_id.tip_product_id.id)]])

		res['search_params']['fields'].extend(['branch_id'])
		res['search_params']['domain'] = domain

		return res

	"""def _loader_params_product_product(self):
		res = super(PosSession, self)._loader_params_product_product()
		domain = [
			'&', '&', ('sale_ok', '=', True), ('available_in_pos', '=', True), '|',
			('company_id', '=', self.config_id.company_id.id), ('company_id', '=', False)
		]
		if self.config_id.branch_id:
			domain = AND([domain, [('branch_id', 'in', [self.config_id.branch_id.id, False])]])
		if self.config_id.limit_categories and self.config_id.iface_available_categ_ids:
			domain = AND([domain, [('pos_categ_id', 'in', self.config_id.iface_available_categ_ids.ids)]])
		if self.config_id.iface_tipproduct:
			domain = OR([domain, [('id', '=', self.config_id.tip_product_id.id)]])

		_logging.info("=================================== _loader_params_product_product")
		_logging.info(domain)

		res['search_params']['fields'].extend(['branch_id'])
		res['search_params']['domain'] = domain

		return res"""
