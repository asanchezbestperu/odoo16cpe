# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

from odoo import models, fields, api, _
from itertools import groupby

_logger = logging.getLogger(__name__)
	
class StockPicking(models.Model):
	_inherit='stock.picking'

	def _prepare_stock_move_vals(self, first_line, order_lines):
		return {
			'name': first_line.name,
			'product_uom': first_line.product_uom_id.id,
			'picking_id': self.id,
			'picking_type_id': self.picking_type_id.id,
			'product_id': first_line.product_id.id,
			'product_uom_qty': abs(sum(order_lines.mapped('qty'))),
			'state': 'draft',
			'location_id': self.location_id.id,
			'location_dest_id': self.location_dest_id.id,
			'company_id': self.company_id.id,
		}