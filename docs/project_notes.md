# Medical clinic and pharmacy system notes

The user wants to build a Flutter Web app for a medical clinic with pharmacy, billing, inventory, points, and Honduras fiscal/discount handling.

Preferred stack:

- Project name: `clinicapharma`.
- Frontend: Flutter Web, following official Flutter architecture guidance.
- State management: Riverpod.
- Backend: FastAPI.
- Database: PostgreSQL.
- Deployment/runtime: NGINX where useful.

Core modules:

- Appointment calendar and scheduling.
- Patient payments for appointments.
- Clinical/doctor-side charging for consultations and extra medical services should primarily generate internal receipts for operational control; invoice generation should remain available as an optional separate billing/fiscal module.
- Patient medical history and clinical records.
- Nursing notes and essential follow-up data.
- Pre-consultation/vital signs can be entered by nurse or doctor depending on staff availability.
- Prescription control, including optional but practically necessary printed prescriptions.
- Configurable print templates for receipts, prescriptions, and optional fiscal invoices.
- Pharmacy inventory, sales, billing, warehouse/store transfers, and lot tracking.
- Points program: every L 25.00 grants 0.05 points, where 1 point equals L 1.00.
- Points are redeemed as a discount, with a minimum redemption threshold of L 50.00 equivalent in available points.
- Internal receipts and revenue control are the priority for this first user; Honduras SAR fiscal invoicing should be designed as a separate optional module that can be enabled when needed or sold to another user.
- Pharmacy customer service should primarily generate receipts for internal sales control; invoice generation should be optional and handled by the separate billing/fiscal module.
- Doctor/clinical checkout should generate receipts for consultations and additional services by default; invoices can be handled separately when the optional billing/fiscal module is enabled.

Additional clinical details:

- Medical consultation history archive.
- Personal medical history.
- Hospitalizations.
- Clinical history subcategories.
- Diagnosis.
- Treatment.
- Printed prescription generation.
- Automatic age-based discounts.

Pharmacy and inventory details:

- There is a small warehouse/storage area for the pharmacy.
- Inventory can move from warehouse/storage to the store/sales area.
- System users need permissions for selling, entering inventory, and managing transfers.
- Track transfers between storage/warehouse and business/store area.
- Track price by entered lot.
- Lots may be boxes.
- A box can contain multiple blisters.
- Each blister can contain a specific number of pills/tablets.
- Not all blisters contain the same number of pills/tablets.
- Products may be sold by pill/tablet unit, by blister unit, or by box unit.
- Inventory model must support unit conversions per lot/product presentation rather than assuming a fixed global conversion.

Pre-consultation flexibility:

- Nursing/pre-consultation fields should be fillable by a nurse when available, but the workflow must not require a nurse.
- If there is no nurse, the doctor can fill vital signs, reason for visit, allergies, current medications, and essential pre-consultation notes directly inside the consultation flow.
- Patient status should support both flows: reception -> nursing -> doctor and reception -> doctor.
- The app should track who entered each pre-consultation value for audit purposes.

Small clinic role flexibility:

- The system must support both small-clinic mode and fuller clinic mode.
- In a small clinic, one person can have multiple roles, for example doctor + receptionist, or doctor + receptionist + clinical cashier.
- In a fuller clinic, roles can be separated between receptionist, nurse, doctor, pharmacy cashier/customer service, and admin.
- Permissions should be assigned per user, not only by a single fixed role, so one user can perform multiple workflows when authorized.
- The UI/dashboard should adapt to the user's permissions and show the modules they can use.

Roles and permissions:

- Receptionist: manages patient intake, appointment scheduling, confirmations, cancellations, and basic patient registration.
- Nurse: records vital signs, essential follow-up notes, pre-consultation observations, and nursing notes.
- Doctor can also enter pre-consultation/vital-sign data when there is no nurse available.
- Doctor: manages clinical history, diagnoses, treatments, prescriptions, follow-up plans, and consultation closure.
- Doctor or authorized clinical cashier can charge consultations and extra services, generating receipts by default and invoices only when the separate billing/fiscal module is enabled.
- Pharmacy customer service/cashier: sells pharmacy products, generates receipts by default, handles payments, and supports customer-facing pharmacy operations; invoice generation belongs to the optional billing/fiscal module.
- Admin: manages users, roles, permissions, configuration, reports, audit records, discounts, points rules, and fiscal/billing settings.
- Permissions should be role-based and auditable; sensitive actions such as invoice cancellation, inventory adjustment, discount override, prescription edits, and clinical record edits should require appropriate permission.

Cash register strategy:

