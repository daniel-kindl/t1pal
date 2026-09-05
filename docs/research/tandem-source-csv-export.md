# Tandem Source CSV Export

Research note. Date of research: 2026-09-05.

## Summary

**What is known.** Tandem documents that Tandem Source has exactly one CSV
export: the **Export CSV** button on the **Daily Timeline** report. It writes a
single `.csv` file (not a zip, not a set of files) named `CSV_<PatientName>` plus
the export date and time. One file holds every pump on the account, sorted by
pump serial number. The Overview and Pump Settings reports have no CSV export;
they offer **Copy as Text** and PDF only. The exported range is the report's
selected range, and Tandem Source caps a report range at 30 days.

**What is not known.** Tandem does not publish the column names, the column
order, the timestamp format, the per-column units, or any record identifier. The
three Tandem Source user guides read for this note say nothing about the file's
internal structure beyond "one CSV file, sorted by pump serial number". No
open-source project was found that parses the Tandem Source **Export CSV** file.
No public sample of that file was found.

**The closest primary evidence is from the previous era.** `tconnectsync` 1.x
parsed a *different* artifact: the CSV returned by the legacy t:connect
`tconnectws2` API endpoint `therapytimeline2csv`. Its exact column names survive
in the project's test fixtures and are reproduced below. That API and the code
were removed on 2026-06-30 after t:connect shut down. Whether Tandem Source's
browser export reuses those column names is **unverified** — do not assume it.

**Practical conclusion for T1Pal.** Nothing in the public record is strong enough
to write a Tandem Source CSV parser against. The only currently maintained
open-source path to Tandem pump data is the authenticated Tandem Source API
(`source.tandemdiabetes.com`), which returns raw pump event records, not CSV.

Confidence labels used below:

- **[Tandem]** — stated in a Tandem document.
- **[Sample]** — observed in a real export sample.
- **[Code]** — inferred from parsing code or its test fixtures.
- **[Unknown]** — no source found.

---

## 1. What an export archive contains

**[Tandem]** A single CSV file. There is no archive, no zip, and no multi-file
bundle.

| Fact | Source |
| --- | --- |
| The export control is `Export CSV`, and it appears only on the Daily Timeline report. | Personal guide AW-1014831_A p.22; Professional guide AW-1014263_B; International personal guide AW-1016501_A |
| The file goes to the browser's Downloads folder by default. | Same |
| The default filename begins with `CSV_[your name]`, e.g. `CSV_TandemTom` for Tom Tandem. The export date and time are appended so repeated exports do not overwrite each other. | Same |
| One CSV file includes all pumps and sorts data by pump serial number within the file. | Personal guide AW-1014831_A p.23; International personal guide AW-1016501_A |
| The Overview report and the Pump Settings report support `Copy as Text` (plain text to the clipboard) and PDF via the Print screen. Neither has a CSV export. | Personal guide AW-1014831_A p.22 |
| Saving from the Print screen produces a PDF, not a CSV. | Personal guide AW-1014831_A p.21 |
| The maximum viewable, and therefore exportable, report range is 30 days. | Personal guide AW-1014831_A p.23 |

The exact separator character, quoting rules, line endings, and text encoding are
**[Unknown]**.

Whether the file carries a preamble block above the data (patient name, date of
birth, generation timestamp), as the legacy t:connect export did, is
**[Unknown]** for Tandem Source.

### Contrast: the legacy t:connect export

**[Code]** The legacy `therapytimeline2csv` response was one text body containing
up to four blank-line-separated sections, each with its own header row: a
metadata preamble, plus CGM/BGM readings, IOB, basal, and bolus sections. See
`tconnectsync/api/ws2.py`, method `WS2Api.therapy_timeline_csv` and the helper
`_split_empty_sections`, at commit `e5195b2` (the last commit before the legacy
code was deleted) in <https://github.com/jwoglom/tconnectsync>.

The preamble in the project's fixture reads:

```
Tandem Diabetes Care Inc.
t:connect Therapy Timeline Data Export
Patient Name, Sample Name
Patient DOB, 1/1/1990
Report Generated On, 4/24/2021 7:50:04 PM
```

