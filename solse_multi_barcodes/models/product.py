# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
import re
from odoo.tools import float_compare, float_round
import logging
_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
	_inherit = 'product.product'

	product_multi_barcodes = fields.One2many('multi.barcode.products', 'product_multi', string='Códigos de Barras')
	datos_str_barcodes = fields.Char("Código barra adicional", compute="_compute_datos_str_barcodes", store=True)

	_sql_constraints = [
		('barcode_uniq', 'check(1=1)', 'No error')
	]

	@api.depends('product_multi_barcodes', 'product_multi_barcodes.multi_barcode')
	def _compute_datos_str_barcodes(self):
		for reg in self:
			datos_str_barcodes = []
			for item in reg.product_multi_barcodes:
				if item.multi_barcode:
					datos_str_barcodes.append(item.multi_barcode)
			reg.datos_str_barcodes = "#".join(datos_str_barcodes)

	@api.model
	def create(self, vals):
		res = super(ProductProduct, self).create(vals)
		res.product_multi_barcodes.update({
			'template_multi': res.product_tmpl_id.id
		})
		return res

	def write(self, vals):
		res = super(ProductProduct, self).write(vals)
		if len(self) > 1:
			for reg in self:
				reg.product_multi_barcodes.update({
					'template_multi': reg.product_tmpl_id.id
				})
		else:
			self.product_multi_barcodes.update({
				'template_multi': self.product_tmpl_id.id
			})
		return res

	@api.model
	def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
		args = args or []
		domain = []
		if name:
			domain = ['|', '|', ('name', operator, name), ('default_code', operator, name),
					  '|', ('barcode', operator, name), ('product_multi_barcodes', operator, name)]
		return self._search(expression.AND([domain, args]),
								  limit=limit, access_rights_uid=name_get_uid)

	@api.constrains('barcode', 'product_multi_barcodes', 'active', 'product_multi_barcodes.name', 'product_multi_barcodes.multi_barcode')
	def _check_unique_barcode(self):
		barcodes_duplicate = []
		for product in self:
			barcode_names_n = []
			if product.product_multi_barcodes:
				barcode_names_n = product.mapped('product_multi_barcodes.name')
			if product.barcode:
				barcode_names_n.append(product.barcode)

			if not barcode_names_n:
				continue

			barcode_names = []
			for item  in barcode_names_n:
				if item and item != "":
					barcode_names.append(item)

			if not barcode_names:
				continue
				
			products = self.env['product.product'].search([
				('barcode', 'in', barcode_names),
				('id', '!=', product.id),
				('active', '=', True),
			])
			product_multi_barcodes = self.env['multi.barcode.products'].search([
				('multi_barcode', 'in', barcode_names),
				('product_multi', '!=', product.id),
			])
			if len(barcode_names) != len(set(barcode_names)):
				barcodes_multi = set([barcode for barcode in barcode_names if barcode_names.count(barcode) > 1])
				for barcode in barcodes_multi:
					barcodes_duplicate.append(barcode)
			if product_multi_barcodes:
				barcodes = [barcode.multi_barcode for barcode in product_multi_barcodes]
				for barcode in barcodes:
					barcodes_duplicate.append(barcode)
			if products:
				barcodes_product = [product.barcode for product in products]
				for barcode in barcodes_product:
					barcodes_duplicate.append(barcode)
		if barcodes_duplicate:
			raise UserError("Se encontraron codigos de barras repetidos {0} ".format(", ".join(set(barcodes_duplicate))) )

	"""@api.model
	def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
		if not args:
			args = []
		if name:
			positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
			product_ids = []
			if operator in positive_operators:
				product_ids = list(self._search([('default_code', '=', name)] + args, limit=limit, access_rights_uid=name_get_uid))
				if not product_ids:
					product_ids = list(self._search([('barcode', '=', name)] + args, limit=limit, access_rights_uid=name_get_uid))
				if not product_ids:
					productos = self.env['multi.barcode.products'].search([('multi_barcode', '=', name)])
					lst_prod = []
					for prod in productos:
						lst_prod.append(prod.product_multi.id)
					domain = [('id', "in", lst_prod)]
					product_ids = list(self._search(domain, limit=limit, access_rights_uid=name_get_uid))
			if not product_ids and operator not in expression.NEGATIVE_TERM_OPERATORS:
				# Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
				# on a database with thousands of matching products, due to the huge merge+unique needed for the
				# OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
				# Performing a quick memory merge of ids in Python will give much better performance
				product_ids = list(self._search(args + [('default_code', operator, name)], limit=limit))
				if not limit or len(product_ids) < limit:
					# we may underrun the limit because of dupes in the results, that's fine
					limit2 = (limit - len(product_ids)) if limit else False
					product2_ids = self._search(args + [('name', operator, name), ('id', 'not in', product_ids)], limit=limit2, access_rights_uid=name_get_uid)
					product_ids.extend(product2_ids)
			elif not product_ids and operator in expression.NEGATIVE_TERM_OPERATORS:
				domain = expression.OR([
					['&', ('default_code', operator, name), ('name', operator, name)],
					['&', ('default_code', '=', False), ('name', operator, name)],
				])
				domain = expression.AND([args, domain])
				product_ids = list(self._search(domain, limit=limit, access_rights_uid=name_get_uid))
			if not product_ids and operator in positive_operators:
				ptrn = re.compile('(\[(.*?)\])')
				res = ptrn.search(name)
				if res:
					product_ids = list(self._search([('default_code', '=', res.group(2))] + args, limit=limit, access_rights_uid=name_get_uid))
			# still no results, partner in context: search on supplier info as last hope to find something
			if not product_ids and self._context.get('partner_id'):
				suppliers_ids = self.env['product.supplierinfo']._search([
					('name', '=', self._context.get('partner_id')),
					'|',
					('product_code', operator, name),
					('product_name', operator, name)], access_rights_uid=name_get_uid)
				if suppliers_ids:
					product_ids = self._search([('product_tmpl_id.seller_ids', 'in', suppliers_ids)], limit=limit, access_rights_uid=name_get_uid)
		else:
			product_ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
		return product_ids

	"""


