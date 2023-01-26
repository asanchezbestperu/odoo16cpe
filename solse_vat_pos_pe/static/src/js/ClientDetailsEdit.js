odoo.define('solse_vat_pos_pe.PartnerDetailsEdit', function(require) {
	'use strict';

	const PartnerDetailsEdit = require('point_of_sale.PartnerDetailsEdit');
	const Registries = require('point_of_sale.Registries');
	const session = require('web.session');
	const core = require('web.core');
	const _t = core._t;
	const rpc = require('web.rpc');
	const QWeb = core.qweb;
	const { onMounted } = owl;

	const PartnerDetailsEditVat = (PartnerDetailsEdit_) =>
		class extends PartnerDetailsEdit_ {
			setup() {
				super.setup();

				onMounted(() => {
	                this.iniciarDatos_vat_pe();
	            });
			}
			constructor() {
				super(...arguments);
				//this.intFields = ['country_id', 'state_id', 'property_product_pricelist'];
				this.departamento = null;
				this.provincia = null;
				this.distrito = null;
				this.intFields = ['country_id', 'state_id', 'city_id', 'l10n_pe_district', 'zip', 'property_product_pricelist', 'l10n_latam_identification_type_id'];
				const partner = this.props.partner;
				this.changes = {
					'country_id': partner.country_id && partner.country_id[0],
					'state_id': partner.state_id && partner.state_id[0],
					'city_id': partner.city_id && partner.city_id[0],
					'l10n_pe_district': partner.l10n_pe_district && partner.l10n_pe_district[0],
					'l10n_latam_identification_type_id': partner.l10n_latam_identification_type_id && partner.l10n_latam_identification_type_id[0],
				};
			}
			iniciarDatos_vat_pe(){
				var self = this;
				//---
				$('.consulta-datos').off('click', '');
				$('.consulta-datos').on('click', self._consultarDatos.bind(self));
				
				let partner = this.props.partner;
				self.departamento = partner.state_id || [];
				self.provincia = partner.city_id || [];
				self.distrito = partner.l10n_pe_district || [];
				//---
				var contents = $('.partner-details');
				if (contents.find("[name='doc_type']").val()==6){
					contents.find('.partner-state').show();
					contents.find('.partner-condition').show();
				}
				else {
					contents.find('.partner-state').hide();
					contents.find('.partner-condition').hide();
				}
				contents.find('.doc_number').on('change',function(event){
					var doc_type = contents.find("[name='l10n_latam_identification_type_id']").val();
					doc_type = self.env.pos.doc_code_by_id[doc_type];
					var doc_number = this.value;
					contents.find("[name='vat']").val(doc_number);
					self.changes['doc_number'] = doc_number;
					self.changes['vat'] = doc_number;
				});
				contents.find("[name='l10n_latam_identification_type_id']").on('change',function(event){
					var doc_type = self.env.pos.doc_code_by_id[this.value];
					var doc_number = contents.find(".doc_number").val();
					if (doc_type=="6"){
						contents.find('.partner-state').show();
						contents.find('.partner-condition').show();
					}
					else{
						contents.find('.partner-state').hide();
						contents.find('.partner-condition').hide();
					}
					self.changes['doc_number'] = doc_number;
					self.changes['vat'] = doc_number;
					self.changes['l10n_latam_identification_type_id'] = this.value;
				});
				//---
				$('.client-address-country').off('change', '');
				$('.client-address-country').on('change', self._changeCountry.bind(self));
				$('.client-address-states').off('change', '');
				$('.client-address-states').on('change', self._changeDepartamento.bind(self));
				$('#city_id').off('change', '');
				$('#city_id').on('change', self._onChangeProvincia.bind(self));
				self._changeCountry();
			}
			_consultarDatos() {
				var self = this;
				if (!$(".client-address-type").val() || !$(".doc_number").val()) {
					return;
				}

				let div = $(".client-address-type")[0];
				let tipo_doc = '';
				for (let i = 0; i < div.options.length; i ++){
					if(div.options[i].selected){
						tipo_doc = div.options[i].text;
					}
				}
				if(tipo_doc != 'DNI' && tipo_doc !='RUC'){
					return;
				}
				let parametros = [tipo_doc == "DNI" ? "dni" : "ruc", $(".doc_number").val()]
				let contents = $('.partner-details');
				rpc.query({
					model: 'res.partner',
					method: 'consulta_datos',
					args: parametros,
				}).then(function (datos) {
					if (datos.error) {
						self.showPopup('ErrorTracebackPopup', {
							'title': 'Alerta!',
							'body': datos.message,
						});
					} else if (datos.data) {
						if(!datos.data.success) {
							self.showPopup('ErrorTracebackPopup', {
								'title': 'Alerta!',
								'body': datos.data.message,
							});
							return;
						}
						var respuesta = datos.data.data;
						self.changes['vat'] = $(".doc_number").val();
						if (tipo_doc === 'DNI') {
							contents.find('input[name="name"]').val(respuesta.names);
							contents.find('input[name="zip"]').val(respuesta.district_code)
							contents.find('input[name="street"]').val(respuesta.direccion)


							self.departamento = [respuesta.department_id, "Departamento"]
							self.provincia = [respuesta.province_id, "Provincia"]
							self.distrito = [respuesta.district_id, "Distrito"]
							let div = $(".client-address-country")[0];
							for (let i = 0; i < div.options.length; i ++){
								if(div.options[i].text == 'Perú'){
									div.options[i].selected = 1;
								}
							}
							self.changes['country_id'] = contents.find('select[name="country_id"]').val();
							self.changes['state_id'] = respuesta.department_id;
							self.changes['city_id'] = respuesta.province_id;
							self.changes['l10n_pe_district'] = respuesta.district_id;
							self.changes['name'] = respuesta.names;
							self.changes['zip'] = respuesta.district_code;
							self.changes['street'] = respuesta.direccion;
							self._changeCountry();
						
						} else if (tipo_doc === 'RUC') {
							contents.find('input[name="name"]').val(respuesta.razonSocial);
							contents.find('input[name="zip"]').val(respuesta.district_code);
							contents.find('input[name="street"]').val(respuesta.direccion);

							self.departamento = [respuesta.department_id, "Departamento"]
							self.provincia = [respuesta.province_id, "Provincia"]
							self.distrito = [respuesta.district_id, "Distrito"]

							let div = $(".client-address-country")[0];
							for (let i = 0; i < div.options.length; i ++){
								if(div.options[i].text == 'Perú'){
									div.options[i].selected = 1;
								}
							}
							self.changes['country_id'] = contents.find('select[name="country_id"]').val();
							self.changes['state_id'] = respuesta.department_id;
							self.changes['city_id'] = respuesta.province_id;
							self.changes['l10n_pe_district'] = respuesta.district_id;
							self.changes['name'] = respuesta.razonSocial;
							self.changes['zip'] = respuesta.district_code;
							self.changes['street'] = respuesta.direccion;
							self._changeCountry();
						}
					}



					// placeholder phone_code
					//$("input[name='phone']").attr('placeholder', data.phone_code !== 0 ? '+'+ data.phone_code : '');

					
					/*var selectStates = $("select[name='state_id']");
					if (selectStates.data('init')===0 || selectStates.find('option').length===1) {
						if (data.length) {
							selectStates.html('');
							_.each(data, function (x) {
							  let seleccion = x[0] == self.departamento[0] ? ' selected="1" ' : '';
								var opt = $('<option '+seleccion+'>').text(x[1])
									.attr('value', x[0])
									.attr('data-code', x[2]);
								selectStates.append(opt);
							});
							selectStates.parent('div').show();
						} else {
							selectStates.val('').parent('div').hide();
						}
						selectStates.data('init', 0);
					} else {
						selectStates.data('init', 0);
					}
					self._changeDepartamento();
					if (data.fields) {
						if ($.inArray('zip', data.fields) > $.inArray('city', data.fields)){
							$(".div_zip").before($(".div_city"));
						} else {
							$(".div_zip").after($(".div_city"));
						}
						var all_fields = ["street", "zip", "city", "country_name"]; // "state_code"];
						_.each(all_fields, function (field) {
							$(".checkout_autoformat .div_" + field.split('_')[0]).toggle($.inArray(field, data.fields)>=0);
						});
					}*/
				});
			}
			_changeCountry() {
				var self = this;
				if (!$(".client-address-country").val()) {
					return;
				}
				let div = $(".client-address-country")[0];
				if(div.options[div.selectedIndex].text == 'Perú'){
				  $('.div_provincia').show();
				  $('.div_distrito').show();
				  self._changeDepartamento();
				  self._onChangeProvincia();
				} else {
				  $('.div_provincia').hide();
				  $('.div_distrito').hide();
				}
				rpc.query({
					model: 'res.country',
					method: 'get_pos_sale_departamentos',
					args: [{"id": $(".client-address-country").val()}],
				}).then(function (data) {
					// placeholder phone_code
					//$("input[name='phone']").attr('placeholder', data.phone_code !== 0 ? '+'+ data.phone_code : '');

					// populate states and display
					var selectStates = $("select[name='state_id']");
					// dont reload state at first loading (done in qweb)
					if (selectStates.data('init')===0 || selectStates.find('option').length===1) {
						if (data.length) {
							selectStates.html('');
							_.each(data, function (x) {
							  let seleccion = x[0] == self.departamento[0] ? ' selected="1" ' : '';
								var opt = $('<option '+seleccion+'>').text(x[1])
									.attr('value', x[0])
									.attr('data-code', x[2]);
								selectStates.append(opt);
							});
							selectStates.parent('div').show();
						} else {
							selectStates.val('').parent('div').hide();
						}
						selectStates.data('init', 0);
					} else {
						selectStates.data('init', 0);
					}
					self._changeDepartamento();
					// manage fields order / visibility
					if (data.fields) {
						if ($.inArray('zip', data.fields) > $.inArray('city', data.fields)){
							$(".div_zip").before($(".div_city"));
						} else {
							$(".div_zip").after($(".div_city"));
						}
						var all_fields = ["street", "zip", "city", "country_name"]; // "state_code"];
						_.each(all_fields, function (field) {
							$(".checkout_autoformat .div_" + field.split('_')[0]).toggle($.inArray(field, data.fields)>=0);
						});
					}
				});
			}
			_changeDepartamento() {
				var self = this;
				if (!$(".client-address-states").val()) {
					return;
				}
				rpc.query({
					model: 'res.country.state',
					method: 'get_pos_sale_privincias',
					args: [{"id": $(".client-address-states").val()}],
				}).then(function (data) {
				  var selectStates = $("select[name='city_id']");
				  if (selectStates.data('init')===0 || selectStates.find('option').length===1) {
					  if (data.length) {
						  selectStates.html('');
						  var contador = 0;
						  _.each(data, function (x) {
							  let seleccion = x[0] == self.provincia[0] ? ' selected="1" ' : '';
							  if(x[0] == self.provincia[0] || (!self.provincia[0] && contador == 0)) {
								self.changes['city_id'] = x[0];
							  }
							  contador = contador + 1;

							  var opt = $('<option '+seleccion+'>').text(x[1])
								  .attr('value', x[0])
								  .attr('data-code', x[2]);
							  selectStates.append(opt);
						  });
						  selectStates.parent('div').show();
					  } else {
						  selectStates.val('').parent('div').hide();
					  }
					  selectStates.data('init', 0);
				  } else {
					  selectStates.data('init', 0);
				  }
				  self._changeProvincia();
				});
			}
			_onChangeDepartamento(ev) {
				if (!$('.checkout_autoformat').length) {
					return;
				}
				this._changeDepartamento();
				this._onChangeProvincia();
			}
			_changeProvincia() {
				var self = this;
				if (!$("#city_id").val()) {
				  return;
				}
				let div = $("#city_id")[0];
				$("#city").val(div.options[div.selectedIndex].text);
					rpc.query({
					model: 'res.city',
					method: 'get_pos_sale_distritos',
					args: [{"id": $("#city_id").val()}],
				}).then(function (data) {
				  var selectStates = $("select[name='l10n_pe_district']");
				  if (selectStates.data('init')===0 || selectStates.find('option').length===1) {
					  if (data.length) {
						  selectStates.html('');
						  var contador_distritos = 0;
						  _.each(data, function (x) {
							let seleccion = x[0] == self.distrito[0] ? ' selected="1" ' : '';
							if(x[0] == self.distrito[0] || (!self.distrito[0] && contador_distritos == 0)) {
								self.changes['l10n_pe_district'] = x[0];
								self.changes['zip'] = x[2];
								$("input[name='zip']").val(x[2])
							  }
							  contador_distritos = contador_distritos + 1;

							  var opt = $('<option '+seleccion+'>').text(x[1])
								  .attr('value', x[0])
								  .attr('data-code', x[2]);
							  selectStates.append(opt);
						  });
						  selectStates.parent('div').show();
					  } else {
						  selectStates.val('').parent('div').hide();
					  }
					  selectStates.data('init', 0);
					} else {
						selectStates.data('init', 0);
					}
				});
			}
			_onChangeProvincia(ev) {
				/*if (!this.$('.checkout_autoformat').length) {
					return;
				}*/
				this._changeProvincia();
			}
		};

	Registries.Component.extend(PartnerDetailsEdit, PartnerDetailsEditVat);

	return PartnerDetailsEdit;
});