The parser identifies each section by looking at its **first data row**, not its
header: a row starting with `t:slim X2 Insulin Pump` marks the readings section,
`IOB` the IOB section, `Basal` the basal section, `Bolus` the bolus section. A
section with a header but no rows is therefore invisible to that parser.

---

## 2. Column names and column order

### Tandem Source (current)

**[Unknown].** No Tandem document lists them. No public sample was found. No
open-source parser was found.

The Tandem Source web client was also checked directly: `main.bb844c01.js` and
all 77 statically-referenced chunks under
`https://source.tandemdiabetes.com/static/` were downloaded on 2026-09-05 and
contain no occurrence of the string `csv`, `Export`, or `Timeline` in the report
sense. The reporting code is loaded as a Module Federation remote from
`https://modules.us.tandemdiabetes.com`, whose manifest returns HTTP 400 without
credentials. The column names could not be recovered from the client bundle.

### Legacy t:connect `therapytimeline2csv` (2021 era) — for lineage only

**[Code]** Exact header rows, in order, from the test fixtures in
`tests/api/test_ws2.py` at commit `e5195b2`. These fixtures describe output
generated on 2021-04-24 and were last edited on 2023-01-16.

Readings section (5 columns):

| # | Column |
| --- | --- |
| 1 | `DeviceType` |
| 2 | `SerialNumber` |
| 3 | `Description` |
| 4 | `EventDateTime` |
| 5 | `Readings (CGM / BGM)` |

IOB section (4 columns):

| # | Column |
| --- | --- |
| 1 | `Type` |
| 2 | `EventID` |
| 3 | `EventDateTime` |
| 4 | `IOB` |

Bolus section (41 header names, in order):

| # | Column | # | Column |
| --- | --- | --- | --- |
| 1 | `Type` | 22 | `ExtendedBolusIsComplete` |
| 2 | `Description` | 23 | `EventDateTime` |
| 3 | `BG` | 24 | `RequestDateTime` |
| 4 | `IOB` | 25 | `BolusType` |
| 5 | `BolusRequestID` | 26 | `BolusRequestOptions` |
| 6 | `BolusCompletionID` | 27 | `StandardPercent` |
| 7 | `CompletionDateTime` | 28 | `Duration` |
| 8 | `InsulinDelivered` | 29 | `CarbSize` |
| 9 | `FoodDelivered` | 30 | `UserOverride` |
| 10 | `CorrectionDelivered` | 31 | `TargetBG` |
| 11 | `CompletionStatusID` | 32 | `CorrectionFactor` |
| 12 | `CompletionStatusDesc` | 33 | `FoodBolusSize` |
| 13 | `BolusIsComplete` | 34 | `CorrectionBolusSize` |
| 14 | `BolexCompletionID` | 35 | `ActualTotalBolusRequested` |
| 15 | `BolexSize` | 36 | `IsQuickBolus` |
| 16 | `BolexStartDateTime` | 37 | `EventHistoryReportEventDesc` |
| 17 | `BolexCompletionDateTime` | 38 | `EventHistoryReportDetails` |
| 18 | `BolexInsulinDelivered` | 39 | `NoteID` |
| 19 | `BolexIOB` | 40 | `IndexID` |
| 20 | `BolexCompletionStatusID` | 41 | `Note` |
| 21 | `BolexCompletionStatusDesc` | | |

Basal section: the fixture contains no basal section, so its header row is
**[Unknown]**. Two column names are known from the parser: `EventDateTime` and
`BasalRate`, read by `TConnectEntry.parse_csv_basal_entry` in
`tconnectsync/parser/tconnect.py` at commit `e5195b2`.

**Known defect in the bolus section.** In the fixture, the bolus header row has
41 names but each data row parses to 43 fields. One field is a trailing empty
value from a trailing comma; the other is a real, unnamed column that appears
immediately after `IsQuickBolus`. The result is that positional header mapping
shifts everything from position 37 onward by one: the value that belongs to
`EventHistoryReportEventDesc` lands in `EventHistoryReportDetails`, and the pump
event index lands in the field labelled `Note`. This shift is visible in the
fixture's own expected-output dictionary (`PARSED_DATA`), so the project shipped
with the misalignment. Treat header-position mapping of that section as unsafe.
The readings section also has a trailing comma on every data row (5 header names,
6 parsed fields), which is harmless.

---

