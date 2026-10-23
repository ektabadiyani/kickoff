# Kickoff brief: Harbor Logistics Group, LLC

Ledgerline, Inc. implementation for Harbor Logistics Group, LLC. Generated from the signed contract; every requirement links back to the clause it came from.

## Headline

- **At risk:** projected go-live is **Tue 09 Feb 2027**, 16 business days after the contract date of Fri 15 Jan 2027, even if every task starts as early as possible.
- **4 high-severity contract risks** to resolve at kickoff (of 12 found).
- **10 epics, 73 tickets**, 574 delivery hours (plus 94 customer hours).
- **Estimated delivery cost $48,915** against a fee of $48,000: projected services margin **-2%**.
- **Traceability:** 50 of 50 contract references verified word for word against the document.

## Contract risks to resolve at kickoff

| | Risk | Clause | Recommendation |
|---|---|---|---|
| HIGH · contradiction | Section 2.4 commits Ledgerline to integrate 'any other systems as reasonably required by the Customer', while Section 6 excludes integrations other than NetSuite and Okta. This open-ended clause on a $48,000 fixed fee invites scope disputes and margin erosion. | §2.4 | Confirm in writing at kickoff that integrations are limited to NetSuite and Okta per Section 6, and route any other system requests through the Section 7 change order process. |
| HIGH · timeline | Go-live for three entities across two countries, with integration, PO matching and three payment rails, is targeted about 10 weeks after the effective date. The window includes US Thanksgiving and the Christmas/New Year holidays, and kickoff can slip to mid-November. Sequential dependencies (discovery, then 10 business days for data, then build, then 10 business days of UAT) leave almost no buffer. | §3.1 | Build a backward-scheduled plan at kickoff with holiday blackout dates, show the Customer the critical path, and agree a fallback such as phased go-live by entity if any dependency slips. |
| HIGH · customer dependency | Bank approval for ACH and virtual card has no due date, and bank onboarding often takes weeks. The Customer's bank setup for CAD EFT is not assigned to anyone. Either can block payments at go-live. | §4.5 | Ask the Customer at kickoff to start bank approvals immediately for ACH, virtual card and CAD EFT, set a due date in the project plan, and log a change order or phased payments go-live if approval is late. |
| HIGH · commercial | 40% ($19,200) is payable on 'completion of UAT' and 30% ($14,400) on go-live, both controlled by the Customer. Section 3.2 says delays depend on the Customer but gives no remedy, timeline relief or fee for Customer-caused delay. | §8.1 | Agree at kickoff that UAT is complete when the 10-business-day UAT window closes or deemed acceptance applies, and that Customer-caused delays trigger a change order under Section 7. Document every late dependency in status reports. |
| MEDIUM · contradiction | Deemed acceptance applies 5 business days after delivery, but the Customer has 10 business days to complete UAT. 'Material defect' is not defined. The mismatch will cause disputes over when deliverables, and the UAT payment, are accepted. | §5.1 | Agree at kickoff which period governs the configured Platform (10-day UAT vs 5-day deemed acceptance), define 'material defect' and severity levels, and issue written delivery notices to start the clock. |
| MEDIUM · ambiguous scope | Three-way matching needs receipts, but the NetSuite integration scope lists only vendors, purchase orders, GL accounts and approved bills. Tolerance thresholds are not yet defined. | §2.5 | Confirm during discovery that item receipts will be synced from NetSuite and record that in the scope baseline. Capture tolerance thresholds in a signed discovery document. |
| MEDIUM · unquantified | Data migration of 'historical vendor data' has no record volume, no defined fields, no number of loads and no acceptance criteria. 'Historical' could be read to include inactive vendors or bank details. The boundary with excluded historical invoices may blur. | §2.6 | Agree at kickoff a record count limit, field list, number of migration loads and a reconciliation-based acceptance test, and confirm vendor bank details handling. |
| MEDIUM · missing acceptance criteria | The three custom reports are 'specified by the Customer' with no due date for specifications and no complexity limit. Late or complex specs could push work past go-live. | §2.9 | Set a deadline for custom report specifications (e.g. end of discovery) and agree a complexity boundary using Platform reporting tools only, consistent with the custom development exclusion. |
| MEDIUM · customer dependency | SSO configuration requires Okta admin access, but no Customer obligation or date is listed. Section 4.1 sponsor and PM have no due date. Discovery and decisions may stall without them. | §4.1 | Request at kickoff a named Okta administrator with a date for access, and confirm the sponsor and PM by name before the first discovery workshop. |
| LOW · ambiguous scope | ACH and virtual card are enabled for 'US entities', but the contract does not say whether Harbor Warehousing LLC is a US entity. Payment rails per entity could be disputed. | §2.7 | Confirm the country and payment methods for each of the three entities at kickoff and record them in the project plan. |
| LOW · timeline | Only four 2-hour discovery workshops must cover intake, approval rules, matching tolerances and payments for three entities in two countries. That may be too little to finalize 15 workflows and thresholds. | §2.2 | Publish a workshop agenda at kickoff that allocates topics across the four sessions, and require pre-work from the Customer (current approval matrices, payment processes). |
| LOW · unquantified | End-user training videos have no number, length or topic list. Hypercare does not define priority-1, whether 30 days are calendar or business days, or which time zone sets business hours. | §2.10 | Agree at kickoff a video list with topics and length, a priority definition matrix, and the hypercare calendar and time zone. |

