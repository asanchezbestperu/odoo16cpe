# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class PosConfig(models.Model):
	_inherit = 'pos.config'

	branch_id = fields.Many2one('res.branch', 'Sucursal', index=1, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
	branch_nombre = fields.Char("Nombre Sucursal", related="branch_id.name", store=True)
	branch_direccion = fields.Char("Dirección Sucursal", related="branch_id.street", store=True)
	branch_telefono = fields.Char("Telefono Sucursal", related="branch_id.phone", store=True)

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError('POS config: Se requiere compañía con Sucursal.')
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError('POS config: Sucursal debe pertenecer a la Empresa seleccionada.')

	def query_sin_sucursal(self):
		query = """
			WITH pm AS (
				  SELECT product_id,
						 Max(write_date) date
					FROM stock_quant
				GROUP BY product_id
			)
			   SELECT p.id
				 FROM product_product p
			LEFT JOIN product_template t ON product_tmpl_id=t.id
			LEFT JOIN pm ON p.id=pm.product_id
				WHERE (
						t.available_in_pos
					AND t.sale_ok
					AND (t.company_id=%(company_id)s OR t.company_id IS NULL)
					AND %(available_categ_ids)s IS NULL OR t.pos_categ_id=ANY(%(available_categ_ids)s)
				)    OR p.id=%(tip_product_id)s
			 ORDER BY t.priority DESC,
					  t.detailed_type DESC,
					  COALESCE(pm.date,p.write_date) DESC 
				LIMIT %(limit)s
		"""
		return query

	def query_con_sucursal(self):
		query = """
			WITH pm AS (
				  SELECT product_id,
						 Max(write_date) date
					FROM stock_quant
				GROUP BY product_id
			)
			   SELECT p.id
				 FROM product_product p
			LEFT JOIN product_template t ON product_tmpl_id=t.id
			LEFT JOIN pm ON p.id=pm.product_id
				WHERE (
						t.available_in_pos
					AND t.sale_ok
					AND (t.company_id=%(company_id)s OR t.company_id IS NULL)
					AND (t.branch_id=%(branch_id)s OR t.branch_id IS NULL)
					AND %(available_categ_ids)s IS NULL OR t.pos_categ_id=ANY(%(available_categ_ids)s)
				)    OR p.id=%(tip_product_id)s
			 ORDER BY t.priority DESC,
					  t.detailed_type DESC,
					  COALESCE(pm.date,p.write_date) DESC 
				LIMIT %(limit)s
		"""
		return query

	def get_limited_products_loading(self, fields):
		query = self.query_sin_sucursal()
		params = {
			'company_id': self.company_id.id,
			'available_categ_ids': self.iface_available_categ_ids.mapped('id') if self.iface_available_categ_ids else None,
			'tip_product_id': self.tip_product_id.id if self.tip_product_id else None,
			'limit': self.limited_products_amount
		}
		if self.branch_id:
			query = self.query_con_sucursal()
			params = {
				'company_id': self.company_id.id,
				'branch_id': self.branch_id.id,
				'available_categ_ids': self.iface_available_categ_ids.mapped('id') if self.iface_available_categ_ids else None,
				'tip_product_id': self.tip_product_id.id if self.tip_product_id else None,
				'limit': self.limited_products_amount
			}
		self.env.cr.execute(query, params)
		product_ids = self.env.cr.fetchall()
		products = self.env['product.product'].search_read([('id', 'in', product_ids)], fields=fields)
		return products

class PosSession(models.Model):
	_inherit = 'pos.session'

	branch_id = fields.Many2one('res.branch', related='config_id.branch_id', string='Sucursal', readonly=True, store=True)

class PosPayment(models.Model):
	_inherit = 'pos.payment'

	branch_id = fields.Many2one('res.branch', related='pos_order_id.branch_id', string='Sucursal', readonly=True)
