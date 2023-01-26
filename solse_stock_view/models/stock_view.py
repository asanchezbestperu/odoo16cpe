# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import api, fields, models,_
from odoo.exceptions import UserError, Warning, ValidationError
from dateutil.relativedelta import relativedelta
import xml.etree.cElementTree as ET
from lxml import etree
import json
import logging
_logging = logging.getLogger(__name__)

class Location(models.Model):
	_inherit = "stock.location"
	es_de_transito = fields.Boolean("¿Es una ubicación de transito?")

class SStockView(models.Model):
	_name = 'report.sstock.view'
	_description = 'Stock de Productos por Ubicación'

	product_id = fields.Many2one('product.product', 'Producto')
	name = fields.Char("Nombre", related="product_id.name")
	
	ubicacion_1 = fields.Many2one('stock.location', 'Ubicación n1')
	cantidad_1 = fields.Float('Cantidad n1', compute="_compute_cantidad")

	ubicacion_2 = fields.Many2one('stock.location', 'Ubicación n2')
	cantidad_2 = fields.Float('Cantidad n2', compute="_compute_cantidad")

	ubicacion_3 = fields.Many2one('stock.location', 'Ubicación n3')
	cantidad_3 = fields.Float('Cantidad n3', compute="_compute_cantidad")

	ubicacion_4 = fields.Many2one('stock.location', 'Ubicación n4')
	cantidad_4 = fields.Float('Cantidad n4', compute="_compute_cantidad")

	ubicacion_5 = fields.Many2one('stock.location', 'Ubicación n5')
	cantidad_5 = fields.Float('Cantidad n5', compute="_compute_cantidad")

	ubicacion_6 = fields.Many2one('stock.location', 'Ubicación n6')
	cantidad_6 = fields.Float('Cantidad n6', compute="_compute_cantidad")

	ubicacion_7 = fields.Many2one('stock.location', 'Ubicación n7')
	cantidad_7 = fields.Float('Cantidad n7', compute="_compute_cantidad")

	ubicacion_8 = fields.Many2one('stock.location', 'Ubicación n8')
	cantidad_8 = fields.Float('Cantidad n8', compute="_compute_cantidad")

	ubicacion_9 = fields.Many2one('stock.location', 'Ubicación n9')
	cantidad_9 = fields.Float('Cantidad n9', compute="_compute_cantidad")

	stock_quant_ids = fields.One2many('stock.quant', 'resumen_stock', 'Movimientos')

	@api.depends('stock_quant_ids', 'stock_quant_ids.available_quantity')
	def _compute_cantidad(self):
		ubicaciones = self.env['stock.location'].search([('usage', '=', 'internal')], order='id asc')
		json_ubicaciones =  {}
		contador = 0
		for reg in ubicaciones:
			contador = contador + 1
			json_ubicaciones[reg.id] = contador

		for reg in self:
			json_datos = {
				'cantidad_1': 0,'cantidad_2': 0,'cantidad_3': 0,'cantidad_4': 0,
				'cantidad_5': 0,'cantidad_6': 0,'cantidad_7': 0,'cantidad_8': 0,
				'cantidad_9': 0,
			}
			for mov in reg.stock_quant_ids:
				posicion = str(json_ubicaciones[mov.location_id.id])
				json_datos['cantidad_'+posicion] = json_datos['cantidad_'+posicion] + mov.available_quantity

			reg.cantidad_1 = json_datos['cantidad_1']
			reg.cantidad_2 = json_datos['cantidad_2']
			reg.cantidad_3 = json_datos['cantidad_3']
			reg.cantidad_4 = json_datos['cantidad_4']
			reg.cantidad_5 = json_datos['cantidad_5']
			reg.cantidad_6 = json_datos['cantidad_6']
			reg.cantidad_7 = json_datos['cantidad_7']
			reg.cantidad_8 = json_datos['cantidad_8']
			reg.cantidad_9 = json_datos['cantidad_9']


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
			dominio = [('product_id', '=', res.product_id.id)]
			registro = self.env['report.sstock.view'].search(dominio)
			res.write({'resumen_stock': registro.id})

	def obtener_indice(self, nombre):
		indice = 1
		if nombre == 'cantidad_2':
			indice = 2
		elif nombre == 'cantidad_3':
			indice = 3
		elif nombre == 'cantidad_4':
			indice = 4
		elif nombre == 'cantidad_5':
			indice = 5
		elif nombre == 'cantidad_6':
			indice = 6
		elif nombre == 'cantidad_7':
			indice = 7
		elif nombre == 'cantidad_8':
			indice = 8
		elif nombre == 'cantidad_9':
			indice = 9

		return indice


	@api.model
	def get_view(self, view_id=None, view_type='form', **options):
		res = super(SStockView, self).get_view(view_id, view_type, **options)
		if view_type in ['tree']:
			parametros = {}
			paso_validacion = True
			datos = False
			if self._context.get('params') and 'id' in self._context['params']:
				datos = self.env['report.sstock.view'].search([("id", "=", self._context['params']['id'])], limit=1)

			ubicaciones = self.env['stock.location'].search([('usage', '=', 'internal')], order='id asc')
			cant_reg = 0
			if ubicaciones:
				cant_reg = len(ubicaciones)

			#{'action': 198, 'cids': 1, 'id': '', 'menu_id': 101, 'model': 'account.move', 'view_type': 'form'}
			if paso_validacion:
				root = ET.fromstring(res['arch'])
				for el in root.iter('field'):
					ubicacion = ubicaciones[self.obtener_indice(el.attrib.get('name')) - 1]
					if el.attrib.get('name') in ['cantidad_1', 'cantidad_2', 'cantidad_3', 'cantidad_4', 'cantidad_5', 'cantidad_6', 'cantidad_7', 'cantidad_8', 'cantidad_9']:
						json_mod = {
							'column_invisible': False,
						}
						parametros = {
							'string': ubicacion.complete_name,
							'invisible': '0', 
							'modifiers': json.dumps(json_mod),
						}
						el.attrib.update(parametros)
						break

				res.update({'arch': ET.tostring(root, encoding='utf8', method='xml')})

		return res



