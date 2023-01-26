# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
import logging
_logging = logging.getLogger(__name__)

class SaleOrder(models.Model):
	_inherit = "sale.order"

	"""warehouse_id = fields.Many2one(
		'stock.warehouse', string='Almacen',
		required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
		default=_default_warehouse_id, check_company=True)"""

	@api.model
	def default_get(self,fields):
		res = super(SaleOrder, self).default_get(fields)
		branch_id = warehouse_id = False
		branch_id = self.env.branch.id or self.env.company.default_branch_id.id
		if branch_id:
			branched_warehouse = self.env['stock.warehouse'].search([('branch_id','=',branch_id)])
			if branched_warehouse:
				warehouse_id = branched_warehouse.ids[0]
		else:
			warehouse_id = self._default_warehouse_id()
			warehouse_id = warehouse_id.id

		res.update({
			'branch_id' : branch_id,
			'warehouse_id' : warehouse_id
		})

		return res

	@api.onchange('branch_id')
	def _onchange_branch_id(self):
		if not self.branch_id:
			return
		branched_warehouse = self.env['stock.warehouse'].search([('branch_id','=', self.branch_id.id)], limit=1)
		if branched_warehouse:
			self.warehouse_id = branched_warehouse.id

	#branch_id = fields.Many2one('res.branch', string="Branch")

	
	def _prepare_invoice(self):
		res = super(SaleOrder, self)._prepare_invoice()
		res['branch_id'] = self.branch_id.id
		return res