- Clinic and pharmacy should have separate cash registers/cash boxes.
- Each area should support user-based cash closing: opening balance, income, discounts, refunds/cancellations if allowed, payment methods, expected cash, counted cash, difference, and closing notes.
- Reports should separate clinic income from pharmacy sales, while also allowing consolidated daily/monthly totals.
- Cash closing should be auditable by user, area, date/time, and terminal/workstation when possible.

Points and discounts:

- Points should be tracked for all registered clients/patients.
- Include a points module/listing with client, available points, total earned, total redeemed, adjustments, and movement history.
- Points are earned only from pharmacy purchases, not from medical consultations or clinical services.
- Points can be applied in pharmacy sales as a discount, not as cash.
- Minimum redemption threshold: the client must have at least L 50.00 equivalent in available points to apply points as a discount.
- No new points should be earned from the portion of a purchase paid/discounted using redeemed points.
- The cashier can apply part or all eligible points, respecting available balance and permissions.
- Point usage should appear on the receipt as a discount line.
- Points movement history should prevent double use and support audit: earned, redeemed, canceled, adjusted.
- Include reports for points generated, redeemed, pending balance, clients with most points, and sales where points were applied.

Billing strategy:

- Separate internal receipt generation from fiscal invoice generation.
- For the current user, receipts are more important than formal invoice workflows because some invoices may still be prepared manually with lot/correlative details.
- Receipts should support operational control, monthly generated revenue, profit reports, appointment/service income, pharmacy sales, and cash closing.
- The fiscal invoicing module should be independent, optional, and configurable, so it can be enabled later or offered to another user who needs full billing compliance.
- The app should keep enough structured transaction data from receipts to support future invoice generation, reports, audits, and migration to full fiscal billing.

Printing strategy:

- Add a configurable printing/templates module for receipts, invoices, and prescriptions.
- The same templates should support print and PDF export when possible.
- Thermal printing should support common paper sizes: 58 mm and 80 mm.
- Default recommendation: 80 mm for clinic/pharmacy receipts because it is more readable for products, discounts, points, totals, and payment details.
- Prescriptions should support both quick thermal printing and a more formal letter/A4-style PDF/print format.
- Fiscal invoices, when the optional billing/fiscal module is enabled, should support the required fiscal fields such as CAI/correlatives/RTN/authorized ranges if applicable and validated with SAR/accounting advice.
- Printing settings should be configurable per business/location and per document type: receipt, prescription, invoice.
- Printing settings should include paper size, margins, font size, logo on/off, number of copies, and default printer/workstation behavior where technically possible.
- The app should not assume printer configuration is automatic; Windows/browser/driver paper size setup may still be required for each thermal printer.
- For Flutter Web, design print layouts using fixed paper widths and printable HTML/PDF templates so receipts and prescriptions remain readable on thermal printers and regular printers.

PDF export and sharing:

- Receipts, prescriptions, and optional invoices should be exportable as PDF.
- PDFs should use automatic filenames that include the patient/customer/user name, document type, and date, for example `recibo_Juan_Perez_2026-06-03.pdf` or `receta_Juan_Perez_2026-06-03.pdf`.
- PDF export should support manual sharing through WhatsApp Web, email, browser download, or direct upload by the user.
- Direct WhatsApp integration is optional and can be added later; the MVP can start with PDF export/download and manual sending.
- If WhatsApp automation is added later, it may require WhatsApp Business Platform/API setup, verified business details, templates, phone number configuration, and provider costs/approval.
- The app should keep generated document records linked to the related patient, appointment, receipt, prescription, or invoice.

Dashboard and reports:

- Always create a main dashboard/home screen as the operational starting point.
- Dashboard should show patients/appointments pending for the day.
- Dashboard should show patients/appointments already attended during the day.
- Dashboard should show pharmacy sales summary for the day.
- Dashboard should show small notifications/reminders for appointments scheduled within the next two days.
- Dashboard should show other compact operational alerts, such as low stock, near-expiration lots/products, expired products, unpaid appointments, pending transfers, or pending prescriptions.
- Always include a reports module for relevant business, clinical, pharmacy, receipts, generated revenue, profits, optional billing, inventory, points, discounts, expiration alerts, and daily/monthly activity reports.

Role-based dashboards:

- Dashboard should be modular and permission-based, not one fixed screen for everyone.
- Clinic users should see clinic-relevant widgets: today's appointments, pending patients, attended patients, waiting for nurse/doctor, upcoming appointments within two days, open consultations, pending prescriptions, clinical pending payments, and clinic cash status when permitted.
- Pharmacy users should see pharmacy-relevant widgets: daily sales, open pharmacy cash register, low stock, near-expiration products/lots, expired products, pending warehouse-to-store transfers, top-selling products, customers with redeemable points, returns/cancellations when permitted, and pending user cash closing.
- Admin users should see consolidated widgets: clinic income, pharmacy sales, cash registers, user closings, low stock, expiration alerts, discounts, points generated/redeemed, and user activity.
- Users with multiple roles/permissions should either see a combined dashboard or have a view selector such as Clinic, Pharmacy, Admin.
- The same dashboard engine should show/hide widgets based on permissions and business modules enabled: clinic only, pharmacy only, or clinic + pharmacy.
- Notifications should always be useful and actionable, not decorative.

