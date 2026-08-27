import { defineRule } from "@oxlint/plugins";
import type { ESTree } from "@oxlint/plugins";

import { numberOption, thresholdSchema } from "../shared/options.ts";

const DEFAULT_MIN_BRANCHES = 3;

function testedValue(test: ESTree.Expression, sourceCode: { getText(node: ESTree.Node): string }): string | null {
	if (test.type !== "BinaryExpression") return null;
	if (test.operator !== "===" && test.operator !== "==") return null;
	if (test.right.type !== "Literal") return null;
	return sourceCode.getText(test.left);
}

/** Ban branching on a type code where a type could decide instead. */
export const noTypeCodeSwitchRule = defineRule({
	meta: {
		type: "problem",
		docs: {
			description:
				"Disallow a `switch` or `if`/`else if` chain of `minBranches` or more branches testing one value against literals.",
		},
		messages: {
			typeCodeSwitch:
				"This tests `{{subject}}` against {{count}} literal values, so every new value means editing this chain and every other one like it. Let the type decide: give each case its own class or handler and look it up.",
		},
		...thresholdSchema({ minBranches: DEFAULT_MIN_BRANCHES }),
	},
	createOnce(context) {
		const inner = new Set<ESTree.Node>();

		return {
			Program() {
				inner.clear();
			},
			SwitchStatement(node) {
				const minimum = numberOption(context.options, "minBranches", DEFAULT_MIN_BRANCHES);
				const literalCases = node.cases.filter((entry) => entry.test?.type === "Literal").length;
				if (literalCases < minimum) return;
				context.report({
					node,
					messageId: "typeCodeSwitch",
					data: {
						subject: context.sourceCode.getText(node.discriminant),
						count: String(literalCases),
					},
				});
			},
			IfStatement(node) {
				if (inner.has(node)) return;
				const minimum = numberOption(context.options, "minBranches", DEFAULT_MIN_BRANCHES);
				let subject: string | null = null;
				let branches = 0;
				let current: ESTree.IfStatement | null = node;
				while (current !== null) {
					const tested = testedValue(current.test, context.sourceCode);
					if (tested === null) break;
					if (subject === null) subject = tested;
					else if (tested !== subject) break;
					branches += 1;
					if (current !== node) inner.add(current);
					const alternate: ESTree.Statement | null | undefined = current.alternate;
					current = alternate !== null && alternate !== undefined && alternate.type === "IfStatement"
						? alternate
						: null;
				}
				if (subject === null || branches < minimum) return;
				context.report({
					node,
					messageId: "typeCodeSwitch",
					data: { subject, count: String(branches) },
				});
			},
		};
	},
});
