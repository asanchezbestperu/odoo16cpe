odoo.define('solse_multi_barcodes.models', function (require) {
  "use strict";

	var { PosGlobalState, Order, Orderline } = require('point_of_sale.models');
	var models = require('point_of_sale.models');
	const rpc = require('web.rpc');
	const Registries = require('point_of_sale.Registries');

	const MultiBarcoderOrderline = (Orderline) => class MultiBarcoderOrderline extends Orderline {
		constructor(obj, options) {
			super(...arguments);
			this.product_uom_id = options.product.uom_id;//options.json.product_uom_id || options.product.uom_id;
			if (options.json) {
				this.product_uom_id = options.json.product_uom_id;
			}
		}

		export_as_JSON(){
			const json = super.export_as_JSON(...arguments);
			json.product_uom_id = this.product_uom_id;
			return json;
		}

		init_from_JSON(json){
			super.init_from_JSON(...arguments);
			this.product_uom_id = json.product_uom_id
		}

		set_uom(uom_id){
			this.product_uom_id = uom_id;
			this.trigger('change',this);
		}

		get_unit() {
			if (this.product_uom_id){
				var unit_id = this.product_uom_id;
				if(!unit_id){
					return undefined;
				}
				unit_id = unit_id[0];
				if(!this.pos){
					return undefined;
				}
				return this.pos.units_by_id[unit_id];
			}
			return this.product.get_unit();
		}
	}
	Registries.Model.extend(Orderline, MultiBarcoderOrderline);

	const PosModelMultiBarcode = (PosGlobalState) => class PosModelMultiBarcode extends PosGlobalState {
		async _addProducts(ids){
			await this.rpc({
				model: 'product.product',
				method: 'write',
				args: [ids, {'available_in_pos': true}],
				context: this.session.user_context,
			});
			let product_model = _.find(this.models, (model) => model.model === 'product.product');
			let product = await this.rpc({
				model: 'product.product',
				method: 'read',
				args: [ids, product_model.fields],
				context: { ...this.session.user_context, ...product_model.context() },
			});
			product_model.loaded(this, product);
		}

		/*async _addProducts(ids, setAvailable=true){
			if(setAvailable){
				await this.env.services.rpc({
					model: 'product.product',
					method: 'write',
					args: [ids, {'available_in_pos': true}],
					context: this.env.session.user_context,
				});
			}
			let product = await this.env.services.rpc({
				model: 'pos.session',
				method: 'get_pos_ui_product_product_by_params',
				args: [odoo.pos_session_id, {domain: [['id', 'in', ids]]}],
			});
			this._loadProductProduct(product);
		}*/
	}
	Registries.Model.extend(PosGlobalState, PosModelMultiBarcode);

});