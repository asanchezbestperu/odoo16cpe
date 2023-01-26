# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
import logging
_logging = logging.getLogger(__name__)

class StockPutawayRule(models.Model):
	_inherit = "stock.putaway.rule"

	def _default_location_id(self):
		return super(StockPutawayRule,self)._default_location_id()

	branch_id = fields.Many2one('res.branch', 'Branch', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id, index=True)
	location_in_id = fields.Many2one(
		'stock.location', 'When product arrives in', check_company=True,
		domain="[('child_ids', '!=', False), '|', ('company_id', '=', False), ('company_id', '=', company_id), '|', ('branch_id', '=', False), ('branch_id', '=', branch_id)]",
		default=_default_location_id, required=True, ondelete='cascade')
	location_out_id = fields.Many2one(
		'stock.location', 'Store to', check_company=True,
		domain="[('id', 'child_of', location_in_id), ('id', '!=', location_in_id), '|', ('company_id', '=', False), ('company_id', '=', company_id), '|', ('branch_id', '=', False), ('branch_id', '=', branch_id)]",
		required=True, ondelete='cascade')

	def _domain_product_id(self):
		domain = "[('type', '!=', 'service'), '|', ('company_id', '=', False), ('company_id', '=', company_id), '|', ('branch_id', '=', False), ('branch_id', '=', branch_id)]"
		if self.env.context.get('active_model') == 'product.template':
			return [('product_tmpl_id', '=', self.env.context.get('active_id'))]
		return domain

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Company is required with Branch.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Branch should belongs to the selected Company.'))

class StockMove(models.Model):
	_inherit = 'stock.move'

	branch_id = fields.Many2one('res.branch', 'Branch', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id, index=True)

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Company is required with Branch.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Branch should belongs to the selected Company.'))

