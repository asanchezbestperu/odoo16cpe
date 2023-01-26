/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { symmetricalDifference } from "@web/core/utils/arrays";
import { session } from "@web/session";

function parseBranchIds(cidsFromHash) {
	const bids = [];
	if (typeof cidsFromHash === "string") {
		bids.push(...cidsFromHash.split(",").map(Number));
	} else if (typeof cidsFromHash === "number") {
		bids.push(cidsFromHash);
	}
	return bids;
}

function computeAllowedBranchIds(bids) {
	const { user_branches } = session;
	let allowedBranchIds = bids || [];
	const availableBranchsFromSession = user_branches.allowed_branches;
	const notReallyAllowedBranchs = allowedBranchIds.filter(
		(id) => !(id in availableBranchsFromSession)
	);

	if (!allowedBranchIds.length || notReallyAllowedBranchs.length) {
		allowedBranchIds = [user_branches.current_branch[0]];
	}
	return allowedBranchIds;
}

/*function computeAllowedCompanyIds(cids) {
	const { user_companies } = session;
	let allowedCompanyIds = cids || [];
	const availableCompaniesFromSession = user_companies.allowed_companies;
	const notReallyAllowedCompanies = allowedCompanyIds.filter(
		(id) => !(id in availableCompaniesFromSession)
	);

	if (!allowedCompanyIds.length || notReallyAllowedCompanies.length) {
		allowedCompanyIds = [user_companies.current_company];
	}
	return allowedCompanyIds;
}*/

export const branchService = {
	dependencies: ["user", "router", "cookie"],
	start(env, { user, router, cookie }) {
		let bids;
		if ("bids" in router.current.hash) {
			bids = parseBranchIds(router.current.hash.bids);
		} else if ("bids" in cookie.current) {
			bids = parseBranchIds(cookie.current.bids);
		}
		let allowedBranchIds = computeAllowedBranchIds(bids);

		const stringBIds = allowedBranchIds.join(",");
		router.replaceState({ bids: stringBIds }, { lock: true });
		cookie.setCookie("bids", stringBIds);
		user.updateContext({ allowed_branch_ids: allowedBranchIds });
		const availableBranchs = session.user_branches.allowed_branches;

		return {
			availableBranchs,
			get allowedBranchIds() {
				return allowedBranchIds.slice();
			},
			get currentBranch() {
				return availableBranchs[allowedBranchIds[0]];
			},
			setBranchs(mode, ...branchIds) {
				// compute next company ids
				let nextBranchIds;
				if (mode === "toggle") {
					nextBranchIds = symmetricalDifference(allowedBranchIds, branchIds);
				} else if (mode === "loginto") {
					const branchId = branchIds[0];
					if (allowedBranchIds.length === 1) {
						// 1 enabled company: stay in single company mode
						nextBranchIds = [branchId];
					} else {
						// multi company mode
						nextBranchIds = [
							branchId,
							...allowedBranchIds.filter((id) => id !== branchId),
						];
					}
				}
				nextBranchIds = nextBranchIds.length ? nextBranchIds : [branchIds[0]];
				// apply them
				router.pushState({ bids: nextBranchIds }, { lock: true });
				cookie.setCookie("bids", nextBranchIds);
				browser.setTimeout(() => browser.location.reload()); // history.pushState is a little async
			},
		};
	},
};
registry.category("services").add("branch", branchService);