import { defineRule } from "@oxlint/plugins";
import type { ESTree } from "@oxlint/plugins";

function refusesInheritance(node: ESTree.MethodDefinition): boolean {
	const body = node.value.body;
	if (body === null || body === undefined || body.type !== "BlockStatement") return false;
	if (body.body.length !== 1) return false;
	const only = body.body[0];
	return only?.type === "ThrowStatement";
}

/** Ban subclasses that inherit a method only to refuse it. */
export const noRefusedBequestRule = defineRule({
	meta: {
		type: "problem",
		docs: {
			description:
				"Disallow overriding an inherited method with a bare `throw`; a subclass that refuses its base class is not that base class.",
		},
		messages: {
			refusedBequest:
				"`{{method}}` is inherited from `{{base}}` and then refused, so this class is not the thing its base class promises. Take what you need by holding a `{{base}}` instead of extending it.",
		},
	},
	createOnce(context) {
		return {
			ClassBody(node) {
				const parent = node.parent;
				if (parent?.type !== "ClassDeclaration" && parent?.type !== "ClassExpression") return;
				const superClass = parent.superClass;
				if (superClass === null || superClass === undefined) return;
				if (parent.abstract === true) return;
				for (const member of node.body) {
					if (member.type !== "MethodDefinition" || member.kind === "constructor") continue;
					if (!refusesInheritance(member)) continue;
					context.report({
						node: member,
						messageId: "refusedBequest",
						data: {
							method:
								member.key.type === "Identifier" ? member.key.name : context.sourceCode.getText(member.key),
							base: context.sourceCode.getText(superClass),
						},
					});
				}
			},
		};
	},
});
