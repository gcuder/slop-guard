# Coverage of the Python anti-patterns book

Every general Python entry in [The Little Book of Python Anti-Patterns](https://docs.quantifiedcode.com/python-anti-patterns/index.html), and the rule that enforces it. Forty-three of the forty-six entries have a rule.

Two scopes are deliberately left out. The book's Django chapters are out of scope, because slop-guard's Python pack is framework-neutral and those entries read Django settings modules and model definitions. Entries that exist only because the book targets Python 2 are out of scope as well; they are listed below with what modern Python does instead.

## Correctness

| Book entry | Rule |
| --- | --- |
| Accessing a protected member from outside the class | `no-protected-member-access` |
| Assigning a lambda expression to a variable | `no-lambda-assignment` |
| Assigning to built-in function | `no-builtin-shadowing` |
| Bad except clauses order | `no-unreachable-except-clause` |
| Bad first argument given to `super()` | `no-bad-super-arguments` |
| `else` clause on loop without a `break` statement | `no-loop-else-without-break` |
| `__exit__` must accept 3 arguments | `require-exit-signature` |
| Explicit return in `__init__` | `no-return-value-in-init` |
| `__future__` import is not the first statement | **not implemented** — a `SyntaxError` in Python 3 |
| Implementing Java-style getters and setters | `no-java-style-accessors` |
| Indentation contains mixed spaces and tabs | `no-mixed-indentation` |
| Indentation contains tabs | `no-tab-indentation` |
| Method could be a function | `no-method-without-receiver-use` |
| Method has no argument | `require-method-self` |
| Missing argument to `super()` | **not implemented** — Python 2 only |
| Using a mutable default value as an argument | `no-mutable-default-argument` |
| No exception type(s) specified | `no-bare-except` |
| Not using `defaultdict()` | `prefer-defaultdict` |
| Not using `else` where appropriate in a loop | `prefer-loop-else` |
| Not using explicit unpacking | `prefer-explicit-unpacking` |
| Not using `get()` to return a default value from a dict | `prefer-dict-get` |
| Not using `setdefault()` to initialize a dictionary | `prefer-setdefault` |

## Maintainability

| Book entry | Rule |
| --- | --- |
| Using wildcard imports (`from … import *`) | `no-wildcard-imports` |
| Not using `with` to open files | `require-with-for-open` |
| Returning more than one variable type from function call | `no-mixed-return-types` |
| Using the `global` statement | `no-global-statement` |
| Using single letter to name your variables | `no-single-letter-names` |
| Dynamically creating variable/method/function names | `no-computed-attribute-names` |

## Readability

| Book entry | Rule |
| --- | --- |
| Asking for permission instead of forgiveness | `prefer-eafp-for-files` |
| Comparing things to None the wrong way | `no-comparison-to-none` |
| Comparing things to True the wrong way | `no-comparison-to-bool` |
| Using `type()` to compare types | `no-type-comparison` |
| Not using dict comprehensions | `prefer-dict-comprehension` |
| Not using dict keys when formatting strings | `prefer-format-mapping` |
| Not using `items()` to iterate over a dictionary | `prefer-dict-items` |
| Not using named tuples when returning more than one value | `prefer-named-tuple` |
| Not using unpacking for updating multiple values at once | `prefer-tuple-swap` |
| Not using `zip()` to iterate over a pair of lists | `prefer-zip` |
| Putting type information in a variable name | `no-type-in-name` |
| Test for object identity should be `is` | `no-identity-comparison-to-literal` |
| Using an unpythonic loop | `prefer-enumerate` |
| Using `map()` or `filter()` where a list comprehension is possible | `prefer-comprehension-over-map-filter` |
| Using CamelCase in function names | `no-camel-case-functions` |

## Security

| Book entry | Rule |
| --- | --- |
| Use of `exec` | `no-exec` |

## Performance

| Book entry | Rule |
| --- | --- |
| Using `key in list` to check if a key is contained in a list | `prefer-set-membership` |
| Not using `iteritems()` to iterate over a large dictionary | **not implemented** — Python 2 only |

## The two Python 2 entries

The book was written for Python 2, and two of its entries describe a language that no longer exists. Neither has a rule, because neither pattern can occur in the Python this checker supports:

- **Missing argument to `super()`.** The book says to write `super(Class, self)`, because bare `super()` fails on Python 2. Python 3 added the bare form, and it is now the ordinary spelling. `no-bad-super-arguments` still flags arguments that are genuinely wrong, such as `super(self, Class)`, which raises `TypeError` in any version.
- **Not using `iteritems()`.** The book says to prefer `iteritems()` over `items()` for large dictionaries. Python 3 removed `iteritems()` and made `items()` a view, so the recommended call no longer exists and the flagged call is already correct.

## The `__future__` import entry

**`__future__` import is not the first non-docstring statement.** In Python 3 this is a `SyntaxError`: the interpreter refuses to compile the file at all, so a file that violates it never parses and no linter can reach it. slop-guard reports unparseable files by name, which is all there is to report.

## Two rules that overlap the book across chapters

`no-type-comparison` (readability) and slop-guard's own `no-runtime-isinstance` (evidence) both concern runtime type checks, and they disagree on purpose: the book recommends `isinstance`, while slop-guard's core position is to parse at the boundary. The rules were split so neither reports the other's case — `no-type-comparison` owns `type(a) == type(b)`, and `no-runtime-isinstance` owns `isinstance`. Enable both, or keep only the one that matches your team's position.

The same split applies to `no-bare-except` (correctness), which owns `except:`, and `no-silent-exception-swallow` (evidence), which owns a handler that discards what it caught.
