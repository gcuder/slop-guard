import { defineRule } from "@oxlint/plugins";

/** Ban reaching into another object's internal members. */
export const noInappropriateIntimacyRule = defineRule({
	meta: {
		type: "problem",
		docs: {
			description:
				"Disallow reading another object's underscore-prefixed members; `#private` fields are left to the language, which already limits them to the declaring class.",
		},
		messages: {
			inappropriateIntimacy:
				"`{{owner}}.{{member}}` reaches past the public interface of another object, so this code breaks whenever that object rearranges its insides. Ask the owner for a public method that answers the question.",
		},
	},
	createOnce(context) {
		return {
			MemberExpression(node) {
				if (node.object.type === "ThisExpression" || node.object.type === "Super") return;
				const property = node.property;
				if (property.type !== "Identifier" || !property.name.startsWith("_")) return;
				const member = property.name;
				context.report({
					node,
					messageId: "inappropriateIntimacy",
					data: { owner: context.sourceCode.getText(node.object), member },
				});
			},
		};
	},
});
