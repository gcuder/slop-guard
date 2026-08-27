import { RuleTester } from "oxlint/plugins-dev";

import { noRefusedBequestRule } from "./no-refused-bequest.ts";

const tester = new RuleTester({ languageOptions: { parserOptions: { lang: "ts" } } });
const error = { messageId: "refusedBequest" };

tester.run("slop-guard-smells/no-refused-bequest", noRefusedBequestRule, {
	valid: [
		"class Square extends Shape { area() { return this.side ** 2; } }",
		"class Shape { area() { throw new Error('not implemented'); } }",
	],
	invalid: [
		{ code: "class Square extends Shape { rotate() { throw new Error('unsupported'); } }", errors: [error] },
	],
});
