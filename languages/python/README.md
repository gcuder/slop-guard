# slop-guard for Python

A standalone `ast` checker that rejects low-evidence Python patterns. It has no third-party
dependencies, needs Python 3.12 or newer, and is meant to be vendored into a repository and
maintained there.

Seventy-five rules run in seven groups. `--list-rules` prints each rule with its group and, where it
enforces a published anti-pattern, a link to that entry.

The [repository README](../../README.md) explains how the agent skill installs this pack.
[`anti-patterns.md`](anti-patterns.md) maps the general Python chapters of The Little Book of Python
Anti-Patterns to the rules that enforce them, and [`code-smells.md`](../../code-smells.md) does the
same for the refactoring.guru catalogue.

## Manual local installation

Copy this pack's `src/slop_guard/` into the target repository, for example at `tools/slop_guard/`, and run it as a module. Python 3.12 or newer is required, and nothing else is.

```bash
python3 -m tools.slop_guard --list-rules
python3 -m tools.slop_guard src
```

The checker exits `1` when it reports a finding, so it works as a pre-commit hook or a CI step without a wrapper. `--format json` prints machine-readable findings, `--select` and `--ignore` take comma-separated rule names, and `--exit-zero` reports without failing the build.

## Configuration

Settings live under `[tool.slop-guard]` in the nearest `pyproject.toml`. `select` and `ignore` take rule names, `group:<name>` tokens, or both:

```toml
[tool.slop-guard]
select = ["group:evidence", "group:correctness", "group:security"]  # or leave it out to run all six
ignore = ["no-runtime-isinstance"]
exclude = [".claude", ".venv", "__pycache__", "build", "dist", "tools"]

[tool.slop-guard.rules."no-runtime-isinstance"]
allow_in_type_guards = true

[tool.slop-guard.rules."no-any-parameters"]
allow_variadic_any = true

[tool.slop-guard.rules."no-single-letter-names"]
allow = ["i", "n"]

[tool.slop-guard.rules."no-forbidden-terms-in-symbol-names"]
terms = ["shape", "helper", "manager"]
```

All seventy-five rules run by default. `select` replaces that list; `ignore` subtracts from it.

Several rules overlap Ruff, which is expected and harmless: `no-bare-except` overlaps `E722`, `no-type-comparison` overlaps `E721`, `no-mutable-default-argument` overlaps `B006`, `no-lambda-assignment` overlaps `E731`, and `no-wildcard-imports` overlaps `F403`. Leave the Ruff rules enabled.

## Rules

Seventy-five rules in seven groups, all on by default. `python3 -m slop_guard --list-rules` prints them with their group and source.

**evidence** (15) — slop-guard's own position: a type or a name should record evidence the program has.

- `no-any-parameters` — `Any` inputs, except a parameter named `cause`. `allow_variadic_any` exempts `*args` and `**kwargs`.
- `no-any-returns` — return annotations containing `Any`, including `Awaitable[Any]` and `list[Any]`.
- `no-any-type-aliases` — aliases that rename `Any`.
- `no-chained-casts` — `cast(A, cast(B, value))`.
- `no-conditional-empty-dict-spread` — `{**(payload if cond else {})}`.
- `no-dynamic-attribute-access` — `getattr`, `setattr`, `hasattr`, `delattr` with a literal name, and `__dict__` indexing.
- `no-forbidden-terms-in-symbol-names` — placeholder words in declared names; `terms` sets the list.
- `no-known-value-widening` — annotations that discard what the assigned value already proves.
- `no-module-mocking` — `mock.patch`, `mocker.patch`, and `monkeypatch.setattr`.
- `no-object-parameters` — `object` inputs.
- `no-runtime-isinstance` — ad hoc `isinstance` narrowing. `allow_in_type_guards` permits it inside `TypeGuard` and `TypeIs` functions.
- `no-silent-exception-swallow` — a handler that discards what it caught.
- `no-unsafe-dictionary-type` — mapping types whose value is `Any`, `object`, or an unparameterised container.
- `no-widen-then-cast` — widening a known value to `Any` or `object` and casting it back.
- `require-safety-comment-for-cast` — every `typing.cast` needs a `# SAFETY:` comment.