## Timeline

| Phase | Start | Finish | Tickets |
|---|---|---|---|
| Initiate | Mon 02 Nov 2026 | Thu 25 Feb 2027 | 14 |
| Discover | Mon 09 Nov 2026 | Wed 16 Dec 2026 | 11 |
| Configure | Mon 09 Nov 2026 | Wed 30 Dec 2026 | 15 |
| Integrate | Mon 16 Nov 2026 | Thu 07 Jan 2027 | 8 |
| Migrate | Thu 12 Nov 2026 | Tue 29 Dec 2026 | 4 |
| Test | Fri 08 Jan 2027 | Mon 01 Feb 2027 | 5 |
| Train | Thu 12 Nov 2026 | Wed 20 Jan 2027 | 5 |
| Launch | Wed 13 Jan 2027 | Tue 09 Feb 2027 | 8 |
| Hypercare | Wed 10 Feb 2027 | Thu 18 Mar 2027 | 3 |

**What sets the go-live date.** Delay any of these and go-live moves by the same amount:

1. T001 Complete internal handoff from sales (implementation lead, 1 day, 02 Nov–02 Nov)
1. T002 Customer: Name project sponsor and project manager (customer, 3 days, 03 Nov–05 Nov)
1. T003 Run project kickoff meeting (implementation lead, 1 day, 06 Nov–06 Nov)
1. T015 Publish discovery agenda and pre-work request (solutions consultant, 1 day, 09 Nov–09 Nov)
1. T016 Customer: Complete discovery pre-work (customer, 4 days, 10 Nov–13 Nov)
1. T017 Run workshop 1: invoice intake and entities (solutions consultant, 2 days, 16 Nov–17 Nov)
1. T018 Run workshop 2: approval rules and workflows (solutions consultant, 2 days, 18 Nov–19 Nov)
1. T019 Run workshop 3: PO matching and NetSuite data (solutions consultant, 2 days, 20 Nov–23 Nov)
1. T020 Run workshop 4: payments, SSO and reporting (solutions consultant, 2 days, 24 Nov–25 Nov)
1. T023 Customer: Specify up to three custom reports (customer, 5 days, 30 Nov–04 Dec)
1. T024 Write solution design document (solutions consultant, 5 days, 07 Dec–11 Dec)
1. T025 Customer: Sign off solution design (customer, 3 days, 14 Dec–16 Dec)
1. T041 Design NetSuite integration and field mapping (integration engineer, 3 days, 17 Dec–21 Dec)
1. T042 Build vendor and GL account sync (integration engineer, 3 days, 22 Dec–24 Dec)
1. T044 Build approved bill sync to NetSuite (integration engineer, 3 days, 28 Dec–30 Dec)
1. T045 Build payment status write-back to NetSuite (integration engineer, 2 days, 31 Dec–04 Jan)
1. T046 Test NetSuite integration end to end in sandbox (integration engineer, 3 days, 05 Jan–07 Jan)
1. T053 Run internal end-to-end QA (solutions consultant, 3 days, 08 Jan–12 Jan)
1. T054 Prepare UAT scripts and issue delivery notice (solutions consultant, 2 days, 13 Jan–14 Jan)
1. T055 Customer: Complete user acceptance testing (customer, 10 days, 15 Jan–29 Jan)
1. T057 Record UAT completion and sign-off (implementation lead, 1 day, 01 Feb–01 Feb)
1. T066 Hold go/no-go decision meeting (implementation lead, 1 day, 02 Feb–02 Feb)
1. T067 Promote configuration and SSO to production (solutions consultant, 2 days, 03 Feb–04 Feb)
1. T069 Load and reconcile production vendor data (data specialist, 2 days, 05 Feb–08 Feb)
1. T070 Go live for all three entities (implementation lead, 1 day, 09 Feb–09 Feb)

