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

//const utils_local = require('web.utils');
export class SwitchCompanyMenuL extends Component {
	setup() {
		this.companyService = useService("company");
		this.branchService = useService("branch");
		this.currentCompany = this.companyService.currentCompany;
		this.state = useState({ companiesToToggle: [] });
	}

	setBranchs(main_branch_id, branch_ids) {
		var hash = $.bbq.getState()
		hash.bids = branch_ids.sort(function(a, b) {
			if (a === main_branch_id) {
				return -1;
			} else if (b === main_branch_id) {
				return 1;
			} else {
				return a - b;
			}
		}).join(',');
		setCookie('bids', hash.bids || String(main_branch_id), 24 * 60 * 60 * 365, 'required');
		$.bbq.pushState({'bids': hash.bids}, 0);
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
	}

	toggleCompany(companyId) {
		this.state.companiesToToggle = symmetricalDifference(this.state.companiesToToggle, [
			companyId,
		]);
		browser.clearTimeout(this.toggleTimer);
		this.toggleTimer = browser.setTimeout(() => {
			this.companyService.setCompanies("toggle", ...this.state.companiesToToggle);
		}, this.constructor.toggleDelay);

		var brh_id = this.get_curr_cmp_branch(companyId);
		if(brh_id){ 
			this.switch_company_branch(brh_id.id , brh_id.name); 
		}
	}

	get_curr_cmp_branch(cmpID) {
		for(let indice in session.user_branches.allowed_branches) {
			let registro = session.user_branches.allowed_branches[indice]
			if(registro.company_id == cmpID) {
				return registro
			}
		}
		return false;
	}

	switch_company_branch(brh_id, branch_name) {
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
		//this.branchService.setBranchs("loginto", brh_id);
	}

	logIntoCompany(companyId) {
		browser.clearTimeout(this.toggleTimer);
		var brh_id = this.get_curr_cmp_branch(companyId);
		if(brh_id){ 
			this.switch_company_branch(brh_id.id , brh_id.name); 
		}
		//this.companyService.setCompanies("loginto", companyId);
		this.switchBranchCompany(companyId);
		location.reload();
	}

	get selectedCompanies() {
		return symmetricalDifference(
			this.companyService.allowedCompanyIds,
			this.state.companiesToToggle
		);
	}
}
SwitchCompanyMenuL.template = "web.SwitchCompanyMenu";
SwitchCompanyMenuL.components = { Dropdown, DropdownItem };
SwitchCompanyMenuL.toggleDelay = 1000;


const systrayItemSwitchCompanyMenu = {
	Component: SwitchCompanyMenuL,
	isDisplayed(env) {
		const { availableCompanies } = env.services.company;
		return Object.keys(availableCompanies).length > 1;
	},
};

registry.category("systray").add("SwitchCompanyMenu", systrayItemSwitchCompanyMenu, {
	force: true, sequence: 1
});
	