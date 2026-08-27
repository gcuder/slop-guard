import { defineRule } from "@oxlint/plugins";
import type { ESTree } from "@oxlint/plugins";

import { numberOption, thresholdSchema } from "../shared/options.ts";
import { walk } from "../shared/traversal.ts";

const DEFAULT_MAX_METHODS = 10;
const DEFAULT_MAX_FIELDS = 10;

function className(node: ESTree.ClassBody): string {
	const parent = node.parent;
	if (
		(parent?.type === "ClassDeclaration" || parent?.type === "ClassExpression") &&
		parent.id !== null &&
		parent.id !== undefined
	) {
		return parent.id.name;
	}
	return "This class";
}

/** Ban classes that carry more than one job's worth of members. */
export const noLargeClassRule = defineRule({
	meta: {
		type: "problem",
		docs: {
			description:
				"Disallow classes with more than `maxMethods` methods or `maxFields` fields; a class this wide has more than one reason to change.",
		},
		messages: {
			manyMethods:
				"`{{name}}` declares {{count}} methods, past the {{limit}} this project allows. A class this wide has more than one reason to change; split the group of methods that share data into their own class.",
			manyFields:
				"`{{name}}` holds {{count}} fields, past the {{limit}} this project allows. Group the ones that change together into a smaller type.",
		},
		...thresholdSchema({ maxMethods: DEFAULT_MAX_METHODS, maxFields: DEFAULT_MAX_FIELDS }),
	},
	createOnce(context) {
		return {
			ClassBody(node) {
				const methodLimit = numberOption(context.options, "maxMethods", DEFAULT_MAX_METHODS);
				const fieldLimit = numberOption(context.options, "maxFields", DEFAULT_MAX_FIELDS);
				const methods = node.body.filter((member) => member.type === "MethodDefinition");
				const fields = new Set<string>();
				for (const member of node.body) {
					if (member.type === "PropertyDefinition" && member.key.type === "Identifier") {
						fields.add(member.key.name);
					}
				}
				walk(node, context.sourceCode.visitorKeys, (child) => {
					if (
						child.type === "MemberExpression" &&
						child.object.type === "ThisExpression" &&
						child.property.type === "Identifier" &&
						child.parent?.type === "AssignmentExpression"
					) {
						fields.add(child.property.name);
					}
				});
				if (methods.length > methodLimit) {
					context.report({
						node,
						messageId: "manyMethods",
						data: {
							name: className(node),
							count: String(methods.length),
							limit: String(methodLimit),
						},
					});
					return;
				}
				if (fields.size > fieldLimit) {
					context.report({
						node,
						messageId: "manyFields",
						data: { name: className(node), count: String(fields.size), limit: String(fieldLimit) },
					});
				}
			},
		};
	},
});
