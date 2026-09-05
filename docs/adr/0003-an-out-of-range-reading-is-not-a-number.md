# An out-of-range reading is not a number

When a Dexcom sensor reads outside the range it can report, Clarity writes a localized
word in the glucose column rather than a number. T1Pal models a reading as a sum type: it
carries either a numeric value or an out-of-range marker, never both and never a
substituted number. Out-of-range readings are excluded from mean and coefficient of
variation, included in time in range, time below range and time above range, and the count
excluded is printed alongside every statistic that dropped them.

## Consequences

A flag beside an optional number would have been simpler, and is rejected because a flag
can be ignored by a caller while a sum type cannot. This is the decision in the model with
the most direct safety weight: averaging a fabricated low as if it were a measurement
biases every downstream figure toward the middle of the range.

Downstream projects that faced the same choice picked different numbers — 40 and 400 in
one, 39 and 401 in another — which is evidence that no substitution is obviously correct.

The same fabrication exists upstream and is a reason not to trust a second source for
glucose. Where Clarity writes the word, the Tandem export writes a number: the sensor's
reportable floor, converted into mmol/L. A real Clarity export separately contains genuine
numeric readings at that same floor value, so Clarity distinguishes a measurement at the
floor from a reading below it and Tandem cannot. See ADR-0004.
