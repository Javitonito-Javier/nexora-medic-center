# Database Draft

Tablas iniciales candidatas:

- users
- roles
- permissions
- user_permissions
- patients
- appointments
- nursing_notes
- consultations
- diagnoses
- treatments
- prescriptions
- prescription_items
- services
- cash_registers
- cash_sessions
- payments
- receipts
- receipt_items
- products
- product_presentations
- lots
- inventory_locations
- inventory_balances
- inventory_movements
- stock_transfers
- pharmacy_sales
- pharmacy_sale_items
- point_accounts
- point_movements
- discount_rules
- report_snapshots
- print_templates
- generated_documents
- audit_log

Principio: el stock no debe depender solo de un campo actual; todo ajuste importante debe quedar en movimientos auditables.
