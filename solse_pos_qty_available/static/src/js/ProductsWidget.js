var ConsultarStockSearch = null;

odoo.define('solse_pos_qty_available.pos_product_list_view', function(require) {
"use strict";

	var core = require('web.core');
	var QWeb = core.qweb;
	var ProductsWidget = require('point_of_sale.ProductsWidget');
	const Registries = require('point_of_sale.Registries');
	var model = require('point_of_sale.models');
	var flag = false;
	var rpc = require('web.rpc');
	var PosModelSuper = model.PosModel;
	
	/*model.PosModel = model.PosModel.extend({
		initialize: function (session, attributes) {
			var res = PosModelSuper.prototype.initialize.apply(this, arguments);
			var self_ini = this;
			for (var i = 0; i < this.models.length; i++) {
				var model_temp = this.models[i];
				if (model_temp.model === "product.product") {
					model_temp.context = function(self){
						if(!self) {
							let ubicaciones = self_ini.stock_pick_typ;
							let ubicacion = false;
							let picking_type_id = self_ini.picking_type.id;
							let id_almacen = self_ini.picking_type.warehouse_id[0]
							let datos_contexto = { display_default_code: false, warehouse: id_almacen };
							return datos_contexto; 
						}
						let ubicaciones = self.stock_pick_typ;
						let ubicacion = false;
						let picking_type_id = self.picking_type.id;
						let id_almacen = self.picking_type.warehouse_id[0]
						let datos_contexto = { display_default_code: false, warehouse: id_almacen };
						return datos_contexto; 
					}
				}
			}

			return res;
		},
	});*/

	const ProductListView = (ProductsWidget) =>
		class extends ProductsWidget {
			constructor() {
				super(...arguments);
				this.consultarStock()
				ConsultarStockSearch = this.consultarStockSearch.bind(this);
			}

			obtenerListaProductoIds() {
				let producto_ids = []
				let lst_productos = this.env.pos.db.product_by_id
				for(let indice in lst_productos) {
					let producto = lst_productos[indice]
					if(!producto) {
						continue;
					}
					producto_ids.push(producto.id)
				}
				return producto_ids
			}
			consultarStockSearch() {
				let producto_ids = this.obtenerListaProductoIds()
				let self = this;
				let picking_type_id = self.env.pos.config.picking_type_id[0];
				this.rpc({
					model: 'product.product',
					method: 'get_location_qty_products',
					args: [picking_type_id, producto_ids],
				}).then(function(return_value) {
					let returned_values = return_value;
					$.each(returned_values, function( placeholder, product_details ){
						var product_id = self.env.pos.db.get_product_by_id(product_details.id);
						
						if (product_id) {
							product_id.location_qty_in_pos = product_details.location_qty_available;
						}
					});
					self.render();
				});
			}
			consultarStock(event) {
				let producto_ids = this.obtenerListaProductoIds()
				let self = this;
				let picking_type_id = self.env.pos.config.picking_type_id[0];
				this.rpc({
					model: 'product.product',
					method: 'get_location_qty_products',
					args: [picking_type_id, producto_ids],
				}).then(function(return_value) {
					let returned_values = return_value;
					$.each(returned_values, function( placeholder, product_details ){
						var product_id = self.env.pos.db.get_product_by_id(product_details.id);
						if (product_id) {
							product_id.location_qty_in_pos = product_details.location_qty_available;
						}
					});
					self.render();
				});
			}

			get productsToDisplay() {
				let list = [];
				if (this.searchWord !== '') {
					list = this.env.pos.db.search_product_in_category(
						this.selectedCategoryId,
						this.searchWord
					);
					
					setTimeout(function(){
						ConsultarStockSearch()
					}, 300)
				} else {
					list = this.env.pos.db.get_product_by_category(this.selectedCategoryId);
				}
				return list.sort(function (a, b) { return a.display_name.localeCompare(b.display_name) });
			}
			_updateSearch(event) {
				this.state.searchWord = event.detail;
			}

		}
	Registries.Component.extend(ProductsWidget, ProductListView);
	return ProductsWidget;
});

