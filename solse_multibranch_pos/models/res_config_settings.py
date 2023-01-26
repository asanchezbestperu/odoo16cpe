# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	branch_id = fields.Many2one('res.branch', string='Sucursal', related="pos_config_id.branch_id", readonly=False)
	branch_nombre = fields.Char(string="Nombre Sucursal", related="pos_config_id.branch_nombre", readonly=False)
	branch_direccion = fields.Char(string="Dirección Sucursal", related="pos_config_id.branch_direccion", readonly=False)
	branch_telefono = fields.Char(string="Telefono Sucursal", related="pos_config_id.branch_telefono", readonly=False)
