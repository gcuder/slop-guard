import { defineRule } from "@oxlint/plugins";
import type { ESTree } from "@oxlint/plugins";

import { numberOption, thresholdSchema } from "../shared/options.ts";
import { statementCount } from "../shared/traversal.ts";

const DEFAULT_MAX_STATEMENTS = 20;

type FunctionNode = ESTree.ArrowFunctionExpression | ESTree.Function;

function functionName(node: FunctionNode): string {
	if (node.type !== "ArrowFunctionExpression" && node.id !== null && node.id !== undefined) {
		return node.id.name;
	}
	const parent = node.parent;
	if (parent?.type === "MethodDefinition" && parent.key.type === "Identifier") return parent.key.name;
	if (parent?.type === "VariableDeclarator" && parent.id.type === "Identifier") return parent.id.name;
	if (parent?.type === "PropertyDefinition" && parent.key.type === "Identifier") return parent.key.name;
	return "This function";
}

/** Ban functions that have grown past what one reader can hold at once. */
export const noLongMethodRule = defineRule({
	meta: {
		type: "problem",
		docs: {
			description:
				"Disallow functions longer than `maxStatements` statements; long functions hide the steps they are made of.",
		},
		messages: {
			longMethod:
				"`{{name}}` runs {{count}} statements, past the {{limit}} this project allows, so a reader has to hold all of it at once to change any of it. Pull the middle steps out into named functions.",
		},
		...thresholdSchema({ maxStatements: DEFAULT_MAX_STATEMENTS }),
	},
	createOnce(context) {
		const check = (node: FunctionNode) => {
			if (node.body === null || node.body === undefined || node.body.type !== "BlockStatement") return;
			const limit = numberOption(context.options, "maxStatements", DEFAULT_MAX_STATEMENTS);
			const count = statementCount(node.body, context.sourceCode.visitorKeys);
			if (count <= limit) return;
			context.report({
				node,
				messageId: "longMethod",
				data: { name: functionName(node), count: String(count), limit: String(limit) },
			});
		};

		return {
			ArrowFunctionExpression: check,
			FunctionDeclaration: check,
			FunctionExpression: check,
		};
	},
});
