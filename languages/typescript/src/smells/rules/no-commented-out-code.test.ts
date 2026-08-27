import { RuleTester } from "oxlint/plugins-dev";

import { noCommentedOutCodeRule } from "./no-commented-out-code.ts";

const tester = new RuleTester({ languageOptions: { parserOptions: { lang: "ts" } } });
const error = { messageId: "commentedOutCode" };

tester.run("slop-guard-smells/no-commented-out-code", noCommentedOutCodeRule, {
	valid: [
		"// Load the rows the caller asked for.\nconst rows = load();",
		"// TODO: const rows = loadAll();\nconst rows = load();",
		"/* The parser owns this contract. */\nconst rows = load();",
	],
	invalid: [
		{ code: "// const rows = loadAll();\nconst rows = load();", errors: [error] },
		{ code: "function load() {\n// return cached();\nreturn fresh();\n}", errors: [error] },
	],
});
