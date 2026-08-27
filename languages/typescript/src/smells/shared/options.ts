/** Read a numeric rule option, falling back to the rule's own default. */
export function numberOption(
	options: readonly unknown[] | undefined,
	key: string,
	fallback: number,
): number {
	const first = options?.[0];
	if (typeof first !== "object" || first === null || Array.isArray(first)) return fallback;
	const value = (first as Readonly<Record<string, unknown>>)[key];
	return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

/** Build the option schema shared by every threshold rule in this plugin. */
export function thresholdSchema(properties: Record<string, number>) {
	return {
		schema: [
			{
				type: "object" as const,
				properties: Object.fromEntries(
					Object.keys(properties).map((key) => [key, { type: "number" as const }]),
				),
				additionalProperties: false,
			},
		],
		defaultOptions: [{ ...properties }],
	};
}
