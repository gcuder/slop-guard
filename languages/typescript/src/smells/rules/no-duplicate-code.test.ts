import { RuleTester } from "oxlint/plugins-dev";

import { noDuplicateCodeRule } from "./no-duplicate-code.ts";

const tester = new RuleTester({ languageOptions: { parserOptions: { lang: "ts" } } });
const error = { messageId: "duplicateCode" };

tester.run("slop-guard-smells/no-duplicate-code", noDuplicateCodeRule, {
	valid: [
		"function first() { a(); b(); c(); } function second() { a(); b(); d(); }",
		"function first() { a(); } function second() { a(); }",
	],
	invalid: [
		{ code: "function first() { a(); b(); c(); } function second() { a(); b(); c(); }", errors: [error] },
	],
});
