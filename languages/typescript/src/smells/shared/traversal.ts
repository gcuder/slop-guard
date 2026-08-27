import type { ESTree } from "@oxlint/plugins";

export type VisitorKeys = Readonly<Record<string, readonly string[]>>;

export type FunctionNode =
	| ESTree.ArrowFunctionExpression
	| ESTree.Function
	| ESTree.FunctionBody;

const FUNCTION_TYPES = new Set([
	"ArrowFunctionExpression",
	"FunctionDeclaration",
	"FunctionExpression",
	"TSDeclareFunction",
	"TSEmptyBodyFunctionExpression",
]);

const CLASS_TYPES = new Set(["ClassDeclaration", "ClassExpression"]);

function isNode(value: unknown): value is ESTree.Node {
	return (
		typeof value === "object" && value !== null && "type" in value && typeof value.type === "string"
	);
}

/** Report whether a node introduces its own function scope. */
export function isFunctionNode(node: ESTree.Node): boolean {
	return FUNCTION_TYPES.has(node.type);
}

/** Report whether a node declares a class. */
export function isClassNode(node: ESTree.Node): boolean {
	return CLASS_TYPES.has(node.type);
}

/** Visit a node and its descendants, stopping wherever `descend` says not to go deeper. */
export function walk(
	node: ESTree.Node,
	visitorKeys: VisitorKeys,
	visit: (node: ESTree.Node) => void,
	descend: (node: ESTree.Node) => boolean = () => true,
): void {
	visit(node);
	if (!descend(node)) return;
	const record = node as unknown as Readonly<Record<string, unknown>>;
	for (const key of visitorKeys[node.type] ?? []) {
		const value = record[key];
		if (isNode(value)) {
			walk(value, visitorKeys, visit, descend);
			continue;
		}
		if (!Array.isArray(value)) continue;
		for (const child of value) {
			if (isNode(child)) walk(child, visitorKeys, visit, descend);
		}
	}
}

/** Count the statements a function runs, ignoring functions and classes declared inside it. */
export function statementCount(body: ESTree.Node, visitorKeys: VisitorKeys): number {
	let total = 0;
	walk(
		body,
		visitorKeys,
		(node) => {
			if (node.type.endsWith("Statement") || node.type.endsWith("Declaration")) total += 1;
		},
		(node) => node === body || (!isFunctionNode(node) && !isClassNode(node)),
	);
	return total;
}
