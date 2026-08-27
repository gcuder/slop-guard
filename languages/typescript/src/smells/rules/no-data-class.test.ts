import { RuleTester } from "oxlint/plugins-dev";

import { noDataClassRule } from "./no-data-class.ts";

const tester = new RuleTester({ languageOptions: { parserOptions: { lang: "ts" } } });
const error = { messageId: "dataClass" };

tester.run("slop-guard-smells/no-data-class", noDataClassRule, {
	valid: [
		"class Row { value = 1; total() { return this.value * 2; } }",
		"class Row { value = 1; }",
	],
	invalid: [
		{
			code: "class Row { value = 1; getValue() { return this.value; } setValue(next) { this.value = next; } }",
			errors: [error],
		},
	],
});
