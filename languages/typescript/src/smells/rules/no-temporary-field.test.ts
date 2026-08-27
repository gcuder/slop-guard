import { RuleTester } from "oxlint/plugins-dev";

import { noTemporaryFieldRule } from "./no-temporary-field.ts";

const tester = new RuleTester({ languageOptions: { parserOptions: { lang: "ts" } } });
const error = { messageId: "temporaryField" };

tester.run("slop-guard-smells/no-temporary-field", noTemporaryFieldRule, {
	valid: [
		"class Store { rows = []; load() { this.rows = [1]; } }",
		"class Store { constructor() { this.rows = []; } load() { this.rows = [1]; } }",
	],
	invalid: [
		{ code: "class Store { constructor() { this.rows = []; } load() { this.cache = {}; } }", errors: [error] },
	],
});
