import { defineRule } from "@oxlint/plugins";
import type { ESTree } from "@oxlint/plugins";

import { numberOption, thresholdSchema } from "../shared/options.ts";

const DEFAULT_MIN_GROUP = 3;

type ParameterOwner = ESTree.ArrowFunctionExpression | ESTree.Function;

function parameterNames(node: ParameterOwner): string[] {
	return node.params
		.map((parameter) => (parameter.type === "Identifier" ? parameter.name : null))
		.filter((name): name is string => name !== null);
}

/** Ban the same group of parameters travelling between functions. */
export const noDataClumpsRule = defineRule({
	meta: {
		type: "problem",
		docs: {
			description:
				"Disallow the same group of `minGroup` parameter names appearing in more than one function; values that travel together belong to one type.",
		},
		messages: {
			dataClump:
				"This function and an earlier one both take {{names}}. Values that travel together belong to one thing; give them a type and pass that instead.",
		},
		...thresholdSchema({ minGroup: DEFAULT_MIN_GROUP }),
	},
	createOnce(context) {
		const seen = new Map<string, true>();

		const check = (node: ParameterOwner) => {
			const minimum = numberOption(context.options, "minGroup", DEFAULT_MIN_GROUP);
			const names = parameterNames(node);
			if (names.length < minimum) return;
			const key = [...names].sort().join(",");
			if (!seen.has(key)) {
				seen.set(key, true);
				return;
			}
			context.report({
				node,
				messageId: "dataClump",
				data: { names: [...names].sort().map((name) => `\`${name}\``).join(", ") },
			});
		};

		return {
			Program() {
				seen.clear();
			},
			ArrowFunctionExpression: check,
			FunctionDeclaration: check,
			FunctionExpression: check,
		};
	},
});
