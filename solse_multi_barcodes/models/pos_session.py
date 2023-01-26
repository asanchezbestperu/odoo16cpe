# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)
	
class PosSession(models.Model):
	_inherit = 'pos.session'

	def _loader_params_product_product(self):
		res = super(PosSession, self)._loader_params_product_product()
		res['search_params']['fields'].extend(["product_multi_barcodes", "datos_str_barcodes"])
		return res