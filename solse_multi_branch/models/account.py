# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
import logging
_logging = logging.getLogger(__name__)

TYPE2JOURNAL = {
	'out_invoice':'sale', 
	'in_invoice':'purchase',  
	'out_refund':'sale', 
	'in_refund':'purchase'
}

class AccountMove(models.Model):
	_inherit = "account.move"

	#branch_id = fields.Many2one('res.branch', related="journal_id.branch_id", string='Sucursal')
	branch_id = fields.Many2one('res.branch', string='Sucursal', compute="_compute_branch", store=True, readonly=False)
	pe_branch_code = fields.Char("Codigo Sucursal", related="branch_id.code", store=True)
	auto_branch = fields.Boolean(string="Auto sucursal", help="asignar sucursal segun cambio de diario")

	def _compute_branch(self):
		for reg in self:
			branch_id = self.env.branch.id or self.env.company.default_branch_id.id 

	def obtener_datos_entidad_emisora(self):
		invoice_id = self
		comercial_name = False
		if invoice_id.branch_id:
			comercial_name = invoice_id.branch_id.name.strip()

		if comercial_name == '' and invoice_id.company_id.partner_id:
			comercial_name = invoice_id.company_id.partner_id.commercial_name.strip()
		datos = {
			'comercial_name':  comercial_name or '-',
			'legal_name': invoice_id.company_id.partner_id.legal_name.strip() or '-',
			'pe_branch_code': invoice_id.pe_branch_code or '0000',
		}
		if invoice_id.branch_id.city_id:
			datos['province_id'] = invoice_id.branch_id.city_id.name.strip()
		else:
			datos['province_id'] = invoice_id.company_id.partner_id.city_id.name.strip()

		if invoice_id.branch_id.state_id:
			datos['state_id'] = invoice_id.branch_id.state_id.name
		else:
			datos['state_id'] = invoice_id.company_id.partner_id.state_id.name

		if invoice_id.branch_id.l10n_pe_district:
			datos['district_id'] = invoice_id.branch_id.l10n_pe_district.name
			datos['ubigeo'] = invoice_id.branch_id.l10n_pe_district.code
		else:
			datos['district_id'] = invoice_id.company_id.partner_id.l10n_pe_district.name
			datos['ubigeo'] = invoice_id.company_id.partner_id.l10n_pe_district.code

		if invoice_id.branch_id.street:
			datos['street_id'] = invoice_id.branch_id.street
		else:
			datos['street_id'] = invoice_id.company_id.partner_id.street

		if invoice_id.branch_id.country_id:
			datos['country_code'] = invoice_id.branch_id.country_id.code
		else:
			datos['country_code'] = invoice_id.company_id.partner_id.country_id.code
		return datos

	@api.onchange('journal_id', 'auto_branch')
	def _onchange_diario(self):
		if self.auto_branch and self.journal_id.branch_id:
			self.branch_id = self.journal_id.branch_id.id
			
	@api.depends('l10n_latam_available_document_type_ids', 'debit_origin_id')
	def _compute_l10n_latam_document_type(self):
		for rec in self.filtered(lambda x: x.state == 'draft'):
			document_types = rec.l10n_latam_available_document_type_ids._origin
			invoice_type = rec.move_type
			if invoice_type in ['out_refund', 'in_refund']:
				document_types = document_types.filtered(lambda x: x.internal_type not in ['debit_note', 'invoice'])
			elif invoice_type in ['out_invoice', 'in_invoice']:
				document_types = document_types.filtered(lambda x: x.internal_type not in ['credit_note'])
			if rec.debit_origin_id:
				document_types = document_types.filtered(lambda x: x.internal_type == 'debit_note')
			
			l10n_latam_document_type_id = False
			for reg in document_types:
				if reg.branch_id.id == rec.branch_id.id:
					l10n_latam_document_type_id = document_types and document_types[0]

			if not l10n_latam_document_type_id:
				rec.l10n_latam_document_type_id = False
			else:
				rec.l10n_latam_document_type_id = l10n_latam_document_type_id.id

	@api.constrains('move_type', 'l10n_latam_document_type_id')
	def _check_invoice_type_document_type(self):
		#self._compute_l10n_latam_document_type()
		#self._onchange_partner_id()
		for rec in self.filtered('l10n_latam_document_type_id.internal_type'):
			internal_type = rec.l10n_latam_document_type_id.internal_type
			invoice_type = rec.move_type
			if internal_type in ['debit_note', 'invoice'] and invoice_type in ['out_refund', 'in_refund']:
				raise ValidationError(_('You can not use a %s document type with a refund invoice', internal_type))
			elif internal_type == 'credit_note' and invoice_type in ['out_invoice', 'in_invoice']:
				raise ValidationError(_('You can not use a %s document type with a invoice', internal_type))


	def _get_l10n_latam_documents_domain(self):
		self.ensure_one()
		if self.move_type in ['out_refund', 'in_refund']:
			internal_types = ['credit_note']
		else:
			internal_types = ['invoice', 'debit_note']
		
		if self.branch_id:
			return [('internal_type', 'in', internal_types), ('country_id', '=', self.company_id.country_id.id), ('company_id', '=', self.company_id.id), ('branch_id', '=', self.branch_id.id)]
		else:
			return [('internal_type', 'in', internal_types), ('country_id', '=', self.company_id.country_id.id), ('company_id', '=', self.company_id.id)]

	@api.depends('journal_id', 'partner_id', 'company_id', 'move_type')
	def _compute_l10n_latam_available_document_types(self):
		self.l10n_latam_available_document_type_ids = False
		for rec in self.filtered(lambda x: x.journal_id and x.l10n_latam_use_documents and x.partner_id):
			dominio = rec._get_l10n_latam_documents_domain()
			rec.l10n_latam_available_document_type_ids = self.env['l10n_latam.document.type'].search(dominio)

	@api.onchange('partner_id', 'company_id', 'branch_id')
	def _onchange_partner_id(self):
		self.ensure_one()
		res = super(AccountMove, self)._onchange_partner_id()
		if not self.move_type or self.move_type not in TYPE2JOURNAL:
			return

		if not self.branch_id:
			return
			
		journal_type = TYPE2JOURNAL[self.move_type]
		tipo_documento = self.env['l10n_latam.document.type']

		if self.move_type in ['out_refund', 'in_refund']:
			return res

		partner_id = self.partner_id.parent_id or self.partner_id
		doc_type = partner_id.doc_type
		tipo_doc_id = False
		if not doc_type:
			return res
		if doc_type in '6':
			if not self.env.context.get('is_pos_invoice'):
				if self.l10n_latam_document_type_id.code != '01' or self.l10n_latam_document_type_id.branch_id.id != self.branch_id.id:
					tipo_doc_id = tipo_documento.search([('code', '=', '01'), ('sub_type', '=', journal_type), ('branch_id', '=', self.branch_id.id)], limit=1)
					if tipo_doc_id:
						self.l10n_latam_document_type_id = tipo_doc_id.id
						return res
		if doc_type in ('6', ):
			tipo_doc_id = tipo_documento.search([('code', '=', '01'), ('sub_type', '=', journal_type), ('branch_id', '=', self.branch_id.id)], limit=1)
		else:
			if self.l10n_latam_document_type_id.code != '03' or self.l10n_latam_document_type_id.branch_id.id != self.branch_id.id:
				tipo_doc_id = tipo_documento.search([('code', '=', '03'), ('sub_type', '=', journal_type), ('branch_id', '=', self.branch_id.id)], limit=1)
		
		if tipo_doc_id:
			self.l10n_latam_document_type_id = tipo_doc_id.id
		return res

	
