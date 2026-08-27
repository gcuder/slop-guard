import { RuleTester } from "oxlint/plugins-dev";

import { noLongParameterListRule } from "./no-long-parameter-list.ts";

const tester = new RuleTester({ languageOptions: { parserOptions: { lang: "ts" } } });
const error = { messageId: "longParameterList" };

tester.run("slop-guard-smells/no-long-parameter-list", noLongParameterListRule, {
	valid: [
		"function load(first, second, third, fourth) {}",
		{ code: "function load(a, b, c, d, e, f) {}", options: [{ maxParameters: 8 }] },
	],
	invalid: [
		{ code: "function load(first, second, third, fourth, fifth) {}", errors: [error] },
		{ code: "const load = (a, b, c, d, e) => a;", errors: [error] },
	],
});