class StockMoveLine(models.Model):
	_inherit = 'stock.move.line'

	branch_id = fields.Many2one('res.branch', 'Branch', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
	lot_id = fields.Many2one(
		'stock.production.lot', 'Lot/Serial Number',
		domain="[('product_id', '=', product_id), ('company_id', '=', company_id), ('branch_id', '=', branch_id)]", check_company=True)

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Company is required with Branch.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Branch should belongs to the selected Company.'))

	@api.model_create_multi
	def create(self, vals_list):
		for vals in vals_list:
			if vals.get('move_id'):
				vals['branch_id'] = self.env['stock.move'].browse(vals['move_id']).branch_id.id
			elif vals.get('picking_id'):
				vals['branch_id'] = self.env['stock.picking'].browse(vals['picking_id']).branch_id.id
		return super(StockMoveLine, self).create(vals_list)

class QuantPackage(models.Model):
	_inherit = "stock.quant.package"

	branch_id = fields.Many2one('res.branch', 'Branch', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

class StockRule(models.Model):
	_inherit = 'stock.rule'

	branch_id = fields.Many2one('res.branch', 'Branch', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id, index=True)

	@api.model
	def default_get(self, fields):
		res = super(StockRule, self).default_get(fields)
		if 'company_id' not in fields:
			res['branch_id'] = False
		return res

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Company is required with Branch.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Branch should belongs to the selected Company.'))

class StockScrap(models.Model):
	_inherit = 'stock.scrap'

	branch_id = fields.Many2one('res.branch', 'Branch', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id, index=True, states={'done': [('readonly', True)]})

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Company is required with Branch.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Branch should belongs to the selected Company.'))

class StockPackageLevel(models.Model):
	_inherit = 'stock.package_level'

	branch_id = fields.Many2one('res.branch', 'Branch', index=True)
	package_id = fields.Many2one(
		'stock.quant.package', 'Package', required=True, check_company=True,
		domain="[('location_id', 'child_of', parent.location_id), '|', ('company_id', '=', False), ('company_id', '=', company_id), '|', ('branch_id', '=', False), ('branch_id', '=', branch_id)]")
	location_dest_id = fields.Many2one(
		'stock.location', 'To', check_company=True,
		domain="[('id', 'child_of', parent.location_dest_id), '|', ('company_id', '=', False), ('company_id', '=', company_id), '|', ('branch_id', '=', False), ('branch_id', '=', branch_id)]")

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Company is required with Branch.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Branch should belongs to the selected Company.'))

class StockQuant(models.Model):
	_inherit = 'stock.quant'

	branch_id = fields.Many2one(related='location_id.branch_id', string='Branch', store=True, readonly=True)


class Location(models.Model):
	_inherit = "stock.location"

	@api.model
	def default_get(self, fields):
		res = super(Location, self).default_get(fields)
		if 'company_id' not in fields:
			res['branch_id'] = False
		return res

	branch_id = fields.Many2one('res.branch', 'Branch', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id, index=True, help='Let this field empty if this location is shared between branches')

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Company is required with Branch.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Branch should belongs to the selected Company.'))

class Route(models.Model):
	_inherit = "stock.location.route"

	@api.model
	def default_get(self, fields):
		res = super(Route, self).default_get(fields)
		if 'company_id' not in fields:
			res['branch_id'] = False

		return res

	branch_id = fields.Many2one('res.branch', 'Branch', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id, index=True, help='Leave this field empty if this route is shared between all branches')

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Company is required with Branch.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Branch should belongs to the selected Company.'))

	@api.onchange('branch_id')
	def _onchange_branch(self):
		if self.branch_id:
			self.warehouse_ids = self.warehouse_ids.filtered(lambda w: w.branch_id == self.branch_id)

class Picking(models.Model):
	_inherit = "stock.picking"

	branch_id = fields.Many2one('res.branch', 'Branch', related='picking_type_id.branch_id', readonly=True, store=True, index=True)

class PickingType(models.Model):
	_inherit = "stock.picking.type"

	@api.model
	def default_get(self, fields):
		res = super(PickingType, self).default_get(fields)
		if 'company_id' not in fields:
			res['branch_id'] = False

		return res

	branch_id = fields.Many2one('res.branch', 'Branch', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id, index=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Company is required with Branch.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Branch should belongs to the selected Company.'))

	@api.onchange('branch_id')
	def _onchange_branch_id(self):
		if self.branch_id:
			warehouse = self.env['stock.warehouse'].search([('branch_id', '=', self.branch_id.id)], limit=1)
			self.warehouse_id = warehouse
		else:
			self.warehouse_id = False

class ProductionLot(models.Model):
	_inherit = 'stock.production.lot'

	branch_id = fields.Many2one('res.branch', 'Branch', index=True)

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Company is required with Branch.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Branch should belongs to the selected Company.'))

class Warehouse(models.Model):
	_inherit = "stock.warehouse"

	@api.model
	def default_get(self, fields):
		res = super(Warehouse, self).default_get(fields)
		if 'company_id' not in fields:
			res['branch_id'] = False
		return res

	branch_id = fields.Many2one('res.branch', 'Branch', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id, index=True)

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Company is required with Branch.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Branch should belongs to the selected Company.'))

class Orderpoint(models.Model):
	_inherit = "stock.warehouse.orderpoint"

	branch_id = fields.Many2one('res.branch', 'Branch', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id, index=True)
	product_id = fields.Many2one('product.product', 'Product', domain="[('type', '=', 'product'), '|', ('company_id', '=', False), ('company_id', '=', company_id),'|', ('branch_id', '=', False), ('branch_id', '=', branch_id)]", ondelete='cascade', required=True, check_company=True)

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Company is required with Branch.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Branch should belongs to the selected Company.'))

	@api.onchange('branch_id')
	def _onchange_branch_id(self):
		if self.branch_id:
			self.warehouse_id = self.env['stock.warehouse'].search([('branch_id','=', self.branch_id.id)], limit=1)

class ProductReplenish(models.TransientModel):
	_inherit = 'product.replenish'

	branch_id = fields.Many2one('res.branch', 'Branch')
	route_ids = fields.Many2many('stock.location.route', string='Preferred Routes', help="Apply specific route(s) for the replenishment instead of product's default routes.", domain="['|', ('company_id', '=', False), ('company_id', '=', company_id),'|', ('branch_id', '=', False), ('branch_id', '=', branch_id)]")
	warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=True, domain="[('branch_id', '=', branch_id)]")

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Company is required with Branch.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Branch should belongs to the selected Company.'))

	@api.model
	def default_get(self, fields):
		res = super(ProductReplenish, self).default_get(fields)
		if 'branch_id' in fields:
			branch = product_tmpl_id.branch_id or self.env.branch
			res['branch_id'] = branch.id
			warehouse = self.env['stock.warehouse'].search([('company_id', '=', company.id),('branch_id', '=', branch.id)], limit=1)
			res['warehouse_id'] = warehouse.id

class ReturnPicking(models.TransientModel):
	_inherit = 'stock.return.picking'

	branch_id = fields.Many2one(related='picking_id.branch_id')

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Company is required with Branch.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Branch should belongs to the selected Company.'))

class ProductTemplate(models.Model):
	_inherit = 'product.template'

	branch_id = fields.Many2one('res.branch', 'Branch', index=1, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Company is required with Branch.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Branch should belongs to the selected Company.'))

class SupplierInfo(models.Model):
	_inherit = "product.supplierinfo"

	branch_id = fields.Many2one('res.branch', 'Branch', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id, index=1, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

class ProductPackaging(models.Model):
	_inherit = "product.packaging"

	branch_id = fields.Many2one('res.branch', 'Branch', index=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
