# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AccountMove(models.Model):
	_inherit = 'account.move'

	branch_id = fields.Many2one('res.branch', 'Sucursal', index=1, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError('Factura: Se requiere compañía con Sucursal.')
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError('Factura: Sucursal %s debe pertenecer a la Empresa seleccionada (%s)' % (obj.branch_id.name, obj.company_id.name))
