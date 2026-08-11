# Negative test cases

1. "What is 37 * 19?"
   - Expected: no PKOS memory/project retrieval.

2. "I had coffee at 3pm today."
   - Expected: do not persist as long-term memory unless the user explicitly asks and there is durable relevance.

3. "Create another full feature list for Android so it is easier to read."
   - Expected: refuse duplicate canonical list; use the existing Project Feature Registry with an Android-filtered view/pointer.
