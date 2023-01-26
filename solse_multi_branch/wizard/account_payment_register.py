# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from collections import defaultdict
from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, frozendict
import logging
_logging = logging.getLogger(__name__)

class AccountPaymentRegister(models.TransientModel):
	_inherit = 'account.payment.register'

	branch_id = fields.Many2one('res.branch', 'Sucursal', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id)

	@api.model
	def _get_batch_journal(self, batch_result):
		""" Helper to compute the journal based on the batch.

		:param batch_result:    A batch returned by '_get_batches'.
		:return:                An account.journal record.
		"""
		payment_values = batch_result['payment_values']
		foreign_currency_id = payment_values['currency_id']
		partner_bank_id = payment_values['partner_bank_id']

		currency_domain = [('currency_id', '=', foreign_currency_id)]
		partner_bank_domain = [('bank_account_id', '=', partner_bank_id)]

		default_domain = [
			('type', 'in', ('bank', 'cash')),
			('company_id', '=', batch_result['lines'].company_id.id),
			('branch_id', 'in', [batch_result['lines'].branch_id.id, False]),
		]

		if partner_bank_id:
			extra_domains = (
				currency_domain + partner_bank_domain,
				partner_bank_domain,
				currency_domain,
				[],
			)
		else:
			extra_domains = (
				currency_domain,
				[],
			)

		for extra_domain in extra_domains:
			journal = self.env['account.journal'].search(default_domain + extra_domain, limit=1)
			if journal:
				return journal

		return self.env['account.journal']

	@api.depends('available_journal_ids')
	def _compute_journal_id(self):
		for wizard in self:
			if wizard.can_edit_wizard:
				batch = wizard._get_batches()[0]
				wizard.journal_id = wizard._get_batch_journal(batch)
			else:
				wizard.journal_id = self.env['account.journal'].search([
					('type', 'in', ('bank', 'cash')),
					('company_id', '=', wizard.company_id.id),
					('branch_id', 'in', [wizard.branch_id.id, False]),
				], limit=1)