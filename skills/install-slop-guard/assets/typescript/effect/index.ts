import { eslintCompatPlugin } from "@oxlint/plugins";

import { noServiceConstructorImportsRule } from "./rules/no-service-constructor-imports.ts";

/** Opt-in Oxlint rules for Effect service and Layer architecture. */
const slopGuardEffectPlugin = eslintCompatPlugin({
	meta: { name: "slop-guard-effect" },
	rules: {
		"no-service-constructor-imports": noServiceConstructorImportsRule,
	},
});

export default slopGuardEffectPlugin;
