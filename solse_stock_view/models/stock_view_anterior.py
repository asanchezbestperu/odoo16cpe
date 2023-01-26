# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import api, fields, models,_
from odoo.exceptions import UserError, Warning, ValidationError
from dateutil.relativedelta import relativedelta
import logging
_logging = logging.getLogger(__name__)


class SStockView(models.Model):
	_name = 'report.sstock.view'
	_description = 'Stock de Productos por Ubicación'

	product_id = fields.Many2one('product.product', 'Producto')
	name = fields.Char("Nombre", related="product_id.name")
	ubicacion = fields.Many2one('stock.location', 'Ubicación')
	cantidad = fields.Float('Cantidad', compute="_compute_cantidad")
	stock_quant_ids = fields.One2many('stock.quant', 'resumen_stock', 'Movimientos')

	@api.depends('stock_quant_ids', 'stock_quant_ids.available_quantity')
	def _compute_cantidad(self):
		for reg in self:
			cantidad_suma = 0
			for mov in reg.stock_quant_ids:
				cantidad_suma = cantidad_suma + mov.available_quantity

			reg.cantidad = cantidad_suma


	def recrear_stock(self):
		productos = self.env['product.product'].search([])
		for reg in productos:
			dominio = [('product_id', '=', reg.id)]
			registro = self.env['report.sstock.view'].search(dominio)
			if not registro:
				registro = self.env['report.sstock.view'].create({
					'product_id': reg.id
				})

		movimientos = self.env['stock.quant'].search([('location_id.usage', '=', 'internal')])
		for res in movimientos:
			dominio = [('product_id', '=', res.product_id.id), ('ubicacion', '=', res.location_id.id)]
			registro = self.env['report.sstock.view'].search(dominio)
			if not registro:
				dominio = [('product_id', '=', res.product_id.id), ('ubicacion', '=', False)]
				registro = self.env['report.sstock.view'].search(dominio)
				if registro:
					registro.ubicacion = res.location_id.id
				else:
					datos_stock = {
						'product_id': res.product_id.id,
						'ubicacion': res.location_id.id,
					}
					registro = self.env['report.sstock.view'].create(datos_stock)

			res.write({'resumen_stock': registro.id})

class SStockViewLote(models.Model):
	_name = 'report.sstock.lote.view'
	_description = 'Stock de Productos por Lote'

	product_id = fields.Many2one('product.product', 'Producto')
	name = fields.Char("Nombre", related="product_id.name")
	ubicacion = fields.Many2one('stock.location', 'Ubicación')
	lot_id = fields.Many2one('stock.production.lot', 'Lote')
	cantidad = fields.Float('Cantidad', compute="_compute_cantidad")
	stock_quant_ids = fields.One2many('stock.quant', 'resumen_stock_lote', 'Movimientos')

	"""lot_id = fields.Many2one(
		'stock.production.lot', 'Lot/Serial Number', index=True,
		ondelete='restrict', check_company=True,
		domain=lambda self: self._domain_lot_id())"""

	@api.depends('stock_quant_ids', 'stock_quant_ids.available_quantity')
	def _compute_cantidad(self):
		for reg in self:
			cantidad_suma = 0
			for mov in reg.stock_quant_ids:
				cantidad_suma = cantidad_suma + mov.available_quantity

			reg.cantidad = cantidad_suma


	def recrear_stock(self):
		productos = self.env['product.product'].search([])
		for reg in productos:
			dominio = [('product_id', '=', reg.id)]
			registro = self.env['report.sstock.lote.view'].search(dominio)
			if not registro:
				registro = self.env['report.sstock.lote.view'].create({
					'product_id': reg.id
				})

		movimientos = self.env['stock.quant'].search([('location_id.usage', '=', 'internal')])
		for res in movimientos:
			dominio_lote = [('product_id', '=', res.product_id.id), ('ubicacion', '=', res.location_id.id), ('lot_id', '=', res.lot_id.id)]
			registro = self.env['report.sstock.lote.view'].search(dominio_lote)
			if not registro:
				dominio_lote = [('product_id', '=', res.product_id.id), ('ubicacion', '=', False)]
				registro = self.env['report.sstock.lote.view'].search(dominio_lote)
				if registro:
					registro.ubicacion = res.location_id.id
					registro.lot_id = res.lot_id.id
				else:
					datos_stock = {
						'product_id': res.product_id.id,
						'ubicacion': res.location_id.id,
						'lot_id': res.lot_id.id,
					}
					registro = self.env['report.sstock.lote.view'].create(datos_stock)

			res.write({'resumen_stock_lote': registro.id})


class ProductProduct(models.Model):
	_inherit = 'product.product'

	@api.model
	def create(self, vals):
		res = super(ProductProduct, self).create(vals)
		dominio_ubicacion =  [('es_de_transito', '=', False), ('usage', '=', 'internal')]
		ubicaciones = self.env['stock.location'].search(dominio_ubicacion)
		datos_stock = {
			'product_id': res.id,
		}
		self.env['report.sstock.view'].create(datos_stock)
		self.env['report.sstock.lote.view'].create(datos_stock)
		return res

	def unlink(self):
		for reg in self:
			vista_stock = self.env['report.sstock.view'].search([('product_id', '=', reg.id)])
			if vista_stock:
				vista_stock.unlink()

			vista_stock_lote = self.env['report.sstock.lote.view'].search([('product_id', '=', reg.id)])
			if vista_stock_lote:
				vista_stock_lote.unlink()
		return super(ProductProduct, self).unlink()


class StockQuant(models.Model):
	_inherit = 'stock.quant'

	resumen_stock = fields.Many2one('report.sstock.view', 'Resumen Stock')
	resumen_stock_lote = fields.Many2one('report.sstock.lote.view', 'Resumen Stock x Lote')

	@api.model
	def create(self, vals):
		res = super(StockQuant, self).create(vals)
		if res.location_id.usage != 'internal':
			return res
		
		dominio = [('product_id', '=', res.product_id.id), ('ubicacion', '=', res.location_id.id)]
		dominio_lote = [('product_id', '=', res.product_id.id), ('ubicacion', '=', res.location_id.id), ('lot_id', '=', res.lot_id.id)]

		registro = self.env['report.sstock.view'].search(dominio)
		registro_lote = self.env['report.sstock.lote.view'].search(dominio_lote)
		
		if not registro:
			dominio = [('product_id', '=', res.product_id.id), ('ubicacion', '=', False)]
			registro = self.env['report.sstock.view'].search(dominio)
			if registro:
				registro.ubicacion = res.location_id.id
			else:
				datos_stock = {
					'product_id': res.product_id.id,
					'ubicacion': res.location_id.id,
				}
				registro = self.env['report.sstock.view'].create(datos_stock)

		if not registro_lote:
			dominio_lote = [('product_id', '=', res.product_id.id), ('ubicacion', '=', False)]
			registro_lote = self.env['report.sstock.lote.view'].search(dominio_lote)
			if registro_lote:
				registro_lote.ubicacion = res.location_id.id
				registro_lote.lot_id = res.lot_id.id
			else:
				datos_stock = {
					'product_id': res.product_id.id,
					'ubicacion': res.location_id.id,
					'lot_id': res.lot_id.id,
				}
				registro_lote = self.env['report.sstock.lote.view'].create(datos_stock)

		res.write({'resumen_stock': registro.id, 'resumen_stock_lote': registro_lote.id})
		return res
