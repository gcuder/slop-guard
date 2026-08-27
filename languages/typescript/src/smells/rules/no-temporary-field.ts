import { defineRule } from "@oxlint/plugins";
import type { ESTree } from "@oxlint/plugins";

import { walk } from "../shared/traversal.ts";

function assignedFields(node: ESTree.Node, visitorKeys: Readonly<Record<string, readonly string[]>>): Set<string> {
	const found = new Set<string>();
	walk(node, visitorKeys, (child) => {
		if (
			child.type === "AssignmentExpression" &&
			child.left.type === "MemberExpression" &&
			child.left.object.type === "ThisExpression" &&
			child.left.property.type === "Identifier"
		) {
			found.add(child.left.property.name);
		}
	});
	return found;
}

/** Ban fields that only exist for part of an object's life. */
export const noTemporaryFieldRule = defineRule({
	meta: {
		type: "problem",
		docs: {
			description:
				"Disallow `this` fields first assigned outside the constructor and never declared on the class.",
		},
		messages: {
			temporaryField:
				"`this.{{field}}` is created in `{{method}}` rather than in the constructor, so between construction and that call the field does not exist and every reader has to work out when it does. Declare it on the class, or pass it between the methods that use it.",
		},
	},
	createOnce(context) {
		return {
			ClassBody(node) {
				const declared = new Set<string>();
				for (const member of node.body) {
					if (
						(member.type === "PropertyDefinition" || member.type === "AccessorProperty") &&
						member.key.type === "Identifier"
					) {
						declared.add(member.key.name);
					}
				}
				const constructor = node.body.find(
					(member) => member.type === "MethodDefinition" && member.kind === "constructor",
				);
				const initialised =
					constructor === undefined
						? new Set<string>()
						: assignedFields(constructor, context.sourceCode.visitorKeys);

				for (const member of node.body) {
					if (member.type !== "MethodDefinition" || member.kind === "constructor") continue;
					const method =
						member.key.type === "Identifier" ? member.key.name : context.sourceCode.getText(member.key);
					for (const field of assignedFields(member, context.sourceCode.visitorKeys)) {
						if (declared.has(field) || initialised.has(field)) continue;
						context.report({
							node: member,
							messageId: "temporaryField",
							data: { field, method },
						});
					}
				}
			},
		};
	},
});
