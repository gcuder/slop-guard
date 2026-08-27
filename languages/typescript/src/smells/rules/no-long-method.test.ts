import { RuleTester } from "oxlint/plugins-dev";

import { noLongMethodRule } from "./no-long-method.ts";

const tester = new RuleTester({ languageOptions: { parserOptions: { lang: "ts" } } });
const error = { messageId: "longMethod" };
const long = `function load() { ${Array.from({ length: 25 }, (_, index) => `step${index}();`).join(" ")} }`;
const short = "function load() { first(); second(); }";

tester.run("slop-guard-smells/no-long-method", noLongMethodRule, {
	valid: [short, { code: long, options: [{ maxStatements: 40 }] }],
	invalid: [
		{ code: long, errors: [error] },
		{ code: short, options: [{ maxStatements: 1 }], errors: [error] },
	],
});
