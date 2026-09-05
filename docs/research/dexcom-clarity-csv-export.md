# Dexcom Clarity CSV Export

Research note for the T1Pal Dexcom adapter. Scope: the Dexcom Clarity CSV export for a Dexcom G7 user, plus the other first-party and reverse-engineered routes to G7 data.

Each claim below is tagged with its evidence class:

- **[Dexcom]** — stated in Dexcom's own documentation.
- **[Observed]** — read directly out of a real Clarity export file. Sources are named in [Sources](#sources).
- **[Code]** — inferred from open-source code that parses Clarity exports.
- **[Inferred]** — a conclusion drawn from the above, not stated anywhere.

## Summary

What is known with confidence:

- The export is **web-only**. `clarity.dexcom.com` produces one `.csv` file. The Clarity mobile app produces PDF reports only. **[Dexcom]**
- The column set is **14 columns and has not changed between the G6 era and the G7 era**. Two independent real G7 exports from October and November 2025 carry byte-identical headers to G6 exports from 2019 and 2023. **[Observed]**
- The `Timestamp (YYYY-MM-DDThh:mm:ss)` column is **naive local wall-clock time**. It has no offset, no zone, and no UTC counterpart. It is provably ambiguous across a DST fall-back: a real export spanning 2 November 2025 contains eight local timestamps that each appear twice. **[Observed]**
- There is **no stable record id**. `Index` is a row counter for the file, so it is not stable across exports. A synthetic key must be derived. The pair `(Transmitter ID, Transmitter Time (Long Integer))` was unique across every EGV row in the samples, including the repeated DST hour, and is the best available key. **[Observed] [Inferred]**
- Out-of-range readings are encoded as the **strings** `High` and `Low`, not as numeric sentinels, and the same string appears in **both** `Event Subtype` and `Glucose Value`. **[Observed]**
- Gaps and sensor warm-up are represented as **missing rows only**. There is no sensor-start, sensor-stop or warm-up marker row. **[Observed]**

What is **not** known, and what this note does not claim:

- Dexcom publishes **no specification** of the CSV column set, the row types, the timestamp semantics, or the encoding of out-of-range values. Everything in the field-by-field sections below is from real files and from parsing code, not from a Dexcom document.
- ~~Whether the header differs by locale beyond the glucose unit.~~ **Now known.** A real
  Czech-locale export localizes the column names, the event-type values, and the
  out-of-range strings, and changes the delimiter and the decimal separator. See
  section 2a. Behaviour in regions outside the US/EU/CZ is still unknown.
- Whether a G7 export from a **Dexcom receiver** (rather than a phone) differs from the phone exports observed here.
- Whether Clarity ever emits `Carb`, `Exercise`, `Health` or `BG meter` row types for a G7 user. Those columns exist in the header, but no sampled G7 file contained such rows.

## 1. How to export, what comes out, and the limits

### Route

**[Dexcom]** The Dexcom Clarity User Guide (home user edition) documents the export under "Export reports":

> You can export raw glucose data values, calibration values, and events to an Excel spreadsheet saved to your computer. This generates a .csv file.
>
> To export a report from any report page:
> 1. Click the export icon at the top of the page.
> 2. Select a date range. Choose a most recent number of days or click the date boxes to choose dates for a custom view, then click OK.
> 3. Click Export, then Close.

The consumer FAQ says the same thing more briefly: "Dexcom Clarity has the option to export data as a CSV file viewable in Excel. Visit clarity.dexcom.com, log in, and click the export icon from any Reports page."

The clinic-side flow differs. On the provider portal an export is started per patient (click the patient name, then **Export**) or for the whole list (**Export all data** from the Patient List page).

### Web vs mobile

**[Dexcom]** The export is a **web feature only**. Appendix A of the user guide describes the Clarity mobile app as allowing you to "view glucose statistics, save and email reports and enter the clinic code from your clinic to allow data sharing". CSV export is not in that list. The consumer FAQ separately states the mobile app "generates PDF reports for 2, 7, 14, 30, or 90 days".

So: **PDF from mobile, CSV from web.** An automated importer has to go through the web app or through one of the API routes in section 7.

### Date range and granularity

- **[Dexcom]** Dexcom's provider FAQ states: "You can save or print all reports from Dexcom Clarity for up to 90 days of data." The export dialog uses the same date-range picker as save/print, so 90 days is the practical per-export ceiling. Dexcom does not state a 90-day limit for the export flow *specifically*, so treat this as strongly implied rather than documented.
- **[Dexcom]** The picker offers "a most recent number of days" or a custom start/end date. The user guide's digit glyphs are not extractable from the PDF, so the exact preset day counts are not quoted here. The FAQ's list for mobile PDF reports is 2, 7, 14, 30, or 90 days.
- **[Dexcom]** Data retention is open-ended: "All data uploaded to Dexcom Clarity will remain accessible as long as the product is available for use." A user with years of history can therefore pull it as a series of <=90-day exports.
- **[Observed]** Granularity is the native sensor cadence — one EGV row per 5 minutes. There is no downsampling option.
- **[Dexcom]** Clarity data is **not real time**. The user guide carries this caution: "Since the smartphone system sends data to the Dexcom server, the information is always older than the real-time data displayed on the user's CGM app or receiver."

### Units are an account setting

**[Dexcom]** "All reports are generated in the default language and units of measurement for your account." The unit is therefore not chosen at export time; it follows the account. See section 6.

### File shape quirks

- **[Observed]** Files start with a UTF-8 BOM (`\xEF\xBB\xBF`) before `Index`.
- **[Observed]** Quoting is inconsistent between files. One sampled G7 export quotes every field; another quotes nothing. A parser must not assume either.
- **[Code]** `t1dtools/wrapped` (`parsing/dexcomclarity.ts`) strips a 102-byte binary prefix when the file contains a `\x01` byte, and repairs a mangled `"ï»¿""Index"""` header. This suggests some Clarity downloads arrive with a corrupted or double-encoded header. Treat the header as needing normalisation.

## 2. Columns and column order

**[Observed]** The header is 14 columns, in this order, in every sampled file from 2019 through 2025:

| # | Column | Notes |
|---|--------|-------|
| 1 | `Index` | 1-based row counter for this file. Covers header rows too. Not a record id. |
| 2 | `Timestamp (YYYY-MM-DDThh:mm:ss)` | Naive local time. Empty on metadata rows. See section 4. |
| 3 | `Event Type` | Row discriminator. See section 3. |
| 4 | `Event Subtype` | Alert name, insulin type, or the `High`/`Low` marker on an EGV row. |
| 5 | `Patient Info` | Value for the `FirstName` / `LastName` / `DateOfBirth` rows only. |
| 6 | `Device Info` | Human-readable device name on `Device` rows, e.g. `Dexcom G7 Mobile App`. |
| 7 | `Source Device ID` | Which display device produced the row, e.g. `iOS G7`, `iOS Watch`, `Android G6`, a receiver serial, or `NOT_STORED`. |
| 8 | `Glucose Value (mg/dL)` **or** `Glucose Value (mmol/L)` | Header text carries the unit. See section 6. |
| 9 | `Insulin Value (u)` | Populated on `Insulin` rows. |
| 10 | `Carb Value (grams)` | Present in the header in every sample; not populated in any sampled G7 file. |
| 11 | `Duration (hh:mm:ss)` | Populated on `Alert` rows of subtype `Signal Loss`. |
| 12 | `Glucose Rate of Change (mg/dL/min)` **or** `(mmol/L/min)` | Populated on `Alert` rows of subtype `Rise` / `Fall`. Not populated on EGV rows in any sample. |
| 13 | `Transmitter Time (Long Integer)` | Monotonic session clock in seconds. See sections 4 and 5. |
| 14 | `Transmitter ID` | Sensor/transmitter serial. Format differs G6 vs G7 — see below. |

Only columns 8 and 12 change text, and only to carry the unit. Position and count are stable.

### G7 vs G6 differences

The **header does not change**. The **content** of three columns does. **[Observed]**

| Column | G6 era | G7 era |
|--------|--------|--------|
| `Device Info` | `Dexcom G6 Mobile App`, `Dexcom G6 Receiver`, `Dexcom Receiver with G6` | `Dexcom G7 Mobile App` |
| `Source Device ID` | Receiver serial (`PG62269399`), or `Android G6` / `iOS G6`, or `NOT_STORED` | `iOS G7`, `iOS Watch` |
| `Transmitter ID` | 6-character alphanumeric, e.g. `8GH86L`, `80X8K0`, `8CMA87` | 12-digit numeric, e.g. `109395413070` |

**[Inferred]** The `Transmitter ID` change is semantically important. On G6 the transmitter is a separate 90-day part reused across roughly nine sensor sessions, so the ID stays constant for about 90 days. On G7 the transmitter is integrated into the sensor, so **the ID changes at every sensor change** — roughly every 10 days. This is supported by the observed data: in one G7 export the ID changed and `Transmitter Time` reset from `907093` to `1708` at the same instant. `907093` seconds is 10.5 days, matching a 10-day G7 session plus its 12-hour grace period. In a G6 sample the value reached `612974` (7.1 days) with no ID change.

**[Observed] Warning — Excel corrupts the G7 transmitter ID.** One of the two G7 samples has `Transmitter ID` values of `3.47631E+11` and `8.19432E+11`. The 12-digit G7 serial was coerced to scientific notation and **lost precision permanently** because the file was opened and re-saved in a spreadsheet. Any G7 export that has passed through Excel may have an unrecoverable `Transmitter ID`. An importer should detect scientific notation in this column and refuse to use it as a key.

**[Observed]** A second, smaller variation: the `Duration` field for a `Signal Loss` alert was written `0:20:00` in one G7 file and `00:20:00` in another G7 file and in the G6 files. Zero-padding is not guaranteed.

**[Observed]** `DateOfBirth` formatting is locale-dependent: `2/23/68` in a US file, `1999-08-30` in another. It is also simply absent from some exports.

## 2a. Locale variation

**[Observed]** Every sample in section 2 is an English-language export. A real Czech-locale
export from September 2026 (G7, Android, mmol/L) shows that **the format is localized far
beyond the glucose unit**. The column count and column order are unchanged, but almost
every string differs.

### The delimiter and the decimal separator change

| Property | English samples | Czech sample |
|---|---|---|
| Field delimiter | comma | **semicolon** |
| Decimal separator | dot: `7.5` | **comma: `7,5`** |
| Field quoting | unquoted | **every field double-quoted** |
| Byte-order mark | present | present |

This is the European CSV convention. An importer must not assume a comma delimiter, and
must not parse numbers with a fixed decimal separator.

### Column names are translated

The header of the Czech export, verbatim:

```text
"Obsah";"Časové razítko (RRRR-MM-DDThh:mm:ss)";"Typ události";"Podtyp události";"Údaje pacienta";"Informace o zařízení";"ID zdrojového zařízení";"Hodnota glukózy (mmol/L)";"Hodnota inzulinu (j)";"Hodnota sacharidů (gramů)";"Trvání (hh:mm:ss)";"Rychlost změny glukózy (mmol/L/min)";"Čas vysílače (Dlouhá celočíselná hodnota)";"ID vysílače"
```

The date-format hint inside the header is itself translated: `RRRR-MM-DD` is the Czech
spelling of `YYYY-MM-DD`. The format of the data is unchanged.

### Event-type and subtype values are translated

| English | Czech |
|---|---|
| `EGV` | `Odhadovaná hodnota glukózy` |
| `Alert` | `Výstraha` |
| `Device` | `Zařízení` |
| `Sensor` | `Senzor` |
| `Activity` | `Aktivita` |
| `FirstName` / `LastName` / `DateOfBirth` | `Jméno` / `Příjmení` / `Datum narození` |
| `Low` / `High` | `Nízká` / `Vysoká` |
| `Fall` / `Rise` | `Pokles` / `Stoupání` |
| `Signal Loss` | `Ztráta signálu` |
| `Urgent Low` / `Urgent Low Soon` | `Urgentní nízká hladina glukózy` / `Urgentní riziko nízké hladiny glukózy` |

### Out-of-range values are translated strings

The claim in section 6 holds, but the strings are localized. The Czech export has 14 EGV
rows whose glucose value is the literal string `Nízká`, and the same string appears in
both `Event Subtype` and `Glucose Value`, exactly as the English samples do with `Low`.

**[Inferred]** An importer therefore cannot detect an out-of-range reading by matching the
words `Low` and `High`. It must treat any non-numeric glucose value as a sentinel and map
it through a per-locale table.

### What this means for the adapter

**[Inferred]** Column position is the only stable thing across locales. Three options, none
free:

1. **Parse positionally**, ignoring the header text. Stable across locales, but silently
   wrong if Dexcom ever changes the column order.
2. **Parse by header text**, with a translation table per locale. Fails on the first
   unseen locale.
3. **Detect the locale from the header**, then parse positionally with a locale-specific
   value map for sentinels and numbers. The delimiter and the decimal separator can be
   sniffed from the header line itself.

Option 3 matches what the evidence supports: the structure is stable, the strings are not.

## 3. Row types

**[Observed]** A row's type is given entirely by the `Event Type` column. There is no separate header block, no section delimiter, and no comment syntax — the metadata rows are ordinary CSV rows that leave `Timestamp` empty.

| `Event Type` | Meaning | Timestamp? | Key columns |
|---|---|---|---|
| `FirstName` | Patient metadata | empty | `Patient Info` |
| `LastName` | Patient metadata | empty | `Patient Info` |
| `DateOfBirth` | Patient metadata; not always present | empty | `Patient Info` |
| `Device` | Declares a display device; one block per device | empty | `Device Info`, `Source Device ID` |
| `Alert` | The device's configured alert **settings**, not alert occurrences | empty | `Event Subtype`, plus `Glucose Value` / `Duration` / `Rate of Change` as the threshold |
| `EGV` | A sensor glucose reading | **yes** | `Glucose Value`, `Transmitter Time`, `Transmitter ID` |
| `Calibration` | A fingerstick calibration entered into the CGM | **yes** | `Glucose Value`, `Transmitter ID`; `Transmitter Time` is empty |
| `Insulin` | A logged insulin dose | **yes** | `Insulin Value (u)`, `Event Subtype` (e.g. `Fast-Acting`) |
| `Sensor` | Declares the sensor generation; follows each `Device` row | empty | `Device Info` (`G6`, `G7`), `Source Device ID` |
| `Activity` | A logged activity, with its length | **yes** | `Duration (hh:mm:ss)` only; all other value columns empty |

**[Observed]** The `Sensor` and `Activity` rows above come from the Czech-locale export
(section 2a); no English sample in this note contained either. `Activity` rows are the
`Exercise`-family rows that section "What was not seen" records as absent. They do occur.
The Czech file has 25 of them, each carrying only a duration such as `01:00:00`, with no
intensity, no label, and no glucose value.

**[Observed]** In the Czech export the `Device` and `Sensor` rows appear as pairs, once per
device generation: `Dexcom G6` + `G6` with source `android G6`, then `Dexcom G7` + `G7`
with source `android G7`. The `Device Info` value is the bare product name, not the
`Dexcom G7 Mobile App` form seen in the English samples.

**[Observed]** The alert-threshold trap described below is real in this file. Its 14
`Výstraha` rows are 7 thresholds repeated for each of the 2 devices, and they carry
glucose numbers `11,1`, `9,5`, `3,9` and `3,1` in the glucose column. Filtering on a
non-empty glucose column would ingest all of them as readings.

The practical discriminator is therefore: **`Timestamp` empty means a metadata row; `Timestamp` populated means a therapy or glucose record.**

**[Observed]** The `Alert` rows are settings, not events. They come immediately after each `Device` row and enumerate the thresholds configured on that device. Observed subtypes: `Fall`, `High`, `Low`, `Signal Loss`, `Rise`, `Urgent Low`, `Urgent Low Soon`. In a G7 file with both a phone and a watch, the whole `Device` + seven `Alert` block repeats once per device. These rows carry glucose numbers in the `Glucose Value` column (the threshold, e.g. `180`) — **an importer that filters only on a non-empty glucose column will ingest alert thresholds as if they were readings.** Filter on `Event Type == 'EGV'` instead.

**[Code]** Every parser reviewed does exactly this. `im-ethz/TNN-data` (`preprocess_dexcom.py`) drops rows where `Event Type` is `Device` or `Alert` and extracts the `FirstName` / `LastName` / `DateOfBirth` rows separately. `t1dtools/wrapped` (`parsing/dexcomclarity.ts`) keeps only rows where `Event Type === 'EGV'`. `AI-READI/fairhub-pipeline` (`cgm/cgm.py`) locates the first row with a non-empty `Timestamp (YYYY-MM-DDThh:mm:ss)` and treats everything above it as header.

### What was not seen

**[Observed]** Neither *English* G7 sample contained `Calibration`, `Carbs`, `Exercise`, `Health` or
BG-meter rows. The Czech G7 export **does** contain 25 `Activity` rows, so the `Exercise` family is
confirmed to occur; see section 3. `Calibration`, `Carbs` and BG-meter rows remain unseen in any G7 file. `Calibration` rows were present in a G6 sample. G7 is factory-calibrated, and calibration is optional, so their absence in a G7 file is expected but is not proof that G7 exports can never contain them.

**[Dexcom]** Dexcom's own wording — "raw glucose data values, calibration values, and events" — confirms calibrations and events are in scope for the export in general. Dexcom does not enumerate which event types.

**[Inferred]** The presence of `Carb Value (grams)` in the header of every export, including G7, means carb rows are structurally possible. They were simply not logged by these users. Do not assume they cannot appear.

## 4. Timestamps

### Format and precision

**[Observed]** `Timestamp (YYYY-MM-DDThh:mm:ss)` is ISO-8601-like, to the second, with a literal `T`: `2025-10-21T00:04:12`. There is **no** offset suffix, no `Z`, and no fractional seconds.

**[Code]** Parsers allow for a space instead of the `T` in some files. `GlucoseDAO/glucose_data_processing` (`formats/dexcom_schema.yaml`) declares both `%Y-%m-%dT%H:%M:%S` and `%Y-%m-%d %H:%M:%S`. `t1dtools/wrapped` tries `yyyy-MM-dd'T'HH:mm:ss` and falls back to `yyyy-MM-dd HH:mm:ss`. Both variants should be accepted.

**[Observed]** EGV timestamps are **not** aligned to a 5-minute grid. The seconds field is whatever the sensor session started on, and it drifts by a second or two between readings (`00:32:20`, `00:37:20`, `00:47:19`, `00:52:20`). Do not round to a grid and do not assume equality of seconds.

### Timezone: naive local time

**[Observed]** The timestamp is **local wall-clock time on the display device, with no offset recorded.** There is no second, internal, UTC column. The only other time-bearing column is `Transmitter Time (Long Integer)`, which is not a wall clock at all.

This is proven by a real G7 export that spans the US DST fall-back on 2 November 2025 (02:00 EDT to 01:00 EST). In that file:

```
3447,2025-11-02T01:03:30,EGV,,,,iOS G7,153,,,,,485908,...
3448,2025-11-02T01:03:30,EGV,,,,iOS G7,146,,,,,489508,...
3449,2025-11-02T01:08:30,EGV,,,,iOS G7,153,,,,,486208,...
3450,2025-11-02T01:08:30,EGV,,,,iOS G7,145,,,,,489808,...
```

**Eight local timestamps each appear twice**, spanning `01:03:30` to `01:53:30` — exactly the repeated hour. The two occurrences carry different glucose values and differ in `Transmitter Time` by exactly **3600** seconds. Nothing in the timestamp itself distinguishes them.

Consequences for an importer:

- **[Inferred]** The local timestamp alone is **not** a valid key and is **not** convertible to an instant without external knowledge of the user's timezone history.
- **[Observed]** Rows are sorted primarily by the local timestamp, so the two passes of the repeated hour **interleave** in file order. Reading the file sequentially and assuming monotonic time will produce a non-monotonic series.
- **[Inferred]** On a spring-forward transition the reverse happens: an hour of local timestamps is simply absent, and looks identical to a sensor gap.
- **[Inferred]** On a **travel** timezone change the local clock jumps by the offset difference. `Transmitter Time` keeps running at 300 seconds per reading throughout, so the jump is detectable as a mismatch between the wall-clock delta and the transmitter-time delta.

**[Code]** This is a known, real-world problem, not a theoretical one. `im-ethz/TNN-data` (`preprocess_dexcom.py`) contains a function literally named `fix_errors_manual_timezone` that hand-corrects a dozen cases of wrong device dates and mis-set timezones across a research cohort, and it does so by keying on `Transmitter Time (Long Integer)` ranges — because the transmitter clock is the only trustworthy ordering in the file.

**[Inferred]** `Transmitter Time` is the reliable monotonic clock within a sensor session. It advances by exactly 300 per 5-minute reading, and gaps advance it by the corresponding multiple. It resets to a small value at each G7 sensor change.

## 5. Uniqueness and idempotent re-import

**[Observed]** There is **no stable id column.**

- `Index` is `1..N` over the whole file including the metadata rows. It is dense, unique **within one file**, and meaningless across files: exporting a different date range renumbers everything. It must not be persisted as a key.
- Dexcom does not expose the server-side record id in the CSV. (The Developer API does — see section 7.)

### Recommended synthetic key

**[Observed]** In the 3,933 EGV rows of the DST-spanning G7 sample, the pair

```
(Transmitter ID, Transmitter Time (Long Integer))
```

had **zero duplicates**, while the local timestamp alone had **eight**. The pair correctly separates the two passes of the repeated DST hour.

**[Inferred]** For EGV rows, use `(Transmitter ID, Transmitter Time)` as the natural key, with these caveats:

- It only works for `EGV` rows. `Calibration` rows have a `Transmitter ID` but an **empty** `Transmitter Time` **[Observed]**, and `Insulin` rows have neither **[Observed]**.
- On G7, `Transmitter Time` resets each sensor session, so `Transmitter Time` alone is not unique across an export — the `Transmitter ID` component is required.
- It is destroyed by Excel's scientific-notation coercion of the 12-digit G7 ID (section 2). Validate the column before trusting it.
- **[Code]** `im-ethz/TNN-data` reports having to invent an `UNK_ID` placeholder for EGV rows with a missing `Transmitter ID`, so the column is not guaranteed populated in all historical data.

**[Inferred]** A robust fallback for rows without a usable transmitter pair — calibrations, insulin, carbs, and any EGV with a corrupted ID — is a hash over `(Event Type, Event Subtype, local timestamp, Source Device ID, value column)`. This is not collision-proof across a DST fall-back and should be flagged as such.

**[Inferred]** Because `Transmitter Time` is monotonic within a session, it can also be used to *reconstruct* the missing offset information: within one sensor session, the difference between the wall-clock delta and the transmitter-time delta between consecutive rows is the timezone shift that occurred between them.

## 6. Units, out-of-range values, and gaps

### Units

**[Observed]** The unit is **stated in the column header text**, not in a separate field and not in a per-row column:

- mg/dL account: `Glucose Value (mg/dL)` and `Glucose Rate of Change (mg/dL/min)`
- mmol/L account: `Glucose Value (mmol/L)` and `Glucose Rate of Change (mmol/L/min)`

**[Dexcom]** Which one you get is decided by the account: "All reports are generated in the default language and units of measurement for your account."

**[Code]** Every parser sniffs the header for this. `t1dtools/wrapped` checks whether the file contains the literal `mg/dL` or `mmol/L` and normalises the header to a bare `Glucose Value`. `im-ethz/TNN-data` selects the column with `df.columns.str.startswith('Glucose Value')` and converts mmol/L to mg/dL when needed.

**[Observed]** mmol/L values are written to one decimal place (`6.3`, `12.0`). mg/dL values are integers.

**[Code]** `im-ethz/TNN-data` notes that merging a US (mg/dL) and an EU (mmol/L) export of the same period produces rows that differ only in the glucose value, because the mmol->mg/dL conversion does not round-trip exactly. If T1Pal ever ingests both, dedupe on the key from section 5, not on the value.

### Out-of-range encoding

**[Observed]** Out-of-range readings are encoded as the **strings** `High` and `Low`. They are **not** numeric sentinels. In a real G7 export:

```
1302,2025-10-25T11:09:13,EGV,High,,,iOS G7,High,,,,,742093,...
1473,2025-10-26T01:39:13,EGV,Low,,,iOS G7,Low,,,,,794293,...
```

Note that the marker appears in **two** columns: `Event Subtype` **and** `Glucose Value`. Both hold the same string. `Event Subtype` is otherwise empty on EGV rows.

**[Observed]** In the same file the numeric EGV values ranged from **40 to 397**, while 17 rows carried the string `Low` and 16 carried `High`. So the number `40` occurs as a genuine in-range reading in the very same file that also uses `Low`. **An importer must not treat 40 or 400 as sentinels** — the sentinel is the string, and it is unambiguous.

**[Code]** Downstream projects substitute their own numbers, and they do not agree. `im-ethz/TNN-data` replaces `Low` with `40` and `High` with `400`. `GlucoseDAO/glucose_data_processing` documents defaults of `39` for Low and `401` for High, explicitly to keep them distinguishable from in-range values. T1Pal should keep the out-of-range fact as a flag on the reading rather than fabricating a number.

**[Dexcom]** The strings match the device's own behaviour. Dexcom's FDA 510(k) summary for the G7 states the reportable range is 40–400 mg/dL, and that when G7 determines the reading is below 40 mg/dL it displays `LOW`, and above 400 mg/dL it displays `HIGH`. So `Low` means "below 40" and `High` means "above 400". This is a property of the device, not of the file format — but it confirms the CSV is faithfully carrying the device's out-of-range state rather than inventing an encoding.

### Gaps and warm-up

**[Observed]** Gaps are **missing rows**. There is no gap marker, no sensor-start row, no sensor-stop row, and no warm-up row.

In the 14-day G7 sample, 10 gaps longer than 6 minutes appear:

- Eight short gaps of 10–15 minutes, with no change of `Transmitter ID`. **[Inferred]** these are transient signal loss or a phone that was out of range.
- One 75-minute gap with no change of `Transmitter ID`. **[Inferred]** a longer disconnection, not a sensor change.
- One 94-minute gap **with** a `Transmitter ID` change and a `Transmitter Time` reset from `907093` to `1708`:

```
1849,2025-10-27T08:59:13,EGV,,,,iOS G7,245,,,,,907093,<sensor A>
1850,2025-10-27T10:33:08,EGV,,,,iOS G7,316,,,,,1708,<sensor B>
```

**[Inferred]** This is a sensor change. The G7 warm-up is 30 minutes, so the 94 minutes covers removal, insertion, and warm-up. **A sensor change is detectable only as the conjunction of a `Transmitter ID` change and a `Transmitter Time` reset.** Nothing labels it.

**[Inferred]** For T1Pal this means: a sensor session must be reconstructed by grouping consecutive EGV rows on `Transmitter ID`, and warm-up must be inferred from the leading gap of each session rather than read from the file.

## 7. Other first-party and unofficial routes to G7 data

<!--ROUTES-->

## Overlap with Tandem Source

**[Observed]** This section is measured, not inferred. It compares a real Clarity export
(90 days) with a real Tandem Source export (28 days, fully inside the Clarity window)
from the same person, the same G7 sensor, and the same period.

The t:slim X2 receives G7 readings for Control-IQ, so the same reading is present in both
exports. The two representations are not identical.

### Values agree exactly

Sampled over one hour, the glucose values match with no rounding difference. Both sources
report mmol/L to one decimal place.

### Timestamps differ by 15 to 17 seconds

Values are withheld here; this repository holds no real patient data. The offset is the
finding, and it is reproduced below against the reading interval. Times are given as
offsets from the first reading in the sampled hour.

| Reading | Clarity | Tandem | Clarity minus Tandem |
|---|---|---|---|
| 1 | `T+00:00` | `T-00:16` | +16 s |
| 2 | `T+05:00` | `T+04:44` | +16 s |
| 3 | `T+10:00` | `T+09:45` | +15 s |
| 4 | `T+15:00` | `T+14:44` | +16 s |
| 5 | `T+20:01` | `T+19:44` | +17 s |
| 6 | `T+25:00` | `T+24:45` | +15 s |

Across these six readings the glucose values were identical in both sources, to the one
decimal place that both report.

Clarity is consistently later. The offset is not constant: it varies by a few seconds
between readings.

**The cause is undocumented.** Neither Dexcom nor Tandem publishes what instant its
timestamp records. Only the measurement above is established here.

### Consequences for an importer

**[Inferred]**

- A join on an exact timestamp cannot match these records. Deduplication needs a
  tolerance window. A window of about 60 seconds separates a matched pair from the
  neighbouring reading, because the reading interval is 5 minutes.
- Value equality alone is not sufficient either. Glucose values repeat often, so
  `6.2 mmol/L` occurs many times in an hour.
- The pair `(Transmitter ID, Transmitter Time)` exists only in the Clarity export. The
  Tandem CGM file carries no record id at all, so a cross-source key cannot be built from
  a shared identifier. Matching must use time proximity plus value.
- Source precedence must be a decision, not an accident. Clarity holds the longer history
  (90 days against Tandem's 30-day cap) and carries the transmitter key, so it is the
  stronger source for glucose. This is a design decision to record, not a fact from the
  files.

### Open

- Which instant each source records: sensor time, transmitter time, or receipt time on
  the display device.
- Whether the offset is stable across sensor sessions, or drifts within one session.
- How the offset behaves across a DST transition, when both files use naive local time.

## Sources

### Dexcom documentation (primary)

| Source | URL | Era |
|---|---|---|
| Dexcom Clarity User Guide (home user) — "Export reports", "Date range selection", "Report outputs", Appendix A | https://productstore.clarity.dexcom.com/Documentation/en/Dexcom_Clarity_User_Guide_Home_User.pdf | current at retrieval, 2026-09 |
| FAQ — "Can I export raw data?" (consumer) | https://www.dexcom.com/en-us/faqs/can-i-export-raw-data | retrieved 2026-09 |
| FAQ — "Can I export raw data?" (provider) | https://provider.dexcom.com/can-i-export-raw-data | retrieved 2026-09 |
| FAQ — "Can I export raw data from Dexcom Clarity?" (CA provider) | https://ca.provider.dexcom.com/faq/can-i-export-raw-data-dexcom-clarity | retrieved 2026-09 |
| FAQ — "Using Clarity Reporting Software" (mobile PDF ranges, retention) | https://www.dexcom.com/en-us/faqs/clarity/using-clarity | retrieved 2026-09 |
| FAQ — "How do I save or print reports?" (90-day limit) | https://provider.dexcom.com/how-do-i-save-or-print-reports | retrieved 2026-09 |
| FDA 510(k) K253737 — Dexcom G7 CGM System: reportable range 40–400 mg/dL, `LOW`/`HIGH` display behaviour | https://www.accessdata.fda.gov/cdrh_docs/pdf25/K253737.pdf | FDA clearance document |

Dexcom publishes no CSV schema document. The user guide's only statement about the file's content is the sentence quoted in section 1.

### Real export files examined (observed evidence)

| File | Device era | Unit | Span | URL |
|---|---|---|---|---|
| `Files/Clarity_Export_Parmar_Henna_2025-11-03_231446.csv` in `sophia-mai/predictive-glucose-insights` | **G7**, `iOS G7` + `iOS Watch` | mg/dL | 2025-10-21 to 2025-11-03 (crosses US DST fall-back) | https://github.com/sophia-mai/predictive-glucose-insights |
| `assets/data/Dexcom_data.csv` in `GlucoTrack-Cooperatives/Diabetes_Management_Frontend` | **G7**, `iOS G7` | mg/dL | 2025-11-21 to 2025-11-30 | https://github.com/GlucoTrack-Cooperatives/Diabetes_Management_Frontend |
| `data_test/Dexcom/Clarity_Export_Madison_James_2023-08-18_170011.csv` in `leesadie/reachout-tir` | G6, `iOS G6` | **mmol/L** | 2023-08 | https://github.com/leesadie/reachout-tir |
| `datasets/Clarity_Export_00000_Subject_1_2023-10-16_235810.csv` in `dhruv-aron/Glucose360` | G6 receiver | mg/dL | 2023-07 | https://github.com/dhruv-aron/Glucose360 |
| `data/example.csv` in `GlucoseDAO/sugar-sugar` | G6, `Android G6`, contains `Calibration` rows | mg/dL | 2019-10 | https://github.com/GlucoseDAO/sugar-sugar |
| `inst/extdata/dexcom-g6/original/CLARITY_Export__111111-example.csv` in `MRCIEU/GLU` | G6 receiver, `NOT_STORED` | **mmol/L** | 2019-03 | https://github.com/MRCIEU/GLU |

Caveat: the `Glucose360` and `sugar-sugar` G6 files both begin at `Transmitter Time` `7573`, which suggests at least one of them derives from a Dexcom demo file rather than a distinct real user. The two G7 files and the two mmol/L files are clearly independent.

### Parsing code (inferential evidence)

| Repo | File | What it establishes |
|---|---|---|
| `im-ethz/TNN-data` | `preprocess_dexcom.py` | Drops `Device`/`Alert` rows; extracts `FirstName`/`LastName`/`DateOfBirth`; moves `High`/`Low` out of `Glucose Value` and `Event Subtype`; detects the unit by header prefix and converts mmol/L; `fix_errors_manual_timezone` corrects device clock and timezone errors by keying on `Transmitter Time` ranges. https://github.com/im-ethz/TNN-data/blob/master/preprocess_dexcom.py |
| `t1dtools/wrapped` | `parsing/dexcomclarity.ts` | Declares the full 14-field row type; sniffs `mg/dL` vs `mmol/L` from the file text; filters to `Event Type === 'EGV'`; accepts both `T` and space timestamp separators; strips a corrupt binary/BOM header prefix. https://github.com/t1dtools/wrapped/blob/main/parsing/dexcomclarity.ts |
| `AI-READI/fairhub-pipeline` | `cgm/cgm.py` | Finds the data start by locating the first non-empty `Timestamp (YYYY-MM-DDThh:mm:ss)`; maps `Event Type`, `Source Device ID`, `Glucose Value (mg/dL)`, `Transmitter Time`, `Transmitter ID`. https://github.com/AI-READI/fairhub-pipeline/blob/main/cgm/cgm.py |
| `GlucoseDAO/glucose_data_processing` | `formats/dexcom_schema.yaml`, `formats/dexcom/DEXCOM.md` | Declares both accepted timestamp formats; documents the High/Low substitution defaults (401/39) and calibration-removal behaviour. https://github.com/GlucoseDAO/glucose_data_processing |

<!--SOURCES_EXTRA-->

## Open questions

A single real export from the user's own G7 + t:slim X2 setup would settle most of these.

1. **Does a G7 export ever contain `Calibration` rows?** G7 allows optional calibration. No sampled G7 file had any. If it does, confirm whether `Transmitter Time` is empty as it is on G6 calibration rows — that decides whether the section 5 key works for them.
2. **Do `Carbs`, `Exercise`, or `Health` row types exist?** The `Carb Value (grams)` column is always present but was never populated. Log a carb entry in the Dexcom app, export, and look.
3. **What does a G7 export look like when the display device is a Dexcom receiver rather than a phone?** All sampled G7 rows came from `iOS G7` / `iOS Watch`. Confirm whether `Source Device ID` becomes a receiver serial and whether `Transmitter ID` formatting changes.
4. **What are the exact preset day counts in the web export date picker, and is 90 days a hard ceiling on the export specifically?** The 90-day figure is documented for save/print, not for export.
5. **Confirm the spring-forward behaviour.** The fall-back case is proven. A spring-forward export should show a missing hour that is indistinguishable from a gap except via `Transmitter Time`. Verify against a March export.
6. **Confirm travel-timezone behaviour.** Predicted: a wall-clock jump with `Transmitter Time` continuing at 300/reading. Not yet observed in a real file.
7. **Is `Transmitter Time` ever populated on non-EGV rows in a G7 export?** Only EGV rows had it in the samples.
8. **Does the EU/UK export carry any additional or renamed columns beyond the unit change?** Only the unit differed in the mmol/L samples, but both were G6-era.
9. **Does the export ever populate `Glucose Rate of Change` on EGV rows?** It was populated only on `Alert` threshold rows in every sample.

<!--OPEN_EXTRA-->
