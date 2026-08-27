import { RuleTester } from "oxlint/plugins-dev";

import { noUnreachableCodeRule } from "./no-unreachable-code.ts";

const tester = new RuleTester({ languageOptions: { parserOptions: { lang: "ts" } } });
const error = { messageId: "unreachableCode" };

tester.run("slop-guard-smells/no-unreachable-code", noUnreachableCodeRule, {
	valid: [
		"function load() { return 1; }",
		"function load() { if (ready) { return 1; } return 2; }",
	],
	invalid: [
		{ code: "function load() { return 1; log(); }", errors: [error] },
		{ code: "for (const row of rows) { break; log(); }", errors: [error] },
	],
});
