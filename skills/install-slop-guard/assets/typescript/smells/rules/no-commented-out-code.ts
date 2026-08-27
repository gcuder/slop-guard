import { defineRule } from "@oxlint/plugins";

const CODE_SHAPED =
	/(^|\s)(return|const|let|var|function|class|import|export|if|for|while|await)\s|[;{}]\s*$|\)\s*[;{]?\s*$|=>/u;
const PROSE_MARKERS = ["eslint", "oxlint", "@ts-", "TODO", "FIXME", "NOTE", "SAFETY:", "prettier"];

/** Ban code left behind as a comment. */
export const noCommentedOutCodeRule = defineRule({
	meta: {
		type: "problem",
		docs: {
			description:
				"Disallow commented-out code; version control already remembers what was deleted.",
		},
		messages: {
			commentedOutCode:
				"This comment is code that has been switched off, so a reader has to guess whether it still matters. Delete it; version control already remembers it.",
		},
	},
	createOnce(context) {
		return {
			Program(node) {
				for (const comment of node.comments) {
					const text = comment.value.trim();
					if (text.length === 0) continue;
					if (PROSE_MARKERS.some((marker) => text.includes(marker))) continue;
					if (!CODE_SHAPED.test(text)) continue;
					context.report({ node: comment, messageId: "commentedOutCode" });
				}
			},
		};
	},
});