5 of these are customer tasks. Agree owners and dates for them at kickoff.

## Customer responsibilities

| Id | What | Due (contract) | Planned finish | Clause |
|---|---|---|---|---|
| C01 | Provide a project sponsor with decision-making authority and a day-to-day project manager. | Not stated | Wed 16 Dec 2026 | §4.1 |
| C02 | Provide NetSuite sandbox access and an administrator with integration permissions. | within five (5) business days of kickoff | Fri 13 Nov 2026 | §4.2 |
| C03 | Deliver vendor master data, open purchase orders and approval matrices in Ledgerline's templates. | within ten (10) business days of the final discovery workshop | Fri 11 Dec 2026 | §4.3 |
| C04 | Complete user acceptance testing of the configured Platform. | within ten (10) business days of Ledgerline making the configured Platform available for testing | Mon 01 Feb 2027 | §4.4 |
| C05 | Obtain the Customer's bank approval to enable virtual card and ACH payments. | Not stated | Tue 15 Dec 2026 | §4.5 |
| C06 | Specify the custom reports to be built. | Not stated | Fri 04 Dec 2026 | §2.9 |
| C07 | Agree PO matching tolerance thresholds with Ledgerline. | during discovery | Mon 30 Nov 2026 | §2.5 |

## Effort and cost

| Role | Hours | Cost |
|---|---|---|
| solutions consultant | 234 | $19,890 |
| implementation lead | 99 | $9,405 |
| integration engineer | 97 | $9,700 |
| customer | 94 | $0 |
| support engineer | 64 | $4,160 |
| trainer | 48 | $3,360 |
| data specialist | 32 | $2,400 |
| **Total** | **668** | **$48,915** |

Payment milestones:

- 30% ($14,400) on SOW signature (§8.1)
- 40% ($19,200) on Completion of UAT (§8.1)
- 30% ($14,400) on Go-live (§8.1)

## Requirements traceability

