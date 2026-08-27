import { RuleTester } from "oxlint/plugins-dev";

import { noDataClumpsRule } from "./no-data-clumps.ts";

const tester = new RuleTester({ languageOptions: { parserOptions: { lang: "ts" } } });
const error = { messageId: "dataClump" };

tester.run("slop-guard-smells/no-data-clumps", noDataClumpsRule, {
	valid: [
		"function save(street, city, code) {} function load(key) {}",
		"function save(street, city) {} function load(street, city) {}",
	],
	invalid: [
		{ code: "function save(street, city, code) {} function load(street, city, code) {}", errors: [error] },
	],
});