class SStockViewLote(models.Model):
	_name = 'report.sstock.lote.view'
	_description = 'Stock de Productos por Lote'

	product_id = fields.Many2one('product.product', 'Producto')
	name = fields.Char("Nombre", related="product_id.name")
	lot_id = fields.Many2one('stock.lot', 'Lote')

	ubicacion_1 = fields.Many2one('stock.location', 'Ubicación n1')
	cantidad_1 = fields.Float('Cantidad n1', compute="_compute_cantidad")

	ubicacion_2 = fields.Many2one('stock.location', 'Ubicación n2')
	cantidad_2 = fields.Float('Cantidad n2', compute="_compute_cantidad")

	ubicacion_3 = fields.Many2one('stock.location', 'Ubicación n3')
	cantidad_3 = fields.Float('Cantidad n3', compute="_compute_cantidad")

	ubicacion_4 = fields.Many2one('stock.location', 'Ubicación n4')
	cantidad_4 = fields.Float('Cantidad n4', compute="_compute_cantidad")

	ubicacion_5 = fields.Many2one('stock.location', 'Ubicación n5')
	cantidad_5 = fields.Float('Cantidad n5', compute="_compute_cantidad")

	ubicacion_6 = fields.Many2one('stock.location', 'Ubicación n6')
	cantidad_6 = fields.Float('Cantidad n6', compute="_compute_cantidad")

	ubicacion_7 = fields.Many2one('stock.location', 'Ubicación n7')
	cantidad_7 = fields.Float('Cantidad n7', compute="_compute_cantidad")

	ubicacion_8 = fields.Many2one('stock.location', 'Ubicación n8')
	cantidad_8 = fields.Float('Cantidad n8', compute="_compute_cantidad")

	ubicacion_9 = fields.Many2one('stock.location', 'Ubicación n9')
	cantidad_9 = fields.Float('Cantidad n9', compute="_compute_cantidad")



	stock_quant_ids = fields.One2many('stock.quant', 'resumen_stock_lote', 'Movimientos')

	"""lot_id = fields.Many2one(
		'stock.lot', 'Lot/Serial Number', index=True,
		ondelete='restrict', check_company=True,
		domain=lambda self: self._domain_lot_id())"""

	"""@api.depends('stock_quant_ids', 'stock_quant_ids.available_quantity')
	def _compute_cantidad(self):
		for reg in self:
			cantidad_suma = 0
			for mov in reg.stock_quant_ids:
				cantidad_suma = cantidad_suma + mov.available_quantity

			reg.cantidad = cantidad_suma"""

	@api.depends('stock_quant_ids', 'stock_quant_ids.available_quantity')
	def _compute_cantidad(self):
		ubicaciones = self.env['stock.location'].search([('usage', '=', 'internal')], order='id asc')
		json_ubicaciones =  {}
		contador = 0
		for reg in ubicaciones:
			contador = contador + 1
			json_ubicaciones[reg.id] = contador

		for reg in self:
			json_datos = {
				'cantidad_1': 0,'cantidad_2': 0,'cantidad_3': 0,'cantidad_4': 0,
				'cantidad_5': 0,'cantidad_6': 0,'cantidad_7': 0,'cantidad_8': 0,
				'cantidad_9': 0,
			}
			for mov in reg.stock_quant_ids:
				posicion = str(json_ubicaciones[mov.location_id.id])
				json_datos['cantidad_'+posicion] = json_datos['cantidad_'+posicion] + mov.available_quantity

			reg.cantidad_1 = json_datos['cantidad_1']
			reg.cantidad_2 = json_datos['cantidad_2']
			reg.cantidad_3 = json_datos['cantidad_3']
			reg.cantidad_4 = json_datos['cantidad_4']
			reg.cantidad_5 = json_datos['cantidad_5']
			reg.cantidad_6 = json_datos['cantidad_6']
			reg.cantidad_7 = json_datos['cantidad_7']
			reg.cantidad_8 = json_datos['cantidad_8']
			reg.cantidad_9 = json_datos['cantidad_9']


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
			dominio_lote = [('product_id', '=', res.product_id.id), ('lot_id', '=', res.lot_id.id)]
			registro = self.env['report.sstock.lote.view'].search(dominio_lote)
			if not registro:
				dominio_lote = [('product_id', '=', res.product_id.id), ('lot_id', '=', False)]
				registro = self.env['report.sstock.lote.view'].search(dominio_lote)
				if registro:
					registro.lot_id = res.lot_id.id
				else:
					datos_stock = {
						'product_id': res.product_id.id,
						'lot_id': res.lot_id.id,
					}
					registro = self.env['report.sstock.lote.view'].create(datos_stock)

			res.write({'resumen_stock_lote': registro.id})

	def obtener_indice(self, nombre):
		indice = 1
		if nombre == 'cantidad_2':
			indice = 2
		elif nombre == 'cantidad_3':
			indice = 3
		elif nombre == 'cantidad_4':
			indice = 4
		elif nombre == 'cantidad_5':
			indice = 5
		elif nombre == 'cantidad_6':
			indice = 6
		elif nombre == 'cantidad_7':
			indice = 7
		elif nombre == 'cantidad_8':
			indice = 8
		elif nombre == 'cantidad_9':
			indice = 9

		return indice


	@api.model
	def get_view(self, view_id=None, view_type='form', **options):
		res = super(SStockViewLote, self).get_view(view_id, view_type, **options)
		if view_type in ['tree']:
			parametros = {}
			paso_validacion = True
			ubicaciones = self.env['stock.location'].search([('usage', '=', 'internal')], order='id asc')
			cant_reg = 0
			if ubicaciones:
				cant_reg = len(ubicaciones)

			#{'action': 198, 'cids': 1, 'id': '', 'menu_id': 101, 'model': 'account.move', 'view_type': 'form'}
			if paso_validacion:
				root = ET.fromstring(res['arch'])
				for el in root.iter('field'):
					ubicacion = ubicaciones[self.obtener_indice(el.attrib.get('name')) - 1]
					if el.attrib.get('name') in ['cantidad_1', 'cantidad_2', 'cantidad_3', 'cantidad_4', 'cantidad_5', 'cantidad_6', 'cantidad_7', 'cantidad_8', 'cantidad_9']:
						json_mod = {
							'column_invisible': False,
						}
						parametros = {
							'string': ubicacion.complete_name,
							'invisible': '0', 
							'modifiers': json.dumps(json_mod),
						}
						el.attrib.update(parametros)
						break

				res.update({'arch': ET.tostring(root, encoding='utf8', method='xml')})

		return res


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
		
		dominio = [('product_id', '=', res.product_id.id)]
		dominio_lote = [('product_id', '=', res.product_id.id), ('lot_id', '=', res.lot_id.id)]

		registro = self.env['report.sstock.view'].search(dominio)
		registro_lote = self.env['report.sstock.lote.view'].search(dominio_lote)

		if not registro_lote:
			dominio_lote = [('product_id', '=', res.product_id.id), ('lot_id', '=', False)]
			registro_lote = self.env['report.sstock.lote.view'].search(dominio_lote)
			if registro_lote:
				registro_lote.lot_id = res.lot_id.id
			else:
				datos_stock = {
					'product_id': res.product_id.id,
					'lot_id': res.lot_id.id,
				}
				registro_lote = self.env['report.sstock.lote.view'].create(datos_stock)


		res.write({'resumen_stock': registro.id, 'resumen_stock_lote': registro_lote.id})
		return res
