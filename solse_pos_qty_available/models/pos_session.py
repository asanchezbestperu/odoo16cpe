# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)
	
class PosSession(models.Model):
	_inherit = 'pos.session'

	def _loader_params_product_product(self):
		res = super(PosSession, self)._loader_params_product_product()
		res['search_params']['fields'].extend(["qty_available", "location_qty_in_pos"])
		return res

	def _loader_params_stock_picking_type(self):
		res = super(PosSession, self)._loader_params_stock_picking_type()
		res['search_params']['fields'].extend(["warehouse_id"])
		return res