class AccountMoveLine(models.Model):
	_inherit = "account.move.line"

	branch_id = fields.Many2one(related='move_id.branch_id', store=True, readonly=True)

class AccountJournalGroup(models.Model):
	_inherit = 'account.journal.group'

	branch_id = fields.Many2one('res.branch', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id)

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Comapny is required with Sucursal.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Sucursal should belongs to the selected Company.'))

class AccountJournal(models.Model):
	_inherit = "account.journal"

	branch_id = fields.Many2one('res.branch', string='Sucursal', index=True, default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id, help="Sucursal related to this journal")

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Comapny is required with Sucursal.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Sucursal should belongs to the selected Company.'))

class account_payment(models.Model):
	_inherit = "account.payment"

	branch_id = fields.Many2one('res.branch', related='journal_id.branch_id', string='Sucursal', readonly=True)

class AccountPaymentTerm(models.Model):
	_inherit = "account.payment.term"

	branch_id = fields.Many2one('res.branch', string='Sucursal')

class AccountBankStatement(models.Model):
	_inherit = "account.bank.statement"

	branch_id = fields.Many2one('res.branch', related='journal_id.branch_id', string='Sucursal', store=True, readonly=True, default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id)

class AccountBankStatementLine(models.Model):
	_inherit = "account.bank.statement.line"

	branch_id = fields.Many2one('res.branch', related='statement_id.branch_id', string='Sucursal', store=True, readonly=True)


