# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging
_logging = logging.getLogger(__name__)

class ProductProduct(models.Model):
	_inherit = 'product.product'

	def filtrar_productos_por_sucursal(self, sucursal_id):
		producto_ids = self.ids

		return producto_ids