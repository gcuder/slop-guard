import { RuleTester } from "oxlint/plugins-dev";

import { noFeatureEnvyRule } from "./no-feature-envy.ts";

const tester = new RuleTester({ languageOptions: { parserOptions: { lang: "ts" } } });
const error = { messageId: "featureEnvy" };

tester.run("slop-guard-smells/no-feature-envy", noFeatureEnvyRule, {
	valid: [
		"class Report { total(order) { return this.rate * order.amount; } }",
		"class Report { total() { return this.a + this.b + this.c; } }",
	],
	invalid: [
		{
			code: "class Report { total(order) { return order.amount + order.tax + order.shipping + order.discount + order.fee; } }",
			errors: [error],
		},
		{
			code: "class Report { total(order) { return order.amount + order.tax; } }",
			options: [{ minAccesses: 2 }],
			errors: [error],
		},
	],
});
