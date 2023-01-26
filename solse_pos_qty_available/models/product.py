# -*- coding: utf-8 -*-
# Copyright (c) 2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import api, fields, models, _
from operator import itemgetter
from itertools import groupby
import logging
_logging = logging.getLogger(__name__)

class Product(models.Model):
	_inherit = "product.product"

	location_qty_in_pos = fields.Float(string='Quantity')

	@api.model
	def get_location_qty(self, picking_type_id):
		product_list = []
		products = self.env['product.product'].search([('available_in_pos', '=', True) ])
		picking_type = self.env['stock.picking.type'].search([('id', '=', picking_type_id) ])
		#self.with_context({'warehouse': w.id}).cant_fraccion
		for product_id in products:
			product_list.append({
				'id': product_id.id,
				'location_qty_available': product_id.with_context({'warehouse': picking_type.warehouse_id.id}).qty_available,
			})
		return product_list

	@api.model
	def get_location_qty_products(self, picking_type_id, producto_ids):
		product_list = []
		products = self.env['product.product'].search([('id', 'in', producto_ids) ])
		picking_type = self.env['stock.picking.type'].search([('id', '=', picking_type_id) ])
		for product_id in products:
			product_list.append({
				'id': product_id.id,
				'location_qty_available': product_id.with_context({'warehouse': picking_type.warehouse_id.id}).qty_available,
			})
		return product_list