import { RuleTester } from "oxlint/plugins-dev";

import { noMiddleManRule } from "./no-middle-man.ts";

const tester = new RuleTester({ languageOptions: { parserOptions: { lang: "ts" } } });
const error = { messageId: "middleMan" };

tester.run("slop-guard-smells/no-middle-man", noMiddleManRule, {
	valid: [
		"class Store { load() { return this.rows; } save(row) { this.rows.push(row); return row; } }",
		"class Store { load() { return this.inner.load(); } }",
	],
	invalid: [
		{
			code: "class Store { load() { return this.inner.load(); } save(row) { return this.inner.save(row); } }",
			errors: [error],
		},
	],
});