Expiration notifications:

- Dashboard must include notifications for products/lots close to expiration.
- Expiration alerts should be based on configurable windows, for example 30, 60, or 90 days before expiration.
- Alerts should identify product, lot, expiration date, current stock, and location: warehouse/storage or store/sales area.
- Expired products should be clearly separated from near-expiration products.
- Reports should include near-expiration inventory, expired inventory, and actions taken such as adjustment, removal, return to supplier, or disposal.

Recommended product principles:

- Prefer configurable rules over hard-coded business rules for discounts, points, cash handling, fiscal behavior, printing, and alerts.
- Keep modules activable/deactivable so the product can serve clinic only, pharmacy only, or clinic + pharmacy businesses.
- Prioritize audit trails for sensitive actions: cash closing, discounts, point redemption, inventory adjustments, prescription edits, clinical record edits, cancellations, and invoice/receipt changes.
- Use practical default workflows for small businesses, while allowing more separated roles as the business grows.
- When a workflow is uncertain, design it so it can be adjusted in configuration without changing core code.

Design implications:

- Model inventory with product presentations/units, lot-specific purchase/sale pricing, expiration dates, and conversion rules.
- Avoid hard-coding age discount percentages or fiscal rules; make them configurable and auditable.
- Receipt generation should be independent from invoice generation; invoice behavior must be configurable and validated against SAR requirements/accounting advice before production use.
- Keep clinical data, billing data, and inventory movements traceable with user/date audit fields.
- The app should feel polished and practical for repeated daily use by doctor, nurse, cashier, pharmacy, and admin roles.
- The home screen should prioritize daily status, pending work, alerts, and fast access to the modules each role uses most.

Imported prior chat context:

- The user installed or explored Codex skills from curated skill lists, but some requested skill names may not exist literally. When exact skills are unavailable, use the closest equivalent workflow by intent.
- Prior requested planning phases:
  1. Product planning / create-plan equivalent: executive summary, problem, MVP scope, out-of-MVP features, MVP roadmap, V1 roadmap, V2 roadmap, technical risks, dependencies, and development estimate.
  2. System design equivalent: architecture for Flutter, Riverpod, GoRouter, FastAPI, PostgreSQL, JWT, logical diagram, folders, auth flow, data flow, and best practices.
  3. Database design equivalent: PostgreSQL relational model with tables, relationships, indexes, constraints, soft delete, and audit fields.
  4. Task breakdown equivalent: user stories by epic, priority, acceptance criteria, and phase.
  5. Flutter architecture equivalent: Clean Architecture, feature-first structure, Riverpod, GoRouter, `lib/`, `features/`, `core/`, `services/`, `widgets/`, and `routes/`.
  6. Backend architecture equivalent: FastAPI structure with `app/`, `api/`, `services/`, `repositories/`, `models/`, `schemas/`, CRUD, JWT auth, roles, and permissions.
  7. API contract equivalent: OpenAPI/Swagger documentation with request, response, validation, and errors for each endpoint.
  8. UI/UX equivalent: MVP screens, navigation map, textual wireframes, reusable components, empty/loading/error states, optimized for Flutter.
  9. Testing equivalent: unit tests, widget tests, API tests, integration tests, prioritized for MVP.
  10. GitHub Actions equivalent: CI/CD for Flutter analysis, tests, lint, and build.
  11. Project generation: create Flutter app, FastAPI backend, PostgreSQL database setup, JWT auth, admin panel, docs, and tests.
- Confirmed stack:
  - Frontend: Flutter Web.
  - State management: Riverpod.
  - Routing: GoRouter.
  - HTTP client: Dio.
  - Backend: FastAPI.
  - ORM/migrations: SQLAlchemy and Alembic.
  - Database: PostgreSQL.
  - Authentication: JWT.
  - DevOps: GitHub Actions.
  - Architecture: Clean Architecture and feature-first.
- Recommended real project location:
  - Prefer `C:\dev\<project-name>` instead of OneDrive to avoid sync conflicts with generated files, build folders, virtual environments, caches, and dependency directories.
  - Recommended structure:
    - `docs/`
    - `frontend/`
    - `backend/`
    - `docker-compose.yml`
    - `README.md`
    - `.gitignore`