**correctness** (20) — code that misbehaves at runtime.

- `no-bad-super-arguments` — `super(self, Class)`, or a first argument that is not the enclosing class.
- `no-bare-except` — `except:` with no exception type.
- `no-builtin-shadowing` — binding a name such as `list`, `id`, or `type`.
- `no-java-style-accessors` — `get_x`/`set_x` methods that only move one attribute.
- `no-lambda-assignment` — a lambda bound to a name.
- `no-loop-else-without-break` — a loop `else` clause with no `break` to trigger it.
- `no-method-without-receiver-use` — a method that never reads `self` or `cls`.
- `no-mixed-indentation` — indentation that mixes tabs and spaces.
- `no-mutable-default-argument` — `def load(rows=[])`.
- `no-protected-member-access` — `owner._member` from outside the owning class.
- `no-return-value-in-init` — returning a value from `__init__`.
- `no-tab-indentation` — tabs in indentation.
- `no-unreachable-except-clause` — an `except` clause an earlier, broader one already caught.
- `prefer-defaultdict` — guarding a key before updating it in place.
- `prefer-dict-get` — branching on key presence only to pick a default.
- `prefer-explicit-unpacking` — a run of `first = values[0]`, `second = values[1]`.
- `prefer-loop-else` — a boolean flag that records whether a loop broke.
- `prefer-setdefault` — guarding a key before assigning it.
- `require-exit-signature` — `__exit__` must take the exception type, value, and traceback.
- `require-method-self` — a method must declare `self` or `cls`, or be `@staticmethod`.

**maintainability** (6)

- `no-computed-attribute-names` — `setattr` with a computed name, or writing into `globals()`.
- `no-global-statement` — the `global` statement.
- `no-mixed-return-types` — returning a value on one path and `None` on another, unless the return type names `None`.
- `no-single-letter-names` — single-letter names; `allow` lists exceptions.
- `no-wildcard-imports` — `from module import *`.
- `require-with-for-open` — `open()` outside a `with` block.

**readability** (15)

- `no-camel-case-functions` — camelCase function names.
- `no-comparison-to-bool` — `== True` and `== False`.
- `no-comparison-to-none` — `== None` and `!= None`.
- `no-identity-comparison-to-literal` — `is` against a number, string, or container literal.
- `no-type-comparison` — `type(a) == type(b)`.
- `no-type-in-name` — names such as `count_int` that state a type.
- `prefer-comprehension-over-map-filter` — `map` or `filter` with a lambda.
- `prefer-dict-comprehension` — `dict((key, value) for ...)`.
- `prefer-dict-items` — looking the key up inside the loop instead of iterating `items()`.
- `prefer-eafp-for-files` — checking `os.path.exists` before touching a file.
- `prefer-enumerate` — `for index in range(len(items))`.
- `prefer-format-mapping` — passing `mapping["key"]` repeatedly to `.format()`.
- `prefer-named-tuple` — returning three or more values in a bare tuple.
- `prefer-tuple-swap` — shuffling two names through a temporary.
- `prefer-zip` — indexing two sequences with the same counter.

**smells** (17) — the refactoring.guru code smells; every threshold is an option.

- `no-commented-out-code` — code left behind as a comment.
- `no-data-class` — a class whose methods only store and return its own fields.
- `no-data-clumps` — the same group of parameters travelling between functions.
- `no-duplicate-code` — two functions with identical bodies.
- `no-feature-envy` — a method that reads another object's members far more than its own.
- `no-large-class` — more methods or fields than one job's worth.
- `no-lazy-class` — a class with no state and one method.
- `no-long-method` — a function longer than the statement budget.
- `no-long-parameter-list` — more parameters than a caller can keep straight.
- `no-message-chains` — a chain that walks several objects deep.
- `no-middle-man` — a class whose methods only forward to one of its fields.
- `no-primitive-obsession` — several parameters of the same primitive type.
- `no-refused-bequest` — a subclass that overrides an inherited method only to refuse it.
- `no-temporary-field` — a field first assigned outside the constructor.
- `no-type-code-switch` — branching on a type code where a type could decide.
- `no-unreachable-code` — statements after `return`, `raise`/`throw`, `break`, or `continue`.
- `no-unused-parameter` — a parameter the body never reads.

