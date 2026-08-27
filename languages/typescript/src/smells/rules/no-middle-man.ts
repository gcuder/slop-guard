import { defineRule } from "@oxlint/plugins";
import type { ESTree } from "@oxlint/plugins";

import { numberOption, thresholdSchema } from "../shared/options.ts";

const DEFAULT_MIN_METHODS = 2;

function delegateTarget(member: ESTree.MethodDefinition): string | null {
	const body = member.value.body;
	if (body === null || body === undefined || body.type !== "BlockStatement") return null;
	if (body.body.length !== 1) return null;
	const only = body.body[0];
	const expression =
		only?.type === "ReturnStatement"
			? only.argument
			: only?.type === "ExpressionStatement"
				? only.expression
				: null;
	if (expression === null || expression === undefined || expression.type !== "CallExpression") return null;
	const callee = expression.callee;
	if (callee.type !== "MemberExpression") return null;
	const owner = callee.object;
	if (
		owner.type !== "MemberExpression" ||
		owner.object.type !== "ThisExpression" ||
		owner.property.type !== "Identifier"
	) {
		return null;
	}
	return owner.property.name;
}

/** Ban classes that only pass calls along. */
export const noMiddleManRule = defineRule({
	meta: {
		type: "problem",
		docs: {
			description:
				"Disallow a class whose methods all forward to one of its own fields; the class adds a hop and nothing else.",
		},
		messages: {
			middleMan:
				"Every method on `{{name}}` forwards to `this.{{target}}`, so the class adds a hop and nothing else. Let callers talk to `{{target}}` directly, and keep this class only if it is about to grow behaviour of its own.",
		},
		...thresholdSchema({ minMethods: DEFAULT_MIN_METHODS }),
	},
	createOnce(context) {
		return {
			ClassBody(node) {
				const parent = node.parent;
				if (parent?.type !== "ClassDeclaration" && parent?.type !== "ClassExpression") return;
				const minimum = numberOption(context.options, "minMethods", DEFAULT_MIN_METHODS);
				const methods = node.body.filter(
					(member): member is ESTree.MethodDefinition =>
						member.type === "MethodDefinition" && member.kind === "method",
				);
				if (methods.length < minimum) return;
				const targets = methods.map(delegateTarget);
				if (targets.some((target) => target === null)) return;
				context.report({
					node,
					messageId: "middleMan",
					data: { name: parent.id?.name ?? "This class", target: targets[0] ?? "the field" },
				});
			},
		};
	},
});