## 3. Timestamps and timezone

### Tandem Source CSV

**[Unknown]** for the export file itself: no documented format, no sample.

**[Tandem]** The user guides describe how Tandem Source handles a pump clock
change, which is the closest thing to DST/timezone guidance published:

- If the pump's time or date changed inside the selected range, Tandem Source
  treats the affected day(s) as **incomplete**, and splits the Daily Timeline
  graphs at the change. A date change affects multiple days.
- This applies to backwards changes too, and the guide's own example is a
  traveller moving from Eastern to Pacific time.
- A banner is shown on the Overview and Daily Timeline reports naming the change
  and the affected days.

Source: Personal guide AW-1014831_A p.23 ("Time/Date Change") and p.31 (FAQ).
The guides describe the on-screen behaviour. Whether the CSV carries any marker
for the change is **[Unknown]**.

There is no mention anywhere in the three guides of a timezone column, a UTC
offset, or a DST rule.

### What Tandem's own data model does

**[Code]** Tandem timestamps are naive pump-local wall-clock values with no
offset attached, at every layer that has been reverse-engineered:

- `tconnectsync/api/tandemsource.py`, helper `naive_local_to_utc` (v3.0.1,
  commit `7c4b2f4`): "The BFF sends `maxDateOfEvents` / `availableDataRange.start`
  with no tz (e.g. `2022-02-16T22:45:58`) even though they are the pump's local
  wall-clock time." The tool shifts them by a user-configured `TIMEZONE_NAME`.
- `tconnectsync/eventparser/raw_event.py`, `RawEvent.timestamp`: "Event
  timestamps do not have TZ data attached to them when parsed, but represent the
  user's time zone setting." The raw binary field is seconds since a Tandem
  epoch of `1199145600` (2008-01-01T00:00:00Z), parsed as UTC and then forcibly
  relabelled with the user's configured zone.
- The JSON pump-log path reads `event["pumpDateTime"]` and the comment calls it
  "naive local wall-clock, no tz".
- The README states: "Tandem's (to us, undocumented) APIs are a bit loose with
  timezones."

**[Code]** In the legacy CSV, `EventDateTime` was ISO-8601 to the second with no
offset — `2021-04-01T00:01:33` in the fixtures — and the parser comment says
plainly "`EventDateTime` is stored in the user's timezone"
(`tconnectsync/parser/tconnect.py`, `parse_cgm_entry`, `parse_iob_entry`,
`parse_csv_basal_entry`, `parse_bolus_entry`). Precision is whole seconds; there
are no sub-second digits.

**Consequence.** Because the timestamp is naive local time, a fall-back DST
transition produces one duplicated wall-clock hour that cannot be disambiguated
from the timestamp alone, and a spring-forward produces a one-hour gap. No source
found describes any handling for this. Any importer must take the timezone from
outside the file.

---

## 4. Record identity and idempotent re-import

### Tandem Source CSV

**[Unknown].** There is no published evidence of an id column in the Tandem
Source export.

### Legacy t:connect CSV

**[Code]** The legacy bolus section carried several candidate identifiers:
`BolusRequestID`, `BolusCompletionID`, `BolexCompletionID`, `IndexID`, `NoteID`.
The fixture shows `BolusRequestID` and `BolusCompletionID` as decimal-formatted
values such as `7001.000`, and `IndexID` as a large monotonic integer such as
`1181649`. The IOB section carried `EventID`. The readings section carried **no**
id at all — only `DeviceType`, `SerialNumber`, `Description`, `EventDateTime`,
and the value. So even in the legacy format a CGM row had to be keyed
synthetically, on `(SerialNumber, EventDateTime, Description)`.

Note that `tconnectsync` never used those ids for deduplication. Its Nightscout
sync deduplicates by comparing against the last uploaded entry's timestamp.

### What the Tandem Source API offers instead

**[Code]** Every pump event in the Tandem Source event stream carries a
`sequenceNumber` (`seqNum`, a 32-bit field at byte offset 6 of each 26-byte raw
event) alongside a `sequenceGroup`. `tconnectsync` deduplicates pump clock-change
records on the tuple `(sequenceGroup, sequenceNumber)` —
`TandemSourceApi.pump_clock_changes` in `tconnectsync/api/tandemsource.py`,
v3.0.1. That pair, scoped to a pump serial or device id, is the natural stable
key for Tandem pump data. **[Unknown]** whether either value is exposed in the
CSV export.