"""
class AccountAccount(models.Model):
	_inherit = "account.account"

	branch_id = fields.Many2one('res.branch', string='Sucursal', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id)

class AccountRoot(models.Model):
	_inherit = 'account.root'

	branch_id = fields.Many2one('res.branch')

	def init(self):
		tools.drop_view_if_exists(self.env.cr, self._table)
		self.env.cr.execute('''
			CREATE OR REPLACE VIEW %s AS (
			SELECT DISTINCT ASCII(code) * 1000 + ASCII(SUBSTRING(code,2,1)) AS id,
				   LEFT(code,2) AS name,
				   ASCII(code) AS parent_id,
				   company_id,
				   branch_id
			FROM account_account WHERE code IS NOT NULL
			UNION ALL
			SELECT DISTINCT ASCII(code) AS id,
				   LEFT(code,1) AS name,
				   NULL::int AS parent_id,
				   company_id,
				   branch_id
			FROM account_account WHERE code IS NOT NULL
			)''' % (self._table,)
		)
"""

class AccountTax(models.Model):
	_inherit = 'account.tax'

	branch_id = fields.Many2one('res.branch', string='Sucursal', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id)

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Comapny is required with Sucursal.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Sucursal should belongs to the selected Company.'))

class AccountTaxRepartitionLine(models.Model):
	_inherit = "account.tax.repartition.line"

	branch_id = fields.Many2one(string="Sucursal", comodel_name='res.branch', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id, help="The branch this repartition line belongs to.")

class AccountFiscalPosition(models.Model):
	_inherit = 'account.fiscal.position'

	branch_id = fields.Many2one('res.branch', string='Sucursal', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id)

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Comapny is required with Sucursal.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Sucursal should belongs to the selected Company.'))


class AccountReconcileModel(models.Model):
	_inherit = 'account.reconcile.model'

	branch_id = fields.Many2one('res.branch', string='Sucursal', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id)

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Comapny is required with Sucursal.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Sucursal should belongs to the selected Company.'))

class AccountInvoiceReport(models.Model):
	_inherit = "account.invoice.report"

	branch_id = fields.Many2one('res.branch', string='Sucursal', readonly=True)

	def _select(self):
		return super(AccountInvoiceReport, self)._select() + ", move.branch_id as branch_id"

	def _group_by(self):
		return super(AccountInvoiceReport, self)._group_by() + ", move.branch_id"

class L10nLatamDocumentType(models.Model):
	_inherit = 'l10n_latam.document.type'

	branch_id = fields.Many2one('res.branch', string='Sucursal', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id)

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Comapny is required with Sucursal.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Sucursal should belongs to the selected Company.'))
