import { defineRule } from "@oxlint/plugins";
import type { ESTree } from "@oxlint/plugins";

import { numberOption, thresholdSchema } from "../shared/options.ts";

const DEFAULT_MAX_LINKS = 3;

/** Ban long chains that walk through several objects. */
export const noMessageChainsRule = defineRule({
	meta: {
		type: "problem",
		docs: {
			description:
				"Disallow chains of more than `maxLinks` property or call hops. A chain rooted at `this` counts too, because it still walks the objects after the first hop.",
		},
		messages: {
			messageChain:
				"This walks {{links}} objects deep from `{{base}}`, so it depends on how each one is built along the way, and any of them changing breaks this line. Ask `{{base}}` for what you actually need.",
		},
		...thresholdSchema({ maxLinks: DEFAULT_MAX_LINKS }),
	},
	createOnce(context) {
		const inner = new Set<ESTree.Node>();

		return {
			Program() {
				inner.clear();
			},
			MemberExpression(node) {
				// The walk reaches the outermost member expression first; its hops are skipped after.
				if (inner.has(node)) return;
				const limit = numberOption(context.options, "maxLinks", DEFAULT_MAX_LINKS);
				let links = 0;
				let current: ESTree.Node = node;
				while (true) {
					if (current.type === "MemberExpression") {
						links += 1;
						if (current !== node) inner.add(current);
						current = current.object;
						continue;
					}
					if (current.type === "CallExpression") {
						current = current.callee;
						continue;
					}
					if (current.type === "TSNonNullExpression" || current.type === "ChainExpression") {
						current = current.expression;
						continue;
					}
					break;
				}
				if (links <= limit) return;
				context.report({
					node,
					messageId: "messageChain",
					data: { links: String(links), base: context.sourceCode.getText(current) },
				});
			},
		};
	},
});