class ProductTemplate(models.Model):
	_inherit = 'product.template'

	template_multi_barcodes = fields.One2many('multi.barcode.products', 'template_multi', string='Barcodes')

	@api.model
	def create(self, vals):
		res = super(ProductTemplate, self).create(vals)
		res.template_multi_barcodes.update({
			'product_multi': res.product_variant_id.id
		})
		return res

	def write(self, vals):
		res = super(ProductTemplate, self).write(vals)
		if self.template_multi_barcodes:
			self.template_multi_barcodes.update({
				'product_multi': self.product_variant_id.id
			})
		return res

	@api.constrains('barcode', 'template_multi_barcodes', 'active', 'template_multi_barcodes.name' , 'template_multi_barcodes.multi_barcode')
	def _check_unique_barcode(self):
		barcodes_duplicate = []
		for product in self:
			barcode_names_n = []
			if product.template_multi_barcodes:
				barcode_names_n = product.mapped('template_multi_barcodes.name')
			if product.barcode:
				barcode_names_n.append(product.barcode)

			if not barcode_names_n:
				continue

			barcode_names = []
			for item  in barcode_names_n:
				if item and item != "":
					barcode_names.append(item)

			if not barcode_names:
				continue

			products = self.env['product.template'].search([
				('barcode', 'in', barcode_names),
				('id', '!=', product.id),
				('active', '=', True),
			])
			template_multi_barcodes = self.env['multi.barcode.products'].search([
				('multi_barcode', 'in', barcode_names),
				('template_multi', '!=', product.id),
			])
			if len(barcode_names) != len(set(barcode_names)):
				barcodes_multi = set([barcode for barcode in barcode_names if barcode_names.count(barcode) > 1])
				for barcode in barcodes_multi:
					barcodes_duplicate.append(barcode)
			if template_multi_barcodes:
				barcodes = [barcode.multi_barcode for barcode in template_multi_barcodes]
				for barcode in barcodes:
					barcodes_duplicate.append(barcode)
			if products:
				barcodes_product = [product.barcode for product in products]
				for barcode in barcodes_product:
					barcodes_duplicate.append(barcode)
		if barcodes_duplicate:
			raise UserError("Se encontraron codigos de barras repetidos {0} ".format(", ".join(set(barcodes_duplicate))) )



class ProductMultiBarcode(models.Model):
	_name = 'multi.barcode.products'

	multi_barcode = fields.Char(string="Barcode", help="Proporcione códigos de barras alternativos para este producto")
	product_multi = fields.Many2one('product.product')
	name = fields.Char("Nombre", compute="_compute_name", store=True)
	template_multi = fields.Many2one('product.template')
	agregar_datos = fields.Boolean("Editar")
	uom_id = fields.Many2one('uom.uom', 'Und. Medida', required=False, help="Unidad de medida por defecto utilizada para todas las operaciones de stock.")
	list_price = fields.Float('Precio de Venta', default=0.0, digits='Product Price', help="Precio al que se vende el producto a los clientes.", )

	@api.onchange('agregar_datos')
	def _onchange_agregar_datos(self):
		self.uom_id = False

	@api.depends('multi_barcode', 'product_multi')
	def _compute_name(self):
		for reg in self:
			reg.name = reg.multi_barcode if reg.multi_barcode else reg.product_multi.name

	def get_barcode_val(self, product):
		# returns barcode of record in self and product id
		return self.multi_barcode, product

	@api.model
	def obtener_datos(self, vals):
		id_producto = vals.get('product_id', False)
		barcode = vals.get('barcode', False)
		datos = self.env['multi.barcode.products'].search_read([('product_multi', '=', id_producto), ('multi_barcode', '=', barcode)])

		producto = self.env['product.product'].search([("id", "=", id_producto)], limit=1)
		if not datos:
			datos = [{"list_price": producto.lst_price, "uom_id": [producto.uom_id.id, producto.uom_id.name]}]
		else:
			for registro in datos:
				agregar_datos = registro["agregar_datos"]
				if not agregar_datos:
					registro["list_price"] = producto.lst_price
					registro["uom_id"] = [producto.uom_id.id, producto.uom_id.name]

		return datos


	@api.model
	def obtener_lista_codigos(self, vals):
		id_producto = vals.get('product_id', False)
		barcode = vals.get('barcode', False)
		datos = self.env['multi.barcode.products'].search_read([('product_multi', '=', id_producto)])
		producto = self.env['product.product'].search([("id", "=", id_producto)], limit=1)
		datos_ori = [{"id": 0, "name": producto.uom_id.name, "list_price": producto.lst_price, "uom_id": [producto.uom_id.id, producto.uom_id.name]}]
		return datos_ori + datos


