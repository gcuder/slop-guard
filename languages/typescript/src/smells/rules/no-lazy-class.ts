import { defineRule } from "@oxlint/plugins";

import { walk } from "../shared/traversal.ts";

/** Ban classes that do not earn their keep. */
export const noLazyClassRule = defineRule({
	meta: {
		type: "problem",
		docs: {
			description:
				"Disallow a class with no fields and at most one method; a function says the same thing with less ceremony.",
		},
		messages: {
			lazyClass:
				"`{{name}}` holds no state and has one method, so the class adds a name and a call without adding a decision. Make `{{method}}` a function.",
		},
	},
	createOnce(context) {
		return {
			ClassBody(node) {
				const parent = node.parent;
				if (parent?.type !== "ClassDeclaration" && parent?.type !== "ClassExpression") return;
				if (parent.superClass !== null && parent.superClass !== undefined) return;
				if (parent.abstract === true || (parent.decorators?.length ?? 0) > 0) return;
				const fields = node.body.filter(
					(member) => member.type === "PropertyDefinition" || member.type === "AccessorProperty",
				);
				const methods = node.body.filter(
					(member) => member.type === "MethodDefinition" && member.kind === "method",
				);
				const constructors = node.body.filter(
					(member) => member.type === "MethodDefinition" && member.kind === "constructor",
				);
				if (fields.length > 0 || methods.length !== 1 || constructors.length > 0) return;
				let holdsState = false;
				walk(node, context.sourceCode.visitorKeys, (child) => {
					if (
						child.type === "AssignmentExpression" &&
						child.left.type === "MemberExpression" &&
						child.left.object.type === "ThisExpression"
					) {
						holdsState = true;
					}
				});
				if (holdsState) return;
				const only = methods[0];
				context.report({
					node,
					messageId: "lazyClass",
					data: {
						name: parent.id?.name ?? "This class",
						method:
							only !== undefined && only.type === "MethodDefinition" && only.key.type === "Identifier"
								? only.key.name
								: "it",
					},
				});
			},
		};
	},
});
