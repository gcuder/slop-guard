import { defineRule } from "@oxlint/plugins";
import type { ESTree } from "@oxlint/plugins";

import { numberOption, thresholdSchema } from "../shared/options.ts";

const DEFAULT_MAX_PARAMETERS = 4;

type ParameterOwner =
	| ESTree.ArrowFunctionExpression
	| ESTree.Function
	| ESTree.TSMethodSignature;

/** Ban parameter lists long enough that callers must count positions. */
export const noLongParameterListRule = defineRule({
	meta: {
		type: "problem",
		docs: {
			description:
				"Disallow more than `maxParameters` parameters; values that travel together belong in one object.",
		},
		messages: {
			longParameterList:
				"This function takes {{count}} parameters, past the {{limit}} this project allows. Callers have to get every position right, and the list grows with every new case. Pass the group that travels together as one object.",
		},
		...thresholdSchema({ maxParameters: DEFAULT_MAX_PARAMETERS }),
	},
	createOnce(context) {
		const check = (node: ParameterOwner) => {
			const limit = numberOption(context.options, "maxParameters", DEFAULT_MAX_PARAMETERS);
			if (node.params.length <= limit) return;
			context.report({
				node,
				messageId: "longParameterList",
				data: { count: String(node.params.length), limit: String(limit) },
			});
		};

		return {
			ArrowFunctionExpression: check,
			FunctionDeclaration: check,
			FunctionExpression: check,
			TSDeclareFunction: check,
			TSMethodSignature: check,
		};
	},
});