- Git flow for the real repo:
  - Create a clean project directory.
  - Run `git init`.
  - Add initial docs and scaffold.
  - Commit with a clear initial message.
  - Add GitHub remote later.
  - Push `main` when ready.
- Important memory rule:
  - Project memory should live in repo files, not only in chat.
  - Create a future `PROJECT_MEMORY.md` or docs memory file once the real repo exists.
  - In future chats, the user can ask Codex to read that memory file to restore context.
- Name note:
  - The confirmed project/repo name is `clinicapharma`.
  - Do not use `medical-pharmacy-system` as the final name; it was only a technical placeholder.

Official references for implementation:

- Riverpod getting started: https://riverpod.dev/docs/introduction/getting_started
- Flutter official docs: https://docs.flutter.dev/
- FastAPI official docs: https://fastapi.tiangolo.com/

Local reference books and cheat sheets:

- `C:\Users\jesus\OneDrive\Documentos\Código limpio Manual de estilo para el desarrollo ágil de software (Robert C. Martin) (Z-Library).pdf`
- `C:\Users\jesus\OneDrive\Documentos\dart-cheat-sheet (1).pdf`
- `C:\Users\jesus\OneDrive\Documentos\FastAPI Cookbook Develop high-performance APIs and web applications with Python (Giunio De Luca) .pdf`
- `C:\Users\jesus\OneDrive\Documentos\flutter-cheat-sheet.pdf`
- `C:\Users\jesus\OneDrive\Documentos\Hands-On APIs for AI and Data Science (Python Development with FastAPI) (Ryan Day) (Z-Library).epub`
- `C:\Users\jesus\OneDrive\Documentos\NGINX Cookbook, 2nd Edition for 2022 Advanced Recipes for High-Performance Load Balancing (Derek DeJonghe) (Z-Library).pdf`
- `C:\Users\jesus\OneDrive\Documentos\Patrones de Diseño (Erich Gamma, Richard Helm, Ralph Johnson etc.) (Z-Library).epub`
- `C:\Users\jesus\OneDrive\Documentos\Sumérgete en los patrones de diseño (Alexander Shvets) (Z-Library).pdf`

Reference usage guidance:

- Prefer official docs for framework-specific implementation details, especially Flutter, Riverpod, and FastAPI.
- Use local books and cheat sheets as supporting references for patterns, clean code, API structure, NGINX deployment ideas, and quick syntax checks.
- Do not depend on copied book content inside the repo; summarize design decisions in original project documentation.

Codex skills and plugin guidance:

- Use skills when available in the current Codex session and relevant to the task.
- Relevant currently available skills/plugins:
  - `github:github`: repository, pull request, issue, and GitHub workflow context.
  - `github:yeet`: publish local changes to GitHub, commit, push, and open a draft PR when requested.
  - `github:gh-fix-ci`: debug/fix failing GitHub Actions checks.
  - `github:gh-address-comments`: address PR review feedback.
  - `browser:control-in-app-browser`: verify local web targets such as localhost or file URLs.
  - `vercel:agent-browser` and `vercel:agent-browser-verify`: browser verification for local web apps/dev servers when applicable.
  - `vercel:react-best-practices`: only relevant if React/TSX is introduced later; not primary for Flutter.
  - `openai-docs`: only for OpenAI API/product questions.
  - `documents:documents`: create/edit Word or document artifacts if needed.
  - `spreadsheets:Spreadsheets`: work with CSV/XLSX reports or spreadsheet exports.
  - `presentations:Presentations`: build presentation decks if needed.
  - `imagegen`: create visual bitmap assets if the project needs generated images.
  - `skill-installer` and `skill-creator`: install or create Codex skills when explicitly requested.
- Skill intents mentioned in prior planning, even if not installed with exact names:
  - `create-plan`: product plan, MVP, roadmap, risks, dependencies, estimates.
  - `system-design`: complete architecture and data/auth flows.
  - `database-design`: PostgreSQL model, ERD, SQL, constraints, indexes, audit, soft delete.
  - `task-breakdown`: user stories, epics, acceptance criteria, MVP/V1/V2.
  - `flutter-architecture`: Flutter Clean Architecture, feature-first, Riverpod, GoRouter.
  - `fastapi`: FastAPI structure, services, repositories, models, schemas, JWT, roles, permissions.
  - `openapi`: API contracts and Swagger documentation.
  - `ui-review`: MVP screens, navigation, wireframes, reusable components, states.
  - `testing`: unit/widget/API/integration test strategy.
  - `github-actions`: CI/CD for Flutter and FastAPI.
- If an exact skill is not available, follow the closest equivalent workflow manually and document the output in repo files.











