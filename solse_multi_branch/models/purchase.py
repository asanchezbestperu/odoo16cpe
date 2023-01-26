# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class Purchase(models.Model):
	_inherit = "purchase.order"

	branch_id = fields.Many2one('res.branch', 'Sucursal', index=True, default=lambda self:  self.env.branch.id or self.env.company.default_branch_id.id, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

	@api.model
	def create(self, vals):
		if vals.get('name', _('New')) == _('New'):
			seq_date = None
			if 'date_order' in vals:
				seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
			
			secuencia = False
			if 'branch_id' in vals:
				dominio = [('branch_id','=', vals['branch_id']), ('para','=', 'compras')]
				secuencia = self.env['ir.sequence'].search(dominio)

			if secuencia:
				secuencia = secuencia[0].next_by_id()
			
			if not secuencia:
				secuencia = self.env['ir.sequence'].next_by_code('purchase.order', sequence_date=seq_date) or _('New')
			vals['name'] = secuencia

		res = super(Purchase, self).create(vals)
		return res

	@api.constrains('branch_id', 'order_line', 'company_id')
	def _check_order_line_branch_id(self):
		for order in self:
			if order.branch_id not in order.company_id.branch_ids:
				raise ValidationError(_('Sucursal should belongs to the selected Company.'))
			branches = order.order_line.product_id.branch_id
			if branches and branches != order.branch_id:
				bad_products = order.order_line.product_id.filtered(lambda p: p.branch_id and p.branch_id != order.branch_id)
				raise ValidationError((_("Your quotation contains products from branch %s whereas your quotation belongs to branch %s. \n Please change the branch of your quotation or remove the products from other branches (%s).") % (', '.join(branches.mapped('display_name')), order.branch_id.display_name, ', '.join(bad_products.mapped('display_name')))))

class PurchaseLine(models.Model):
	_inherit = 'purchase.order.line'

	branch_id = fields.Many2one(related='order_id.branch_id', string='Sucursal', store=True, readonly=True, index=True)

class PurchaseReport(models.Model):
	_inherit = "purchase.report"

	branch_id = fields.Many2one('res.branch', string='Sucursal', readonly=True)

	def _select(self):
		return super(PurchaseReport, self)._select() + ", po.branch_id as branch_id"

	def _group_by(self):
		return super(PurchaseReport, self)._group_by() + ", po.branch_id"