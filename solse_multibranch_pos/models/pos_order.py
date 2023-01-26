# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging
_logging = logging.getLogger(__name__)

class PosOrder(models.Model):
	_inherit = 'pos.order'

	branch_id = fields.Many2one('res.branch', 'Sucursal', index=1, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
	branch_nombre = fields.Char("Nombre Sucursal")
	branch_direccion = fields.Char("Dirección Sucursal")
	branch_telefono = fields.Char("Telefono Sucursal")

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError('Orden POS: Se requiere compañía con Sucursal.')
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError('Orden POS: Sucursal %s debe pertenecer a la Empresa seleccionada (%s)' % (obj.branch_id.name, obj.company_id.name))

	@api.model
	def _order_fields(self, ui_order):
		res = super(PosOrder, self)._order_fields(ui_order)
		sucursal =  self.env['pos.session'].browse(ui_order['pos_session_id']).config_id.branch_id
		if sucursal:
			res['branch_nombre'] = sucursal.name
			res['branch_direccion'] = sucursal.street
			res['branch_telefono'] = sucursal.phone
			res['branch_id'] = sucursal.id
		return res

	def _prepare_invoice_vals(self):
		res = super(PosOrder, self)._prepare_invoice_vals()
		#res['branch_id'] = self.branch_id.id
		res.update({"branch_id": self.branch_id.id})
		res['pe_branch_code'] = self.branch_id.code or "0000"
		return res

	def obtener_direccion(self):
		if self.branch_id:
			return self.branch_id.street
		else:
			return self.company_id.street_name

	def obtener_telefono(self):
		if self.branch_id:
			return self.branch_id.street
		else:
			return self.company_id.street_name

	def obtener_local(self):
		if self.branch_id:
			return self.branch_id.name
		else:
			return "Principal"

	def _export_for_ui(self, order):
		_logging.info("inicio _export_for_ui solse_multibranch_pos")
		res = super(PosOrder, self)._export_for_ui(order)
		res["branch_id"] = order.branch_id.id
		res["branch_nombre"] = order.branch_nombre
		res["branch_direccion"] = order.branch_direccion
		res["branch_telefono"] = order.branch_telefono
		_logging.info("fin _export_for_ui solse_multibranch_pos")
		return res

	def export_for_ui(self):
		return self.mapped(self._export_for_ui) if self else []