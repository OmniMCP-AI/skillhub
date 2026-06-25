# Intake Decision Tree

1. Did the user provide a file or path?
   - If no, ask only for the file or path.
2. Is the format supported now?
   - If yes, continue to readability checks.
   - If delegated, explain the dependency or fallback.
3. Is the source readable?
   - If yes, hand off to validation or analysis.
   - If partial, report what is missing or unreadable.
4. Is the scope enough for a formal workflow?
   - If yes, route onward.
   - If no, ask for the smallest missing input.

