# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import api, fields, models, tools, _
import base64
import os
import re
from odoo.exceptions import ValidationError, UserError

class Company(models.Model):
	_inherit = "res.company"

	def crear_sucursal(self):
		nombre = "%s%s-%s" % ("E", str(self.id), "Principal")
		datos_sucursal = {
			'name': nombre,
			'company_id': self.id,
		}
		self.env['res.branch'].create(datos_sucursal)

	@api.model
	def create(self, values):
		empresa = super(Company, self).create(values)
		empresa.crear_sucursal()
		return empresa