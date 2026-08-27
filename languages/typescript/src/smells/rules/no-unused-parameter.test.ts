import { RuleTester } from "oxlint/plugins-dev";

import { noUnusedParameterRule } from "./no-unused-parameter.ts";

const tester = new RuleTester({ languageOptions: { parserOptions: { lang: "ts" } } });
const error = { messageId: "unusedParameter" };

tester.run("slop-guard-smells/no-unused-parameter", noUnusedParameterRule, {
	valid: [
		"function load(key) { return rows[key]; }",
		"function load(_key) { return rows; }",
		"function load(key) {}",
	],
	invalid: [{ code: "function load(key, cache) { return rows[key]; }", errors: [error] }],
});
