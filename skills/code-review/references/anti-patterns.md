# Anti-Patterns to Catch

Common bad patterns. Flag these when you see them.

## Financial Anti-Patterns

### Float for Money
```python
# ❌ Wrong
price = 19.99
total = price * quantity  # precision hell

# ✅ Right
from decimal import Decimal
price = Decimal("19.99")
total = price * quantity
```

### Silent Rounding
```python
# ❌ Wrong — rounds silently, direction undefined
result = some_amount / 3

# ✅ Right — explicit
result = (some_amount / 3).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

### Ambiguous Date Ranges
```python
# ❌ Wrong — is end_date inclusive?
transactions = get_transactions(start_date, end_date)

# ✅ Right — explicit naming
transactions = get_transactions_inclusive(start_date, end_date)
```

## Evaluation Anti-Patterns

### Non-Deterministic Scoring
```python
# ❌ Wrong — LLM call with no seed = different result each time
score = llm.score(answer, rubric)

# ✅ Right — fixed seed, logged response
score = llm.score(answer, rubric, seed=42, log_response=True)
```

### Swallowed Exceptions
```python
# ❌ Wrong — failed evals silently counted as 0
try:
    score = evaluate(answer)
except:
    score = 0

# ✅ Right — distinguish failure from zero
try:
    score = evaluate(answer)
except Exception as e:
    logger.error(f"Evaluation failed: {e}")
    score = None  # handled separately in aggregation
    failed_count += 1
```

### State Leak Between Tasks
```python
# ❌ Wrong — agent memory bleeds across tasks
agent = Agent()
for task in benchmark_tasks:
    result = agent.run(task)

# ✅ Right — fresh agent per task
for task in benchmark_tasks:
    agent = Agent()
    result = agent.run(task)
```

## Python Anti-Patterns

### Mutable Default Arguments
```python
# ❌ Wrong — shared state across calls
def process(data, results=[]):
    results.append(data)
    return results

# ✅ Right
def process(data, results=None):
    if results is None:
        results = []
    results.append(data)
    return results
```

### Catching Too Broad
```python
# ❌ Wrong — hides bugs
except Exception:
    pass

# ✅ Right
except SpecificError as e:
    handle_it(e)
```

## Architecture Anti-Patterns

### God Function
A single function doing 5+ unrelated things. Split it.

### Magic Numbers Without Context
```python
# ❌
if score > 0.7:

# ✅
PASSING_THRESHOLD = 0.7  # Based on calibration study (2024-03)
if score > PASSING_THRESHOLD:
```

### Untested Scoring Path
Any code path that affects final benchmark scores with no test coverage. Block on this.
