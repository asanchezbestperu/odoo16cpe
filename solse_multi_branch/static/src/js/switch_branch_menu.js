/** @odoo-module */

import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
import { symmetricalDifference } from "@web/core/utils/arrays";

import { Component, useState } from "@odoo/owl";

import { session } from "@web/session";
import { url } from "@web/core/utils/urls";
import { patch } from "@web/core/utils/patch";

const {setCookie} = require('web.utils.cookies');

class SwitchBranchMenu extends Component {
	setup() {
		this.branchService = useService("branch");
		this.companyService = useService("company");
		this.currentBranch = this.branchService.currentBranch;
		this.state = useState({ branchsToToggle: [] });
	}

	setBranchs(main_branch_id, branch_ids) {
		var hash = $.bbq.getState()
		if(branch_ids) {
			hash.bids = branch_ids.sort(function(a, b) {
				if (a === main_branch_id) {
					return -1;
				} else if (b === main_branch_id) {
					return 1;
				} else {
					return a - b;
				}
			}).join(',');
		} else {
			hash.bids = ''+main_branch_id+'';
		}
		
		setCookie('bids', hash.bids || String(main_branch_id), 24 * 60 * 60 * 365, 'required');
		$.bbq.pushState({'bids': hash.bids}, 0);
		//this.branchService.setBranchs("loginto", main_branch_id);
	}
	switch_branch(brh_id, branch_name) {
		var self = this;
		session.user_branches.current_branch[0] = brh_id;
		session.user_branches.current_branch[1] = branch_name;
		$('.o_switch_branch_menu .oe_topbar_name').text(session.user_branches.current_branch[1]);
		session.user_context.allowed_branch_ids = [brh_id];
		this.allowed_branch_ids = String(session.user_context.allowed_branch_ids)
									.split(',')
									.map(function (id) {return parseInt(id);});
		this.user_branches = session.user_branches.allowed_branches;
		this.current_branch = brh_id;
		this.current_branch_name = _.find(session.user_branches.allowed_branches, function (branch) {
			return branch.id === self.current_branch;
		}).name;
		this.setBranchs(brh_id, this.allowed_branch_ids);
	}

	//Cuando realizo click en la sucursal
	logIntoBranch(branchId, branchName, company_id) {
		browser.clearTimeout(this.toggleTimer);
		var allowed_branch_ids = this.allowed_branch_ids;
		let pertenece = false;
		var datos = this.companyService.allowedCompanyIds;
		if(datos) {
			var cadena = String(datos);
			var allowed_company_ids = cadena.split(',') .map(function (id) {return parseInt(id);});
			for(let indice = 0; indice < allowed_company_ids.length; indice ++) {
				let id_empresa = allowed_company_ids[indice]
				if(id_empresa == company_id) {
					pertenece = true
				}
			}
		} else {
			pertenece = true
		}
		
		if(pertenece == false) { 
			allowed_branch_ids = [branchId];
		}

		this.switch_branch(branchId, branchName);

		//this.branchService.setBranchs("loginto", branchId);
		//this.setBranchs(branchId, allowed_branch_ids);
		if(pertenece == false) {            
			this.switchBranchCompany(company_id);
		}
		location.reload();
	}
	//Acitvo o desactivo una sucursal
	toggleBranch(branchId, company_id) {
		this.state.branchsToToggle = symmetricalDifference(this.state.branchsToToggle, [
			branchId,
		]);
		browser.clearTimeout(this.toggleTimer);
		this.toggleTimer = browser.setTimeout(() => {
			this.branchService.setBranchs("toggle", ...this.state.branchsToToggle);
		}, this.constructor.toggleDelay);

		var allowed_branch_ids = this.branchService.allowedBranchIds;
		var hash = $.bbq.getState()
		var allowed_company_ids = hash.cids
		let pertenece = false;
		if(allowed_company_ids) {
			var current_branch_id = allowed_branch_ids[0];
			for(let indice = 0; indice < allowed_company_ids.length; indice ++) {
				let id_empresa = allowed_company_ids[indice]
				if(id_empresa == company_id) {
					pertenece = true
				}
			}
		} else {
			pertenece = false;
		}
		
		if(pertenece == false) { 
			allowed_branch_ids = [branchId];
			current_branch_id = branchId;
		} else {
			allowed_branch_ids.push(branchId)
		}
		if(pertenece == false) {            
			this.switchBranchCompany(company_id);
		}
	}

	switchBranchCompany(cmpID){
		var self = this;
		session.user_companies.current_company = cmpID;
		// set company name
		var company_name = '';

		for(let reg in session.user_companies.allowed_companies) {
			if (reg.id == cmpID) {
				company_name = reg.name;
				break;
			}
		}
		$('.o_switch_company_menu .oe_topbar_name').text(session.user_companies.allowed_companies[cmpID].name);
		session.user_context.allowed_company_ids = [cmpID];
		this.allowed_company_ids = String(session.user_context.allowed_company_ids).split(',').map(function (id) {
			return parseInt(id);
		});
		this.user_companies = session.user_companies.allowed_companies;
		this.current_company = cmpID;
		this.current_company_name = company_name
		//session_local.setCompanies(cmpID, this.env.services.company.allowedCompanyIds);
		var hash = $.bbq.getState()
		hash.cids = this.allowed_company_ids.sort(function(a, b) {
			if (a === cmpID) {
				return -1;
			} else if (b === cmpID) {
				return 1;
			} else {
				return a - b;
			}
		}).join(',');
		setCookie('cids', hash.cids || String(cmpID));
		$.bbq.pushState({'cids': hash.cids}, 0);
		//location.reload();
		//this.companyService.setCompanies("loginto", cmpID);
	}

	get selectedBranchs() {
		return symmetricalDifference(
			this.branchService.allowedBranchIds,
			this.state.branchsToToggle
		);
	}
}
SwitchBranchMenu.template = "solse_multi_branch.SwitchBranchMenu";
SwitchBranchMenu.components = { Dropdown, DropdownItem };
SwitchBranchMenu.toggleDelay = 1000;

const systrayItem = {
	Component: SwitchBranchMenu,
	isDisplayed(env) {
		const { availableBranchs } = env.services.branch;
		return Object.keys(availableBranchs).length > 1;
	},
};

registry.category("systray").add("SwitchBranchMenu", systrayItem, {
	force: true, sequence: 2
});