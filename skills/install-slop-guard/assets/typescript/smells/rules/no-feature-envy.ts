import { defineRule } from "@oxlint/plugins";

import { numberOption, thresholdSchema } from "../shared/options.ts";
import { walk } from "../shared/traversal.ts";

const DEFAULT_MIN_ACCESSES = 5;
const DOMINANCE = 2;

/** Ban methods more interested in another object than in their own. */
export const noFeatureEnvyRule = defineRule({
	meta: {
		type: "problem",
		docs: {
			description:
				"Disallow a method that reads one parameter's members `minAccesses` times or more and at least twice as often as its own object's.",
		},
		messages: {
			featureEnvy:
				"`{{method}}` reads `{{owner}}` {{count}} times and its own object {{own}} time(s), so the decision this method makes is really about `{{owner}}`. Move the method there, and call it from here.",
		},
		...thresholdSchema({ minAccesses: DEFAULT_MIN_ACCESSES }),
	},
	createOnce(context) {
		return {
			MethodDefinition(node) {
				const body = node.value.body;
				if (body === null || body === undefined || body.type !== "BlockStatement") return;
				const minimum = numberOption(context.options, "minAccesses", DEFAULT_MIN_ACCESSES);
				const parameters = new Set(
					node.value.params
						.map((parameter) => (parameter.type === "Identifier" ? parameter.name : null))
						.filter((name): name is string => name !== null),
				);
				let own = 0;
				const foreign = new Map<string, number>();
				walk(body, context.sourceCode.visitorKeys, (child) => {
					if (child.type !== "MemberExpression") return;
					if (child.object.type === "ThisExpression") {
						own += 1;
						return;
					}
					if (child.object.type !== "Identifier" || !parameters.has(child.object.name)) return;
					foreign.set(child.object.name, (foreign.get(child.object.name) ?? 0) + 1);
				});
				for (const [owner, count] of foreign) {
					if (count < minimum || count <= own * DOMINANCE) continue;
					context.report({
						node,
						messageId: "featureEnvy",
						data: {
							method:
								node.key.type === "Identifier" ? node.key.name : context.sourceCode.getText(node.key),
							owner,
							count: String(count),
							own: String(own),
						},
					});
				}
			},
		};
	},
});
