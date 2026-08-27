import { RuleTester } from "oxlint/plugins-dev";

import { noInappropriateIntimacyRule } from "./no-inappropriate-intimacy.ts";

const tester = new RuleTester({ languageOptions: { parserOptions: { lang: "ts" } } });
const error = { messageId: "inappropriateIntimacy" };

tester.run("slop-guard-smells/no-inappropriate-intimacy", noInappropriateIntimacyRule, {
	valid: [
		"const value = store.rows;",
		"class Store { load() { return this._rows; } }",
		"class Store { #rows = []; copy(other: Store) { return other.#rows; } }",
	],
	invalid: [
		{ code: "const value = store._rows;", errors: [error] },
		{ code: "class Store { copy(other) { return other._rows; } }", errors: [error] },
	],
});
