import { RuleTester } from "oxlint/plugins-dev";

import { noLargeClassRule } from "./no-large-class.ts";

const tester = new RuleTester({ languageOptions: { parserOptions: { lang: "ts" } } });
const methods = Array.from({ length: 12 }, (_, index) => `step${index}() { return ${index}; }`).join(" ");
const fields = Array.from({ length: 12 }, (_, index) => `field${index} = ${index};`).join(" ");

tester.run("slop-guard-smells/no-large-class", noLargeClassRule, {
	valid: ["class Store { load() { return 1; } }"],
	invalid: [
		{ code: `class Store { ${methods} }`, errors: [{ messageId: "manyMethods" }] },
		{
			code: `class Store { ${fields} }`,
			options: [{ maxFields: 5 }],
			errors: [{ messageId: "manyFields" }],
		},
	],
});
