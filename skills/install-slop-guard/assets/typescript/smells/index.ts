import { eslintCompatPlugin } from "@oxlint/plugins";

import { noCommentedOutCodeRule } from "./rules/no-commented-out-code.ts";
import { noDataClassRule } from "./rules/no-data-class.ts";
import { noDataClumpsRule } from "./rules/no-data-clumps.ts";
import { noDuplicateCodeRule } from "./rules/no-duplicate-code.ts";
import { noFeatureEnvyRule } from "./rules/no-feature-envy.ts";
import { noInappropriateIntimacyRule } from "./rules/no-inappropriate-intimacy.ts";
import { noLargeClassRule } from "./rules/no-large-class.ts";
import { noLazyClassRule } from "./rules/no-lazy-class.ts";
import { noLongMethodRule } from "./rules/no-long-method.ts";
import { noLongParameterListRule } from "./rules/no-long-parameter-list.ts";
import { noMessageChainsRule } from "./rules/no-message-chains.ts";
import { noMiddleManRule } from "./rules/no-middle-man.ts";
import { noPrimitiveObsessionRule } from "./rules/no-primitive-obsession.ts";
import { noRefusedBequestRule } from "./rules/no-refused-bequest.ts";
import { noTemporaryFieldRule } from "./rules/no-temporary-field.ts";
import { noTypeCodeSwitchRule } from "./rules/no-type-code-switch.ts";
import { noUnreachableCodeRule } from "./rules/no-unreachable-code.ts";
import { noUnusedParameterRule } from "./rules/no-unused-parameter.ts";

/** Opt-in Oxlint rules for the code smells catalogued at refactoring.guru. */
const slopGuardSmellsPlugin = eslintCompatPlugin({
	meta: { name: "slop-guard-smells" },
	rules: {
		"no-commented-out-code": noCommentedOutCodeRule,
		"no-data-class": noDataClassRule,
		"no-data-clumps": noDataClumpsRule,
		"no-duplicate-code": noDuplicateCodeRule,
		"no-feature-envy": noFeatureEnvyRule,
		"no-inappropriate-intimacy": noInappropriateIntimacyRule,
		"no-large-class": noLargeClassRule,
		"no-lazy-class": noLazyClassRule,
		"no-long-method": noLongMethodRule,
		"no-long-parameter-list": noLongParameterListRule,
		"no-message-chains": noMessageChainsRule,
		"no-middle-man": noMiddleManRule,
		"no-primitive-obsession": noPrimitiveObsessionRule,
		"no-refused-bequest": noRefusedBequestRule,
		"no-temporary-field": noTemporaryFieldRule,
		"no-type-code-switch": noTypeCodeSwitchRule,
		"no-unreachable-code": noUnreachableCodeRule,
		"no-unused-parameter": noUnusedParameterRule,
	},
});

export default slopGuardSmellsPlugin;
