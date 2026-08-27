import { defineRule } from "@oxlint/plugins";
import type { ESTree } from "@oxlint/plugins";

import { numberOption, thresholdSchema } from "../shared/options.ts";

const DEFAULT_MIN_STATEMENTS = 3;

type FunctionNode = ESTree.ArrowFunctionExpression | ESTree.Function;

function normalise(text: string): string {
	return text.replace(/\s+/gu, " ").trim();
}

/** Ban two functions in one file with identical bodies. */
export const noDuplicateCodeRule = defineRule({
	meta: {
		type: "problem",
		docs: {
			description:
				"Disallow two functions in a file with identical bodies of `minStatements` statements or more.",
		},
		messages: {
			duplicateCode:
				"This function has the same body as an earlier one, so a fix to one has to be remembered for the other. Keep one copy and call it from both.",
		},
		...thresholdSchema({ minStatements: DEFAULT_MIN_STATEMENTS }),
	},
	createOnce(context) {
		const seen = new Set<string>();

		const check = (node: FunctionNode) => {
			const body = node.body;
			if (body === null || body === undefined || body.type !== "BlockStatement") return;
			const minimum = numberOption(context.options, "minStatements", DEFAULT_MIN_STATEMENTS);
			if (body.body.length < minimum) return;
			const fingerprint = normalise(context.sourceCode.getText(body));
			if (!seen.has(fingerprint)) {
				seen.add(fingerprint);
				return;
			}
			context.report({ node, messageId: "duplicateCode" });
		};

		return {
			Program() {
				seen.clear();
			},
			ArrowFunctionExpression: check,
			FunctionDeclaration: check,
			FunctionExpression: check,
		};
	},
});
