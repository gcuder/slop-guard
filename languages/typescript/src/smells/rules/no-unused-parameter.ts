import { defineRule } from "@oxlint/plugins";
import type { ESTree } from "@oxlint/plugins";

import { walk } from "../shared/traversal.ts";

type FunctionNode = ESTree.ArrowFunctionExpression | ESTree.Function;

function declaredNames(parameter: ESTree.ParamPattern): string[] {
	if (parameter.type === "Identifier") return [parameter.name];
	if (parameter.type === "TSParameterProperty") return declaredNames(parameter.parameter);
	if (parameter.type === "AssignmentPattern" && parameter.left.type === "Identifier") {
		return [parameter.left.name];
	}
	return [];
}

/** Ban parameters the body never reads. */
export const noUnusedParameterRule = defineRule({
	meta: {
		type: "problem",
		docs: {
			description:
				"Disallow parameters the body never reads; a name prefixed with an underscore is exempt.",
		},
		messages: {
			unusedParameter:
				"This function takes `{{name}}` and never reads it, so the argument every caller passes does nothing. Remove it, or prefix the name with an underscore when an interface forces the signature.",
		},
	},
	createOnce(context) {
		const check = (node: FunctionNode) => {
			const body = node.body;
			if (body === null || body === undefined || body.type !== "BlockStatement") return;
			if (body.body.length === 0) return;
			const used = new Set<string>();
			walk(body, context.sourceCode.visitorKeys, (child) => {
				if (child.type !== "Identifier") return;
				const parent = child.parent;
				const isPropertyName =
					parent?.type === "MemberExpression" && parent.property === child && !parent.computed;
				if (!isPropertyName) used.add(child.name);
			});
			for (const parameter of node.params) {
				for (const name of declaredNames(parameter)) {
					if (name.startsWith("_") || used.has(name)) continue;
					context.report({ node: parameter, messageId: "unusedParameter", data: { name } });
				}
			}
		};

		return {
			ArrowFunctionExpression: check,
			FunctionDeclaration: check,
			FunctionExpression: check,
		};
	},
});
