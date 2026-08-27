import { RuleTester } from "oxlint/plugins-dev";

import { noPrimitiveObsessionRule } from "./no-primitive-obsession.ts";

const tester = new RuleTester({ languageOptions: { parserOptions: { lang: "ts" } } });
const error = { messageId: "primitiveObsession" };

tester.run("slop-guard-smells/no-primitive-obsession", noPrimitiveObsessionRule, {
	valid: [
		"function load(name: string, age: number, active: boolean) {}",
		"function load(street: Street, city: City, code: PostalCode) {}",
	],
	invalid: [{ code: "function load(street: string, city: string, code: string) {}", errors: [error] }],
});
