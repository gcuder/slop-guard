import { defineRule } from "@oxlint/plugins";
import type { ESTree } from "@oxlint/plugins";

import { numberOption, thresholdSchema } from "../shared/options.ts";

const DEFAULT_MAX_SAME_TYPE = 2;

const PRIMITIVE_KEYWORDS: Readonly<Record<string, string>> = {
	TSStringKeyword: "string",
	TSNumberKeyword: "number",
	TSBooleanKeyword: "boolean",
	TSBigIntKeyword: "bigint",
};

type ParameterOwner =
	| ESTree.ArrowFunctionExpression
	| ESTree.Function
	| ESTree.TSMethodSignature;

function parameterName(parameter: ESTree.ParamPattern): string | null {
	if (parameter.type === "Identifier") return parameter.name;
	if (parameter.type === "TSParameterProperty") return parameterName(parameter.parameter);
	return null;
}

/** Ban runs of same-typed primitive parameters that a domain type should carry. */
export const noPrimitiveObsessionRule = defineRule({
	meta: {
		type: "problem",
		docs: {
			description:
				"Disallow more than `maxSameType` parameters of the same primitive type; give the domain concept a type of its own.",
		},
		messages: {
			primitiveObsession:
				"This function takes {{count}} `{{primitive}}` parameters ({{names}}), so any two of them can be swapped at a call site and nothing complains. Give the values a type of their own.",
		},
		...thresholdSchema({ maxSameType: DEFAULT_MAX_SAME_TYPE }),
	},
	createOnce(context) {
		const check = (node: ParameterOwner) => {
			const limit = numberOption(context.options, "maxSameType", DEFAULT_MAX_SAME_TYPE);
			const counts = new Map<string, string[]>();
			for (const parameter of node.params) {
				const name = parameterName(parameter);
				const annotation =
					parameter.type === "Identifier" ? parameter.typeAnnotation?.typeAnnotation : undefined;
				if (name === null || annotation === undefined || annotation === null) continue;
				const primitive = PRIMITIVE_KEYWORDS[annotation.type];
				if (primitive === undefined) continue;
				counts.set(primitive, [...(counts.get(primitive) ?? []), name]);
			}
			for (const [primitive, names] of counts) {
				if (names.length <= limit) continue;
				context.report({
					node,
					messageId: "primitiveObsession",
					data: {
						count: String(names.length),
						primitive,
						names: names.map((name) => `\`${name}\``).join(", "),
					},
				});
			}
		};

		return {
			ArrowFunctionExpression: check,
			FunctionDeclaration: check,
			FunctionExpression: check,
			TSDeclareFunction: check,
			TSMethodSignature: check,
		};
	},
});
