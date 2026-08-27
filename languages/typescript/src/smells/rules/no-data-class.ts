import { defineRule } from "@oxlint/plugins";
import type { ESTree } from "@oxlint/plugins";

function isAccessor(member: ESTree.MethodDefinition): boolean {
	if (member.kind === "get" || member.kind === "set") return true;
	const body = member.value.body;
	if (body === null || body === undefined || body.type !== "BlockStatement") return false;
	if (body.body.length !== 1) return false;
	const only = body.body[0];
	if (only?.type === "ReturnStatement") {
		return only.argument?.type === "MemberExpression" && only.argument.object.type === "ThisExpression";
	}
	return (
		only?.type === "ExpressionStatement" &&
		only.expression.type === "AssignmentExpression" &&
		only.expression.left.type === "MemberExpression" &&
		only.expression.left.object.type === "ThisExpression"
	);
}

/** Ban classes that hold data and do nothing with it. */
export const noDataClassRule = defineRule({
	meta: {
		type: "problem",
		docs: {
			description:
				"Disallow a class whose methods only store and return its own fields; the decisions about that data live elsewhere.",
		},
		messages: {
			dataClass:
				"`{{name}}` only stores and hands back its own fields, so the code that decides anything about that data lives somewhere else. Move the behaviour that reads these fields into the class, or make it a plain type.",
		},
	},
	createOnce(context) {
		return {
			ClassBody(node) {
				const parent = node.parent;
				if (parent?.type !== "ClassDeclaration" && parent?.type !== "ClassExpression") return;
				if ((parent.decorators?.length ?? 0) > 0) return;
				const methods = node.body.filter(
					(member): member is ESTree.MethodDefinition => member.type === "MethodDefinition",
				);
				const fields = node.body.filter(
					(member) => member.type === "PropertyDefinition" || member.type === "AccessorProperty",
				);
				const behaviour = methods.filter(
					(member) => member.kind !== "constructor" && !isAccessor(member),
				);
				const hasState = fields.length > 0 || methods.some((member) => member.kind === "constructor");
				if (!hasState || methods.length === 0 || behaviour.length > 0) return;
				context.report({
					node,
					messageId: "dataClass",
					data: { name: parent.id?.name ?? "This class" },
				});
			},
		};
	},
});