**Recommendation.** Until a real export sample is inspected, assume a synthetic
key is required, and design the importer to key on
`(pump serial number, event timestamp, event type, value)` with an explicit
re-import reconciliation step, rather than assuming a stable per-row id exists.

---

## 5. Representation of each data type

For the Tandem Source CSV specifically, the per-record encoding is **[Unknown]**.
What *is* documented is the set of things the Daily Timeline report renders, and
the CSV is described as an export of "the report contents", so this list bounds
what the file can plausibly contain.

**[Tandem]** Daily Timeline report elements (Personal guide AW-1014831_A p.19–20):

| Element | Documented description |
| --- | --- |
| Food Bolus | Bolus delivered from carb grams entered and carb ratio. Always accompanied by the Carbs element. |
| Correction Bolus | Manually delivered correction, from the entered BG, the correction factor, and the time-of-day target. |
| Control-IQ Technology Bolus Events | A Control-IQ automatic correction bolus was initiated. |
| Food Bolus with Correction Bolus | A food bolus delivered with a correction added to or subtracted from it. |
| Extended Bolus | Bolus delivered for food or override boluses over an extended period. |
| Quick Bolus | Bolus delivered using the Quick Bolus feature. |
| Override Bolus | Bolus where the user increased, decreased, or manually entered the units. |
| Profile Basal | Continuous rate from the pump Personal Profiles, "measured in units per hour". |
| Temporary Basal | Basal for a short period, "set in the pump as a percentage of the Profile Basal rate". Can be higher or lower. |
| Control-IQ Technology Basal Insulin Adjustment | Control-IQ increasing or decreasing basal. |
| Automatic Suspensions | Predictive technology suspended delivery; pump delivering 0 units/hour. |
| Carbs | "The total amount of carbs used to deliver a food bolus." |
| Exercise Activities | An Exercise Activity was enabled while Control-IQ was active. |
| Sleep Activities | A Sleep Activity was enabled while Control-IQ was active. |
| Cartridge Changes | Cartridge changed, tubing filled, or cannula filled. |
| Lost CGM Connection | Pump not communicating with CGM for an extended period while Control-IQ was active. |
| CGM Alerts | CGM readings stopped for any reason (out of range, transmitter error). |
| Pump Alarms | A pump alarm or malfunction occurred and deliveries stopped. |
| Manual Stop | The user manually stopped insulin deliveries. |
| Pump Shutdown | The pump was powered off and all deliveries stopped. |

**[Tandem]** Two constraints that matter for import correctness:

- "Tandem Source only displays completed boluses. If a bolus was still in
  progress during your last pump data upload, that bolus will not appear in any
  reports." (AW-1014831_A p.18). An in-flight extended bolus is therefore
  absent, and will appear only in a later export.
- BG meter readings are described only as "BG entries on the pump". The reports
  fall back to showing BG entries when no CGM data exists (AW-1014831_A p.18).
  Whether the CSV separates CGM from BG rows is **[Unknown]**; the legacy format
  did so with a single `Description` value (`EGV` for CGM) inside one shared
  `Readings (CGM / BGM)` column.

**[Tandem]** Pump settings and Personal Profiles are **not** in any CSV. They
live in the Pump Settings report, which offers only `Copy as Text` and PDF, and
which always shows the most recently uploaded pump's settings (AW-1014831_A
p.20–22). Profiles, carb ratios, correction factors, and targets are therefore
not obtainable as CSV from Tandem Source.

**[Code]** Legacy t:connect mapping, for lineage:

