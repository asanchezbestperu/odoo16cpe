odoo.define('solse_multibranch_pos.TicketScreen', function(require) {
	'use strict';

	const TicketScreen = require('point_of_sale.TicketScreen');
	const Registries = require('point_of_sale.Registries');
	const { Order } = require('point_of_sale.models');
	const session = require('web.session');
	const core = require('web.core');
	const rpc = require('web.rpc');
	const _t = core._t;
	const QWeb = core.qweb;

	const TicketScreenReport = TicketScreen =>
		class extends TicketScreen {
			async _fetchSyncedOrders() {
				const domain = this._computeSyncedOrdersDomain();
				let domain_suc = ['branch_id','in',[this.env.pos.config.branch_id[0], false]];
				domain.push(domain_suc)
				const limit = this._state.syncedOrders.nPerPage;
				const offset = (this._state.syncedOrders.currentPage - 1) * this._state.syncedOrders.nPerPage;
				let { ids, totalCount } = await this.rpc({
					model: 'pos.order',
					method: 'search_paid_order_ids',
					kwargs: { config_id: this.env.pos.config.id, domain, limit, offset },
					context: this.env.session.user_context,
				});
				const idsNotInCache = ids.filter((id) => !(id in this._state.syncedOrders.cache));
				//const idsNotInCache = ids
				if (idsNotInCache.length > 0) {
					let fetchedOrders = await this.rpc({
						model: 'pos.order',
						method: 'export_for_ui',
						args: [idsNotInCache],
						context: this.env.session.user_context,
					});
					await this.env.pos._loadMissingProducts(fetchedOrders);
	                await this.env.pos._loadMissingPartners(fetchedOrders);
	                // Cache these fetched orders so that next time, no need to fetch
	                // them again, unless invalidated. See `_onInvoiceOrder`.
	                fetchedOrders.forEach((order) => {
	                    this._state.syncedOrders.cache[order.id] = Order.create({}, { pos: this.env.pos, json: order });
	                });
				}
				this._state.syncedOrders.totalCount = totalCount;
				this._state.syncedOrders.toShow = ids.map((id) => this._state.syncedOrders.cache[id]);
			}
		}

	Registries.Component.extend(TicketScreen, TicketScreenReport);

	return TicketScreen;
})