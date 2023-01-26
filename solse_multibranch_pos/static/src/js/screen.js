odoo.define('solse_multibranch_pos.pos_screens', function(require) {
	"use strict";

	var { PosGlobalState, Order } = require('point_of_sale.models');
	var PosDB = require('point_of_sale.DB');
	var core    = require('web.core');
	var rpc = require('web.rpc');
	var concurrency = require('web.concurrency');
	const Registries = require('point_of_sale.Registries');
	var QWeb = core.qweb;
	var PosDBSuper = PosDB;
	var Mutex = concurrency.Mutex;
	var _t      = core._t;
	var json_ordens = {}

	const PosModelBranch = (PosGlobalState) => class PosModelBranch extends PosGlobalState {
		async _addProducts(ids, setAvailable=true){
			let branch_id = this.pos.config.branch_id[0];
			if(setAvailable){
				await this.env.services.rpc({
					model: 'product.product',
					method: 'write',
					args: [ids, {'available_in_pos': true, 'branch_id': branch_id}],
					context: this.env.session.user_context,
				});
			}
			let product = await this.env.services.rpc({
				model: 'pos.session',
				method: 'get_pos_ui_product_product_by_params',
				args: [odoo.pos_session_id, {domain: [['id', 'in', ids]]}],
			});
			this._loadProductProduct(product);
		}

	}
	Registries.Model.extend(PosGlobalState, PosModelBranch);

	const BranchOrder = (Order) => class BranchOrder extends Order {

		constructor(obj, options) {
			super(...arguments);
			this.branch_id = this.branch_id || this.pos.config.branch_id[0];
			this.branch_nombre = this.branch_nombre || this.pos.config.branch_nombre;
			this.branch_direccion = this.branch_direccion || this.pos.config.branch_direccion;
			this.branch_telefono = this.branch_telefono || this.pos.config.branch_telefono;
		}

		init_from_JSON(json) {
			const res = super.init_from_JSON(...arguments);
			var self = this;
			self.branch_id = json.branch_id || false;
			self.branch_nombre = json.branch_nombre || false;
			self.branch_direccion = json.branch_direccion || false;
			self.branch_telefono = json.branch_telefono || false;
		}

		export_as_JSON() {
			var res = super.export_as_JSON(...arguments);
			res['branch_id']= this.branch_id || this.pos.config.branch_id[0];
			res['branch_nombre']= this.branch_nombre || this.pos.config.branch_nombre;
			res['branch_direccion']= this.branch_direccion || this.pos.config.branch_direccion;
			res['branch_telefono']= this.branch_telefono || this.pos.config.branch_telefono;
			return res;
		}

		export_for_printing() {
			var res = super.export_for_printing(...arguments);
			var self = this;
			res['branch_id'] = self.branch_id || self.pos.config.branch_id[0];
			res['branch_nombre']= self.branch_nombre || self.pos.config.branch_nombre;
			res['branch_direccion']= self.branch_direccion || self.pos.config.branch_direccion;
			res['branch_telefono']= self.branch_telefono || self.pos.config.branch_telefono;
			return res;
		}

	}
	Registries.Model.extend(Order, BranchOrder);

});