| Concept | Legacy columns |
| --- | --- |
| CGM reading | readings section, `Description` = `EGV`, value in `Readings (CGM / BGM)` |
| BG meter reading | readings section, a different `Description` value (not present in the fixture) |
| Bolus, delivered total | `InsulinDelivered` |
| Bolus, requested total | `ActualTotalBolusRequested` |
| Bolus, food component | `FoodDelivered`, requested as `FoodBolusSize` |
| Bolus, correction component | `CorrectionDelivered`, requested as `CorrectionBolusSize` |
| Bolus calculator inputs | `BG`, `IOB`, `CarbSize`, `TargetBG`, `CorrectionFactor` |
| Carb ratio | not a column; embedded in the free-text detail string, e.g. `CF 1:30 - Carb Ratio 1:6 - Target BG 110` |
| Extended (dual-wave) bolus | the `Bolex*` column family: `BolexSize`, `BolexStartDateTime`, `BolexCompletionDateTime`, `BolexInsulinDelivered`, `BolexIOB`, `BolexCompletionStatusID`, `BolexCompletionStatusDesc`, `ExtendedBolusIsComplete`; split governed by `StandardPercent` and `Duration` |
| Quick bolus / override | `IsQuickBolus`, `UserOverride` |
| Basal rate | basal section, `BasalRate` |
| Temp basal, suspends | **not in the CSV**; delivered by separate JSON endpoints (`basalsuspension`, with `SuspendReason` in `site-cart`, `basal-profile`, `manual`, `previous`, `alarm`) and by the Control-IQ endpoints |
| Carbohydrates | `CarbSize`, on the bolus row only — no standalone carb-entry rows |
| Alarms, device events | **not in the CSV** |

**[Code] Important gap in the legacy format.** The docstring on
`WS2Api.therapy_timeline_csv` states: "Basal data does NOT appear for the
specified time range if using Control-IQ. The ControlIQ API endpoints must be
used for basal data instead." For a Control-IQ user, the legacy CSV's basal
section was empty.

**[Sample], indirect.** The AZT1D dataset (25 patients, Mayo Clinic Arizona,
December 2023 – April 2024, Tandem t:slim X2) reports the same split: the paper
says the pump provided "a CSV file" with "blood glucose readings at five-minute
interval, carb sizes, target blood glucose levels, bolus logs (including sizes
and types)", while "hourly basal rates and device modes (regular/sleep/exercise)"
were only available in **PDF**, and had to be recovered by OCR. That is
independent evidence that basal rates were not in the CSV for Control-IQ users in
that era. The dataset's variable names — `EventDateTime`, `BolusType`,
`CorrectionDelivered`, `TotalBolusInsulinDelivered`, `FoodDelivered`, `CarbSize`,
`CGM`, `Basal`, `DeviceMode` — are the authors' harmonised names, but four of
them are verbatim legacy t:connect column names. The paper does not say whether
the export came from t:connect or Tandem Source, and the collection window spans
the transition.

Corroborating: the Glucose-ML-Project loader for AZT1D branches on whether a file
has a `Readings (CGM / BGM)` column or a `CGM` column, renaming `EventDateTime`
to `timestamp` in both cases — so both column spellings occur across the AZT1D
raw files.

---

## 6. Units

**[Tandem]** Glucose units are a property of the account's region and locale, not
of the file:

- The US personal guide states three times that "All glucose values shown in the
  [Overview / Daily Timeline / Pump Settings] report are measured in mg/dL"
  (AW-1014831_A p.18, p.19, p.20), and gives the default target range as
  70–180 mg/dL.
- Tandem publishes mmol/L variants of the same guides for international markets.
  The international English personal guide (AW-1016501_A, © 2025) drops the
  mg/dL sentences entirely.

So a Tandem Source export cannot be assumed to be mg/dL. **[Unknown]** whether
the CSV names its glucose unit anywhere in the file.