**security** (1)

- `no-exec` — `exec`.

**performance** (1)

- `prefer-set-membership` — `value in [...]` against a literal list or tuple.

The correctness, maintainability, readability, security, and performance groups come from the general Python chapters of [The Little Book of Python Anti-Patterns](https://docs.quantifiedcode.com/python-anti-patterns/index.html). Two scopes are left out on purpose: its Django chapters, because this pack stays framework-neutral, and its Python 2 entries, because the patterns they describe cannot occur in Python 3. `languages/python/anti-patterns.md` maps every entry to its rule and says why each of the three unimplemented entries has none. The `smells` group comes from the refactoring.guru catalogue, mapped in `code-smells.md`.

## Evidence rule examples

Each snippet below is rejected by the named rule. These are the evidence rules, which are specific to slop-guard. The other five groups come from the anti-patterns book, and `--list-rules` prints a link to the entry each one enforces.

### `no-any-parameters`

```python
def handle(payload: Any) -> None: ...
```

A parameter named `cause` may be `Any`, matching the error-cause convention.

### `no-any-returns`

```python
def load_user() -> Any: ...
```

### `no-any-type-aliases`

```python
ExternalValue = Any
```

### `no-chained-casts`

```python
user = cast(User, cast(object, payload))
```

### `no-conditional-empty-dict-spread`

```python
options = {**({"timeout": timeout} if timeout is not None else {})}
```

Declare the field and give it a documented default instead.

### `no-dynamic-attribute-access`

```python
value = getattr(owner, "name")
```

Write `owner.name`, or parse the object into a type that declares the attribute. A computed key such as `getattr(owner, key)` is outside the rule.

### `no-forbidden-terms-in-symbol-names`

```python
class UserShape: ...
```

The rule reads declared names only, so `image.shape` is untouched.

### `no-known-value-widening`

```python
handlers: dict[str, Handler] = {"start": start_handler}
payload: Any = load_user()
```

The first discards the known `start` key; use `Final` and inference, a `TypedDict`, or a `Literal` key type. The second discards the type the call already returns.

### `no-module-mocking`

```python
monkeypatch.setattr("app.user_store.load", fake_load)
```

### `no-object-parameters`

```python
def save(value: object) -> None: ...
```

### `no-runtime-isinstance`

```python
if isinstance(payload, str):
    use_name(payload)
```

Projects without a parsing layer can permit these checks inside `TypeGuard` and `TypeIs` functions while continuing to reject ad hoc checks elsewhere:

```toml
[tool.slop-guard.rules."no-runtime-isinstance"]
allow_in_type_guards = true
```

The option defaults to `false`.

### `no-silent-exception-swallow`

```python
try:
    run()
except Exception:
    pass
```

A bare `except:` is `no-bare-except`'s case, in the correctness group.

### `no-unsafe-dictionary-type`

```python
metadata: dict[str, Any] = {}
rows: dict = load_rows()
```

### `no-widen-then-cast`

```python
stored: Any = load_user()
user = cast(User, stored)
```

### `require-safety-comment-for-cast`

```python
user_id = cast(UserId, value)
```

Add a specific justification immediately before a necessary cast:

```python
# SAFETY: parse_user_id validated the identifier before branding it.
user_id = cast(UserId, value)
```

## Development

```bash
./check.sh
PYTHONPATH=src python3 -m slop_guard --list-rules
PYTHONPATH=src python3 -m slop_guard src
```

`./check.sh` runs the tests and then the checker over its own source. There is no installation step.
