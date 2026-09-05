# The canonical model has one glucose unit and no unit field

`docs/TECH_STACK.md` requires that glucose units cannot silently change. T1Pal enforces
this by removing the thing that could change: the canonical model stores mmol/L and
carries no unit field at all. The source's own unit is recorded on the source record, so
the conversion stays auditable, and mg/dL exists only inside an adapter and in display
formatting.

Values are stored as an integer count of 0.1 mmol/L, never as a floating-point number.

## Considered options

A validated unit field on each record moves the bug rather than removing it: the field is
correct and the comparison that forgets to check it is not. A field that does not exist
cannot be forgotten.

mmol/L over mg/dL because both real sources are mmol/L, so the first slice performs no
lossy conversion at all. A US mg/dL export converts at the adapter boundary onto the 0.1
grid, with the original value and unit preserved on the source record.

## Consequences

0.1 mmol/L is the true resolution of the data — both sources report exactly one decimal
place — so the integer is exact rather than an approximation, and sums stay exact until
the final division. `REAL` was rejected because it reintroduces the floating-point error
`Decimal` was chosen to avoid, and `TEXT` because it sorts lexicographically, which puts
10.0 below 9.9.

The domain type exposes a decimal in mmol/L and scales at the persistence boundary, which
keeps the domain model independent of persistence as `docs/TECH_STACK.md` requires.
