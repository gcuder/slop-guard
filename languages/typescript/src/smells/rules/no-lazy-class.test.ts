import { RuleTester } from "oxlint/plugins-dev";

import { noLazyClassRule } from "./no-lazy-class.ts";

const tester = new RuleTester({ languageOptions: { parserOptions: { lang: "ts" } } });
const error = { messageId: "lazyClass" };

tester.run("slop-guard-smells/no-lazy-class", noLazyClassRule, {
	valid: [
		"class Store { rows = []; load() { return this.rows; } }",
		"class Store { load() { return 1; } save() { return 2; } }",
		"class Store extends Base { load() { return 1; } }",
	],
	invalid: [{ code: "class Formatter { render(row) { return String(row); } }", errors: [error] }],
});
