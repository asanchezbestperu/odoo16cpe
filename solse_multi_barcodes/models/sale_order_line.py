# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)
	
class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	@api.depends('product_id', 'product_uom', 'product_uom_qty')
	def _compute_price_unit(self):
		res = super(SaleOrderLine, self)._compute_price_unit()
		for line in self:
			und_prod = line.product_id.uom_id
			if line.product_id.product_multi_barcodes:
				if und_prod.id == line.product_uom.id:
					continue
				for presentacion in line.product_id.product_multi_barcodes:
					if presentacion.uom_id.id == line.product_uom.id:
						reg.price_unit = presentacion.list_price
						continue