| Id | Requirement | Clause | Quote check | Tickets |
|---|---|---|---|---|
| R01 | Named implementation lead and kickoff | §2.1 | verified | T001, T003 |
| R02 | Weekly status meetings | §2.1 | verified | T004, T014 |
| R03 | Shared project plan | §2.1 | verified | T004, T014 |
| R04 | Discovery workshops | §2.2 | verified | T015, T016, T017, T018, T019, T020, T024 |
| R05 | Configure three operating entities | §2.3 | verified | T017, T024, T026, T027, T028, T029, T040, T053, T056, T063, T066, T067, T070 |
| R06 | Configure approval workflows | §2.3 | verified | T018, T024, T030, T031, T032, T040, T053, T056, T067 |
| R07 | NetSuite ERP integration | §2.4 | verified | T019, T022, T041, T042, T043, T044, T045, T046, T053, T056, T064, T068 |
| R08 | Other integrations as reasonably required | §2.4 | verified | T005 |
| R09 | Two-way and three-way PO matching | §2.5 | verified | T019, T022, T024, T033, T040, T043, T046, T053, T056, T067 |
| R10 | Migrate historical vendor data | §2.6 | verified | T007, T049, T051, T052, T069 |
| R11 | ACH and virtual card payments (US) | §2.7 | verified | T008, T020, T024, T034, T040, T053, T056, T065, T070 |
| R12 | CAD EFT payments for Canada | §2.7 | verified | T008, T020, T024, T035, T040, T053, T056, T065, T070 |
| R13 | SAML SSO with Okta | §2.8 | verified | T011, T020, T024, T047, T048, T053, T056, T067 |
| R14 | Standard AP reports | §2.9 | verified | T020, T024, T036, T040, T053, T056, T067 |
| R15 | Custom reports | §2.9 | verified | T013, T024, T037, T038, T039, T040, T053, T056, T067 |
| R16 | Train-the-trainer sessions | §2.10 | verified | T058, T059, T060, T061 |
| R17 | Recorded end-user training videos | §2.10 | verified | T012, T062 |
| R18 | 30-day hypercare | §2.11 | verified | T012, T071, T072 |

## Out of scope

- integrations with systems other than NetSuite and Okta (§6)
- migration of historical invoices or payment history (§6)
- custom development of Platform features (§6)
- on-site services (§6)
- support for entities other than those named in Section 1 (§6)

## Assumptions to confirm with the customer

- All services are delivered remotely; on-site services are excluded (Section 6).
- Two environments: one sandbox and one production Platform tenant, connected to one NetSuite sandbox and NetSuite production.
- Harbor runs a single NetSuite OneWorld account, with the three entities as subsidiaries.
- Harbor will provide NetSuite production integration credentials for cutover. The contract names only sandbox access (C02).
- Harbor Logistics Group (US) and Harbor Warehousing LLC are US entities using ACH and virtual card; Harbor Freight Canada Ltd. uses CAD EFT only. To be confirmed at kickoff (K09).
- Historical vendor data is limited to active vendors, capped at 5,000 records, with one trial load and one production load. Volume, fields and bank detail handling to be confirmed (K07).
- NetSuite item receipts are synced to support three-way matching, and treated as part of the R07 integration scope (K06).
- Vendors migrated from historical data will be de-duplicated against vendors synced from NetSuite; NetSuite remains the vendor master after go-live.
- The 15 approval workflows are split roughly 7 (US), 4 (Canada) and 4 (Warehousing), adjustable within the total of 15.
- Up to 150 end users across the three entities will be provisioned through Okta. The user count is not stated in the contract.
- End-user training is delivered as up to 5 recorded videos of no more than 10 minutes each. To be confirmed (K12).
- Each train-the-trainer session lasts up to 3 hours.
- Hypercare runs 30 calendar days from go-live, with business hours in US Eastern time. To be confirmed (K12).
- Bank approvals for ACH, virtual card and CAD EFT are received by December 18, 2026. Otherwise payments go live in a later phase under a change order (K03).
- Kickoff is held by November 16, 2026, and the final discovery workshop by November 25, 2026, so data delivery (C03) lands by about December 10, 2026.
- UAT runs over the December holiday period, with up to 8 Harbor testers. One round of defect fixes is included in the fixed fee.
- Custom reports use standard Platform reporting tools only, with no custom development.
- Integrations are limited to NetSuite and Okta. Any other system is a change order under Section 7 (K01).

## Plan quality checks

- Automated checks: 0 errors, 0 warnings.

## Method

- Requirements, dependencies and risks were extracted from the contract by Claude, with a verbatim quote for each. Every quote was then matched against the document by code, not by the model.
- The plan was generated against the delivery playbook and checked automatically for coverage (every requirement has a ticket), missing or circular dependencies, and unknown phases.
- Dates use the critical path method over business days, skipping weekends and the playbook's holidays. They assume people are available when each task can start, so they are the earliest achievable dates.
- Cost uses the playbook's loaded hourly rates (SaaS implementation).
