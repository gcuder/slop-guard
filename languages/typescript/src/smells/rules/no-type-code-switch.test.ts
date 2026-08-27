import { RuleTester } from "oxlint/plugins-dev";

import { noTypeCodeSwitchRule } from "./no-type-code-switch.ts";

const tester = new RuleTester({ languageOptions: { parserOptions: { lang: "ts" } } });
const error = { messageId: "typeCodeSwitch" };

tester.run("slop-guard-smells/no-type-code-switch", noTypeCodeSwitchRule, {
	valid: [
		"if (kind === 'a') { first(); } else if (kind === 'b') { second(); }",
		"switch (kind) { case 'a': first(); break; default: other(); }",
	],
	invalid: [
		{
			code: "if (kind === 'a') { first(); } else if (kind === 'b') { second(); } else if (kind === 'c') { third(); }",
			errors: [error],
		},
		{
			code: "switch (kind) { case 'a': first(); break; case 'b': second(); break; case 'c': third(); break; }",
			errors: [error],
		},
	],
});
