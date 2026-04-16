# Review Checklist

Work through these in order. Stop at CRITICAL — fix before proceeding.

## ✅ Correctness
- [ ] Does the code do what the description claims?
- [ ] Are edge cases handled? (empty lists, zero, None/null, max values)
- [ ] Are error conditions handled? What happens when it fails?
- [ ] Are return values checked where they matter?
- [ ] Are off-by-one errors possible? (loops, date ranges, indexes)
- [ ] Is conditional logic correct? (especially complex boolean expressions)
- [ ] Are there unreachable code paths or dead branches?

## 🔒 Security
- [ ] Is user input validated/sanitized before use?
- [ ] Are there SQL/command injection risks?
- [ ] Is auth checked before data access?
- [ ] Are secrets/keys hardcoded anywhere?
- [ ] Is data properly escaped before output?
- [ ] Are file paths sanitized (path traversal)?

## 💰 Financial Logic (finbench-specific)
- [ ] Are monetary values using decimal/fixed-point, NOT float?
- [ ] Is rounding done explicitly and correctly? (round half up vs banker's rounding)
- [ ] Are date ranges correct? (inclusive vs exclusive endpoints)
- [ ] Are timezone conversions explicit?
- [ ] Are percentage calculations correct? (0.05 vs 5 for 5%?)
- [ ] Is division-by-zero possible?
- [ ] Are there precision loss risks in arithmetic chains?

## 🔄 State Management
- [ ] Is concurrent access possible? Are shared resources protected?
- [ ] Can state get out of sync between components?
- [ ] Are there race conditions in async code?
- [ ] Is state cleaned up properly (resources, connections, locks)?
- [ ] Are there unintended side effects?

## ⚡ Performance
- [ ] Are there N+1 query patterns?
- [ ] Are there unbounded loops or operations?
- [ ] Is unnecessary data loaded from DB/API?
- [ ] Are there missing indexes for query patterns?
- [ ] Are expensive operations cached where appropriate?
- [ ] Is pagination applied to potentially large datasets?

## 🧹 Maintainability
- [ ] Can a new person understand this code in 5 minutes?
- [ ] Are variable/function names descriptive?
- [ ] Is there duplicated logic that should be extracted?
- [ ] Are magic numbers explained or named?
- [ ] Are comments accurate? (outdated comments are worse than no comments)
- [ ] Is the abstraction level consistent?

## 🎨 Style (never block on these)
- [ ] Consistent with surrounding code?
- [ ] No obvious formatting issues?
- [ ] Function/file length reasonable?
