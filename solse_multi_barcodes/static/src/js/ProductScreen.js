odoo.define('solse_multi_barcodes.ProductScreen', function(require) {
	'use strict';

	const ProductScreen = require('point_of_sale.ProductScreen');
	const Registries = require('point_of_sale.Registries');
	const session = require('web.session');
	const core = require('web.core');
	const NumberBuffer = require('point_of_sale.NumberBuffer');
	const rpc = require('web.rpc');
	const _t = core._t;
	const QWeb = core.qweb;

	const ProductScreenCPE = ProductScreen =>
		class extends ProductScreen {
			async _clickProduct(event) {
				if (!this.currentOrder) {
					this.env.pos.add_new_order();
				}
				const product = event.detail; 
				const uomList = [ { } ];
				if(product.product_multi_barcodes.length > 0) {
					
					let move_vals = {
						"product_id": product.id,
					}
					let datos_rpt = await rpc.query({
						model: 'multi.barcode.products',
						method: 'obtener_lista_codigos',
						args: [move_vals],
					})
					if (datos_rpt && datos_rpt.length > 1) {
						let contador = 0;
						for(let indice in datos_rpt) {
							let uomPrice = datos_rpt[indice];
							if(!uomPrice.uom_id) {
								continue;
							}
							uomList.push({
							   id:	uomPrice.id,
							   label:	uomPrice.uom_id[1],
							   isSelected: contador == 0 ? true : false ,
							   item:	uomPrice,
						   });
							contador ++
						}
						if (contador > 1) {
							const { confirmed, payload: selectedUOM } = await this.showPopup("SelectionPopup", {
							   title: 'Presentación',
							   list: uomList,
							});

							if (confirmed) {
								product.uom_id = selectedUOM.uom_id
								product.lst_price = selectedUOM.list_price
							} else {
								return
							}
						}
						
						
					}
				}
				const options = await this._getAddProductOptions(product);
				// Do not add product if options is undefined.
				if (!options) return;
				// Add the product after having the extra information.
				this.currentOrder.add_product(product, options);
				NumberBuffer.reset();
			}

			async _barcodeProductAction(code) {
				let product = this.env.pos.db.get_product_by_barcode(code.base_code);
				if (!product) {
					// find the barcode in the backend
					let foundProductIds = [];
					try {
						foundProductIds = await this.rpc({
							model: 'product.product',
							method: 'search',
							args: [[['barcode', '=', code.base_code]]],
							context: this.env.session.user_context,
						});
					} catch (error) {
						if (isConnectionError(error)) {
							return this.showPopup('OfflineErrorPopup', {
								title: this.env._t('Network Error'),
								body: this.env._t("Product is not loaded. Tried loading the product from the server but there is a network error."),
							});
						} else {
							throw error;
						}
					}
					if (foundProductIds.length) {
						await this.env.pos._addProducts(foundProductIds);
						// assume that the result is unique.
						product = this.env.pos.db.get_product_by_id(foundProductIds[0]);
					} else {
						return this._barcodeErrorAction(code);
					}
				}
				const options = await this._getAddProductOptions(product, code);
				// Do not proceed on adding the product when no options is returned.
				// This is consistent with _clickProduct.
				if (!options) return;

				// update the options depending on the type of the scanned code
				if (code.type === 'price') {
					Object.assign(options, {
						price: code.value,
						extras: {
							price_manually_set: true,
						},
					});
				} else if (code.type === 'weight') {
					Object.assign(options, {
						quantity: code.value,
						merge: false,
					});
				} else if (code.type === 'discount') {
					Object.assign(options, {
						discount: code.value,
						merge: false,
					});
				}
				if(product.product_multi_barcodes.length > 0) {
					product.barcode = code.base_code
					let move_vals = {
						"product_id": product.id,
						"barcode": product.barcode
					}
					let datos_rpt = await rpc.query({
						model: 'multi.barcode.products',
						method: 'obtener_datos',
						args: [move_vals],
					})
					datos_rpt = datos_rpt[0]
					product.uom_id = datos_rpt.uom_id
					product.lst_price = datos_rpt.list_price
				}
				
				this.currentOrder.add_product(product,  options)
			}
		};

	Registries.Component.extend(ProductScreen, ProductScreenCPE);

	return ProductScreen;
});
