import { RuleTester } from "oxlint/plugins-dev";

import { noMessageChainsRule } from "./no-message-chains.ts";

const tester = new RuleTester({ languageOptions: { parserOptions: { lang: "ts" } } });
const error = { messageId: "messageChain" };

tester.run("slop-guard-smells/no-message-chains", noMessageChainsRule, {
	valid: [
		"const value = order.customer.name;",
		"const value = this.rows.first;",
		{ code: "const value = order.a.b.c.d;", options: [{ maxLinks: 6 }] },
	],
	invalid: [
		{ code: "const value = order.customer.address.city.name;", errors: [error] },
		{ code: "const value = order.getCustomer().getAddress().getCity().name;", errors: [error] },
		{ code: "const value = this.order.customer.address.city;", errors: [error] },
	],
});
