import { defineRule } from "@oxlint/plugins";
import type { ESTree } from "@oxlint/plugins";

const TERMINATORS: Readonly<Record<string, string>> = {
	ReturnStatement: "return",
	ThrowStatement: "throw",
	BreakStatement: "break",
	ContinueStatement: "continue",
};

function reportUnreachable(
	body: readonly ESTree.Statement[],
	report: (node: ESTree.Statement, keyword: string) => void,
): void {
	for (let index = 0; index < body.length - 1; index += 1) {
		const statement = body[index];
		const keyword = statement === undefined ? undefined : TERMINATORS[statement.type];
		const following = body[index + 1];
		if (keyword === undefined || following === undefined) continue;
		report(following, keyword);
		return;
	}
}

/** Ban statements that can never run. */
export const noUnreachableCodeRule = defineRule({
	meta: {
		type: "problem",
		docs: {
			description:
				"Disallow statements after `return`, `throw`, `break`, or `continue` in the same block.",
		},
		messages: {
			unreachableCode:
				"Nothing after the `{{keyword}}` above can run, so this code is dead. Delete it, or move the `{{keyword}}` if the order is wrong.",
		},
	},
	createOnce(context) {
		const report = (node: ESTree.Statement, keyword: string) => {
			context.report({ node, messageId: "unreachableCode", data: { keyword } });
		};

		return {
			BlockStatement(node) {
				reportUnreachable(node.body, report);
			},
			SwitchCase(node) {
				reportUnreachable(node.consequent, report);
			},
			Program(node) {
				reportUnreachable(node.body as readonly ESTree.Statement[], report);
			},
		};
	},
});
