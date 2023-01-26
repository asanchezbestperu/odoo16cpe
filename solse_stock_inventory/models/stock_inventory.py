# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import api, fields, models,_
from odoo.exceptions import UserError, Warning, ValidationError
from dateutil.relativedelta import relativedelta
import logging
_logging = logging.getLogger(__name__)

class Product(models.Model):
	_inherit = "product.product"

	def obtener_datos_stock_almacen(self, alamcen):
		warehouse_list = {
			'name': alamcen.name,
			'qty_available': self.with_context({'warehouse': alamcen.id}).qty_available,
			'forecasted_quantity': self.with_context({'warehouse': alamcen.id}).virtual_available,
			'uom': self.uom_name,
		}
		return warehouse_list

	def obtener_datos_stock_almacen_lote(self, alamcen, lote):
		datos_stock = self.with_context({'warehouse': alamcen.id, 'lot_id': lote})
		warehouse_list = {
			'name': alamcen.name,
			'qty_available': datos_stock.qty_available,
			'forecasted_quantity': datos_stock.virtual_available,
			'uom': self.uom_name,
		}
		return warehouse_list


class SStockInventory(models.Model):
	_name = 'report.sstock.inventory'
	_description = 'Inventario de Productos por Almacen'
	_order = "fecha_inventario desc"

	name = fields.Char("Referencia")
	almacen_id = fields.Many2one('stock.warehouse', 'Almacen')
	
	modo_filtro = fields.Selection([('categoria', 'Categoria')], default='categoria')
	categoria_ids = fields.Many2many('product.category', 'inv_categ', 'inv_id', 'categ_id', string='Categorias')
	fecha_inventario = fields.Date('Fecha de inventario')
	incluir_stock_cero = fields.Boolean('Incluir Stock Cero')
	state = fields.Selection([('draft', 'Borrador'), ('iniciado', 'Iniciado'), ('finalizado', 'Finalizado')], default='draft', string='Estado')
	user_id = fields.Many2one('res.users', string='Encargado', index=True, tracking=2, default=lambda self: self.env.user)

	detalle_ids = fields.One2many('report.sstock.inventory.detail', 'sinvnetario_id', 'Detalle de Inventario')

	def iniciar_inventario_x_categoria(self):
		contador = 0
		for categoria in self.categoria_ids:
			contador = contador + 1
			parametros = {
				'sinvnetario_id': self.id,
				'es_cabecera': True,
				'texto_cabecera': categoria.name,
				'orden': contador,
				'name': categoria.name,
			}
			self.env['report.sstock.inventory.detail'].create(parametros)
			productos = self.env['product.product'].search([('categ_id', '=', categoria.id)])
			for prod in productos:
				lotes_prod = self.env['stock.lot'].search([('product_id', '=', prod.id)])
				if lotes_prod:
					for lote in lotes_prod:
						cantidades = prod.obtener_datos_stock_almacen_lote(self.almacen_id, lote.id)
						contador = contador + 1
						cantidad_teorica = cantidades['qty_available']
						if cantidad_teorica == 0 and not self.incluir_stock_cero:
							continue
						parametros = {
							'sinvnetario_id': self.id,
							'es_cabecera': False,
							'orden': contador,
							'product_id': prod.id,
							'lot_id': lote.id,
							'name': prod.name,
							'cant_teorica': cantidad_teorica,
						}
						self.env['report.sstock.inventory.detail'].create(parametros)

				cantidades = prod.obtener_datos_stock_almacen_lote(self.almacen_id, False)
				cantidad_teorica = cantidades['qty_available']
				if cantidad_teorica == 0 and not self.incluir_stock_cero:
					continue

				contador = contador + 1
				parametros = {
					'sinvnetario_id': self.id,
					'es_cabecera': False,
					'orden': contador,
					'product_id': prod.id,
					'name': prod.name,
					'cant_teorica': cantidad_teorica,
				}
				self.env['report.sstock.inventory.detail'].create(parametros)

		self.state = 'iniciado'


	def iniciar_inventario(self):
		if self.modo_filtro == 'categoria':
			self.iniciar_inventario_x_categoria()


	def finalizar_inventario_3(self):
		array_lineas = []
		json_productos = {}
		ubicacion_inventario = self.env['stock.location'].search([('usage', '=', 'inventory')], limit=1)
		for linea in self.detalle_ids:
			if linea.cant_diferencia == 0 or linea.es_cabecera == True:
				continue

			cantidad_total = abs(linea.cant_real)
			lote = linea.lot_id.id or False
			dominio_quant = [('location_id', '=', self.almacen_id.lot_stock_id.id), ('product_id', '=', linea.product_id.id), ('lot_id', '=', lote)]
			quant = self.env['stock.quant'].search(dominio_quant)
			quant.write({'inventory_quantity': cantidad_total, 'quantity': cantidad_total})
			wiz = quant.action_apply_inventory()
			if wiz not in [False, True]:
				try:
					wizard = self.env['stock.track.confirmation'].with_context(wiz['context']).create({})
					if wizard:
						wizard.action_confirm()
				except Exception as e:
					_logging.info("horrorrrrrr")
					_logging.info(e)
			
		self.state = 'finalizado'

	def unlink(self):
		for reg in self:
			if reg.state == 'finalizado':
				raise UserError('No puede eliminar un inventario ya finalizado')
				
		return super(SStockInventory, self).unlink()


class SStockInvetoryDetail(models.Model):
	_name = 'report.sstock.inventory.detail'
	_description = 'Stock de Productos por Lote'

	sinvnetario_id = fields.Many2one('report.sstock.inventory', string='Inventario')
	orden = fields.Integer('Orden')
	es_cabecera = fields.Boolean('Es cabecera')
	texto_cabecera = fields.Char('Texto Cabecera')
	product_id = fields.Many2one('product.product', 'Producto')
	name = fields.Char("Nombre")
	lot_id = fields.Many2one('stock.lot', 'Lote')

	cant_teorica = fields.Float('Cantidad Teorica', default=0.00)
	cant_real = fields.Float('Cantidad Real', default=0.00)
	cant_diferencia = fields.Float('Cantidad Diferencia')

	@api.onchange('cant_teorica', 'cant_real')
	def _onchagen_cantidad(self):
		self.cant_diferencia = self.cant_real - self.cant_teorica