**[Tandem]** Insulin is in units; basal rate is in units per hour ("Profile Basal
… is measured in units per hour", AW-1014831_A p.19). Temp basal is expressed as
a **percentage** of the profile rate, not as an absolute rate. Carbohydrates are
in grams ("the number of carb grams entered", same page).

**[Code]** In the legacy CSV, no column carried a unit suffix in its name and no
unit row was present. `Readings (CGM / BGM)` values in the fixture are integers
in the 130–235 range, consistent with mg/dL but not labelled as such. Bolus and
IOB values are two-decimal strings; `CarbSize`, `TargetBG`, and
`CorrectionFactor` are plain numbers. Units were entirely implicit.

---

## Sources

Tandem primary documents (all read 2026-09-05):

1. *Tandem Source Platform User Guide — Personal*, document AW-1014831_A, © 2024
   Tandem Diabetes Care, 38 pages, mg/dL edition.
   <https://www.tandemdiabetes.com/docs/default-source/user-guide/user-guide-tandem-source-personal-mgdl-aw1014831.pdf?sfvrsn=73553bd7_163>
   Relevant pages: 18–23 (report details, Save or Print Report, Exporting Data
   from Report Screens, Select Data Set, Time/Date Change, Multiple Pumps),
   30–32 (FAQ).
2. *Tandem Source Platform User Guide — Professional*, document AW-1014263_B,
   © 2024 Tandem Diabetes Care, 38 pages. Note: the URL slug says
   `professional-mmoll-intl`, but the extracted body text states mg/dL
   throughout and the document number is AW-1014263_B. Flagging the mismatch
   rather than resolving it.
   <https://www.tandemdiabetes.com/docs/default-source/user-guide/user-guide-tandem-source-professional-mmoll-intl-aw1013218d91c939775426a79a519ff1200a9fd393c5ca99775426a79a519ff1300a9fd39.pdf?sfvrsn=535ef9d7_57>
3. *Tandem Source Platform User Guide — Personal, English International*,
   document AW-1016501_A, © 2025 Tandem Diabetes Care, 19 pages.
   <https://www.tandemdiabetes.com/docs/default-source/user-guide/user-guide-tandem-source-personal-en-intl-aw1016501.pdf?sfvrsn=b57cd8d7_4>
4. Tandem Source product page.
   <https://www.tandemdiabetes.com/products/software-apps/tandem-source>
5. Tandem Source support centre index. Checked for an export/CSV article; none
   exists among the 32 listed articles.
   <https://www.tandemdiabetes.com/support-center/software-and-apps/tandem-source>
6. Tandem Source web client, `https://source.tandemdiabetes.com/`, page shell
   plus `static/main.bb844c01.js` plus all 77 referenced chunks, downloaded
   2026-09-05. No CSV-generating code present; report modules are loaded from
   `https://modules.us.tandemdiabetes.com` (HTTP 400 unauthenticated).

Parsing code:

7. `jwoglom/tconnectsync` — <https://github.com/jwoglom/tconnectsync>. Read at
   `master` = `7c4b2f4` (tag v3.0.1, 2026-07-21) and at `e5195b2` (2026-06-30),
   the last commit containing the legacy t:connect code.
   - `tconnectsync/api/tandemsource.py` (v3.0.1) — the live Tandem Source client.
     `naive_local_to_utc` documents that Tandem's BFF sends naive pump-local
     timestamps. `pump_clock_changes` deduplicates on
     `(sequenceGroup, sequenceNumber)`. `DEFAULT_EVENT_IDS` lists the 55 pump
     event ids the tool requests.
   - `tconnectsync/eventparser/raw_event.py` (v3.0.1) — 26-byte raw event layout,
     Tandem epoch `1199145600`, `seqNum` at byte offset 6, and the comment that
     event timestamps carry no timezone.
   - `tconnectsync/eventparser/events.py` (v3.0.1) — 59 `Lid*` event classes
     covering CGM data per sensor family, BG readings, bolus request/activate/
     complete/bolex, basal delivery and rate change, carbs entered, cartridge and
     cannula fill, alarms, alerts, malfunctions, pumping suspended/resumed, and
     `LidTimeChanged` / `LidDateChanged`.
   - `tconnectsync/api/ws2.py` at `e5195b2` — the legacy `therapytimeline2csv`
     client, its four-section splitting, and the Control-IQ basal caveat.
   - `tests/api/test_ws2.py` at `e5195b2` — the legacy CSV fixtures with the
     exact header rows quoted in section 2. Fixture data is dated 2021-04-24; the
     file was last modified 2023-01-16 (commit `85303bc`).
   - `tconnectsync/parser/tconnect.py` at `e5195b2` — `TConnectEntry`, the
     column-by-column reader, including `parse_csv_basal_entry` (`EventDateTime`,
     `BasalRate`) and the `SuspendReason` enumeration.
   - `README.md` (v3.0.1) — "Tandem APIs" section; t:connect shutdown from
     2024-09-30; the timezone-looseness warning.
8. `nightscout/nightscout-connect` — <https://github.com/nightscout/nightscout-connect>.
   Its `lib/sources` directory contains dexcomshare, glooko, librelinkup,
   minimedcarelink and nightscout. **No Tandem source exists.**

Derived datasets, used as indirect evidence only:

9. Arefeen et al., *AZT1D: A Real-World Dataset for Type 1 Diabetes*,
   arXiv:2506.14789. <https://arxiv.org/html/2506.14789v1>. 25 patients,
   Tandem t:slim X2 with Dexcom G6 Pro, December 2023 – April 2024. States the
   pump supplied a CSV (glucose at five-minute intervals, carb sizes, target BG,
   bolus logs with sizes and types) and a PDF (hourly basal rates, device modes)
   requiring OCR. Does not name the export platform.
   Dataset: <https://data.mendeley.com/datasets/gk9m674wcx/1>.
10. `Augmented-Health-Lab/Glucose-ML-Project`,
    `2_Harmonize-cgm-datasets/AZT1D/AZT1D_extract-glucose-data.py`.
    <https://github.com/Augmented-Health-Lab/Glucose-ML-Project>. Branches on
    `Readings (CGM / BGM)` versus `CGM` as the glucose column, with
    `EventDateTime` as the timestamp column in both branches.
11. `nicholas-camarda/bayesian-t1dm`, `src/bayesian_t1dm/ingest.py`.
    <https://github.com/nicholas-camarda/bayesian-t1dm>. A heuristic
    multi-vendor ingester; it matches `readings (cgm / bgm)`, `carbsize`,
    `basalrate`, `actualtotalbolusrequested` and `completiondatetime`
    case-insensitively. Not authoritative about any one format, but it confirms
    those legacy names still circulate in real files. It also defaults naive
    timestamps to a `TIMEZONE_NAME` environment variable.

Searches that returned nothing, recorded so the negative result is auditable:
GitHub code search for `"Tandem Source" csv export`, `"tandemsource" csv`,
`"Therapy Timeline Data Export"`, `"Tandem Source" pump csv parser`,
`"CSV_" tandem export pump`, `"Tandem Mobi" csv columns` — all zero results on
2026-09-05.

---

## Open questions

A single real Tandem Source Daily Timeline CSV export would settle all of these.
Until one is inspected, none should be guessed at in code.

1. **Shape.** Is it one flat table with a `Type`-style discriminator column, or
   several blank-line-separated sections like the legacy t:connect export? Is
   there a metadata preamble above the data?
2. **Exact header row(s)**, verbatim and in order, for every section. Whether
   `Readings (CGM / BGM)`, `EventDateTime`, `CarbSize`, and the `Bolex*` family
   survived the t:connect to Tandem Source migration.
3. **Whether the bolus header/data misalignment observed in the legacy fixture
   still exists.** If it does, positional parsing must be avoided.
4. **Timestamp format.** ISO-8601 with `T`, or a locale-formatted date? Seconds
   or minutes precision? Any offset or `Z` suffix? Any separate timezone column?
5. **What a pump clock change looks like in the file** — a marker row, a
   duplicated span, a gap, or nothing at all. And what a DST fall-back hour looks
   like.
6. **Whether any stable id column exists** (`sequenceNumber`, `sequenceGroup`,
   `IndexID`, `BolusCompletionID`, or similar), and whether it is unique per pump
   or globally.
7. **Whether basal rate rows are present for a Control-IQ user.** This was the
   single biggest gap in the legacy format, and AZT1D suggests it persisted into
   2024.
8. **Whether temp basals, suspends, alarms, alerts, cartridge changes, exercise
   and sleep activities appear as rows**, given that the report renders them.
9. **Whether standalone carbohydrate entries exist**, or whether carbs appear
   only as a `CarbSize` field on a bolus row.
10. **Whether the glucose unit is stated in the file** for an mmol/L account, and
    whether the numeric format changes (one decimal place for mmol/L).
11. **How the file distinguishes CGM from BG meter readings**, and how it labels
    a Control-IQ automatic correction bolus versus a user bolus.
12. **Encoding, line endings, and quoting** — UTF-8 with or without BOM, CRLF or
    LF, and whether the free-text detail fields can contain embedded commas or
    newlines.
13. **Multi-pump layout.** The guides say one file sorts by pump serial number.
    Is the serial a column on every row, or a section header?
