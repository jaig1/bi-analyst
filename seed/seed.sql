-- ============================================================
-- AI BI Analyst — SMB Retailer Sample Schema & Data
-- Run once against your Neon database:
--   psql $DATABASE_URL -f seed/seed.sql
-- ============================================================

-- ── Tables ───────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS categories (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS products (
    id           SERIAL PRIMARY KEY,
    name         TEXT NOT NULL,
    sku          TEXT UNIQUE NOT NULL,
    category_id  INTEGER REFERENCES categories(id),
    unit_price   NUMERIC(10,2) NOT NULL,
    unit_cost    NUMERIC(10,2) NOT NULL,  -- for margin calculations
    stock_qty    INTEGER NOT NULL DEFAULT 0,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS customers (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    email       TEXT UNIQUE NOT NULL,
    region      TEXT NOT NULL,            -- 'North', 'South', 'East', 'West'
    segment     TEXT NOT NULL DEFAULT 'SMB', -- 'SMB', 'Enterprise', 'Consumer'
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS orders (
    id           SERIAL PRIMARY KEY,
    customer_id  INTEGER REFERENCES customers(id),
    status       TEXT NOT NULL DEFAULT 'completed', -- 'completed', 'refunded', 'pending'
    region       TEXT NOT NULL,
    ordered_at   TIMESTAMPTZ NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS order_items (
    id          SERIAL PRIMARY KEY,
    order_id    INTEGER REFERENCES orders(id),
    product_id  INTEGER REFERENCES products(id),
    quantity    INTEGER NOT NULL,
    unit_price  NUMERIC(10,2) NOT NULL,  -- price at time of sale
    unit_cost   NUMERIC(10,2) NOT NULL   -- cost at time of sale
);

-- Audit log written by the application for every query
CREATE TABLE IF NOT EXISTS query_audit (
    id               SERIAL PRIMARY KEY,
    user_id          TEXT NOT NULL,
    user_role        TEXT NOT NULL,
    question         TEXT NOT NULL,
    generated_sql    TEXT NOT NULL,
    row_count        INTEGER,
    execution_ms     INTEGER,
    chart_type       TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ── Seed Data ────────────────────────────────────────────────

TRUNCATE order_items, orders, customers, products, categories, query_audit RESTART IDENTITY CASCADE;

-- Categories
INSERT INTO categories (name, description) VALUES
    ('Electronics',   'Gadgets, accessories, and tech hardware'),
    ('Office',        'Stationery, furniture, and workspace gear'),
    ('Software',      'SaaS licenses and downloadable software'),
    ('Accessories',   'Cables, cases, and peripheral add-ons'),
    ('Services',      'Professional services and support packages');

-- Products (with margin baked in)
INSERT INTO products (name, sku, category_id, unit_price, unit_cost, stock_qty) VALUES
    ('Wireless Keyboard',       'EL-001', 1,  79.99,  32.00, 120),
    ('4K Monitor 27"',          'EL-002', 1, 449.99, 210.00,  45),
    ('Ergonomic Mouse',         'EL-003', 1,  59.99,  22.00, 200),
    ('USB-C Hub 7-port',        'AC-001', 4,  49.99,  18.00, 300),
    ('Standing Desk',           'OF-001', 2, 699.99, 380.00,  20),
    ('Desk Chair Pro',          'OF-002', 2, 399.99, 175.00,  35),
    ('Webcam HD 1080p',         'EL-004', 1,  89.99,  38.00, 150),
    ('Project Mgmt License',    'SW-001', 3, 199.99,  12.00, 999),
    ('Antivirus Suite (1yr)',   'SW-002', 3,  49.99,   5.00, 999),
    ('Cable Management Kit',    'AC-002', 4,  19.99,   7.00, 500),
    ('Laptop Stand Aluminium',  'AC-003', 4,  39.99,  14.00, 250),
    ('IT Support Package',      'SV-001', 5, 299.99,  80.00, 999),
    ('Noise-Cancel Headset',    'EL-005', 1, 129.99,  55.00,  80),
    ('Label Printer',           'OF-003', 2, 159.99,  70.00,  60),
    ('Cloud Backup (1yr)',       'SW-003', 3,  89.99,   8.00, 999);

-- Customers (spread across regions, created over past 18 months)
INSERT INTO customers (name, email, region, segment, created_at) VALUES
    ('Acme Supplies',         'orders@acme.example',       'North',  'SMB',        now() - interval '18 months'),
    ('Bright Ideas Co',       'hello@brightideas.example', 'South',  'SMB',        now() - interval '16 months'),
    ('ClearPath Ltd',         'info@clearpath.example',    'East',   'Enterprise', now() - interval '14 months'),
    ('DeltaForce Trading',    'buy@deltaforce.example',    'West',   'SMB',        now() - interval '13 months'),
    ('Echo Systems',          'ops@echosys.example',       'North',  'Enterprise', now() - interval '12 months'),
    ('Foundry Works',         'admin@foundry.example',     'South',  'SMB',        now() - interval '11 months'),
    ('GreenLeaf Organics',    'shop@greenleaf.example',    'East',   'Consumer',   now() - interval '10 months'),
    ('Harbor Freight Tools',  'orders@harbor.example',     'West',   'SMB',        now() - interval '9 months'),
    ('Ironclad Consulting',   'billing@ironclad.example',  'North',  'Enterprise', now() - interval '8 months'),
    ('JetSet Media',          'tech@jetset.example',       'South',  'Consumer',   now() - interval '7 months'),
    ('KineticEdge',           'po@kineticedge.example',    'East',   'SMB',        now() - interval '6 months'),
    ('Luminary Labs',         'ops@luminary.example',      'West',   'Enterprise', now() - interval '5 months'),
    ('MapleCrest Bakery',     'mgr@maplecrest.example',    'North',  'Consumer',   now() - interval '4 months'),
    ('NorthStar Logistics',   'it@northstar.example',      'South',  'SMB',        now() - interval '3 months'),
    ('Orion Financial',       'tech@orionfi.example',      'East',   'Enterprise', now() - interval '2 months');

-- Helper: generate realistic orders spread over the last 12 months
-- Each customer gets 2–6 orders, items chosen to support the PDF example queries.

-- Acme Supplies — heavy Electronics buyer, last order 95 days ago (churned)
INSERT INTO orders (customer_id, status, region, ordered_at) VALUES
    (1, 'completed', 'North', now() - interval '11 months'),
    (1, 'completed', 'North', now() - interval '8 months'),
    (1, 'completed', 'North', now() - interval '95 days');

INSERT INTO order_items (order_id, product_id, quantity, unit_price, unit_cost) VALUES
    (1, 1, 5, 79.99, 32.00), (1, 3, 5, 59.99, 22.00),
    (2, 2, 2, 449.99, 210.00), (2, 7, 3, 89.99, 38.00),
    (3, 1, 10, 79.99, 32.00), (3, 4, 8, 49.99, 18.00);

-- Bright Ideas Co — Office buyer, active
INSERT INTO orders (customer_id, status, region, ordered_at) VALUES
    (2, 'completed', 'South', now() - interval '10 months'),
    (2, 'completed', 'South', now() - interval '5 months'),
    (2, 'completed', 'South', now() - interval '30 days');

INSERT INTO order_items (order_id, product_id, quantity, unit_price, unit_cost) VALUES
    (4, 5, 1, 699.99, 380.00), (4, 6, 1, 399.99, 175.00),
    (5, 6, 2, 399.99, 175.00), (5, 14, 1, 159.99, 70.00),
    (6, 5, 2, 699.99, 380.00), (6, 11, 4, 39.99, 14.00);

-- ClearPath Ltd — Software + Services
INSERT INTO orders (customer_id, status, region, ordered_at) VALUES
    (3, 'completed', 'East', now() - interval '12 months'),
    (3, 'completed', 'East', now() - interval '6 months'),
    (3, 'completed', 'East', now() - interval '2 months');

INSERT INTO order_items (order_id, product_id, quantity, unit_price, unit_cost) VALUES
    (7, 8, 10, 199.99, 12.00), (7, 9, 10, 49.99, 5.00),
    (8, 8, 10, 199.99, 12.00), (8, 12, 2, 299.99, 80.00),
    (9, 8, 15, 199.99, 12.00), (9, 15, 5, 89.99, 8.00);

-- DeltaForce Trading — mixed, last order 100 days ago (churned)
INSERT INTO orders (customer_id, status, region, ordered_at) VALUES
    (4, 'completed', 'West', now() - interval '9 months'),
    (4, 'completed', 'West', now() - interval '100 days');

INSERT INTO order_items (order_id, product_id, quantity, unit_price, unit_cost) VALUES
    (10, 13, 3, 129.99, 55.00), (10, 4, 5, 49.99, 18.00),
    (11, 1, 8, 79.99, 32.00),   (11, 3, 8, 59.99, 22.00);

-- Echo Systems — Enterprise, recent orders
INSERT INTO orders (customer_id, status, region, ordered_at) VALUES
    (5, 'completed', 'North', now() - interval '11 months'),
    (5, 'completed', 'North', now() - interval '7 months'),
    (5, 'completed', 'North', now() - interval '3 months'),
    (5, 'completed', 'North', now() - interval '20 days');

INSERT INTO order_items (order_id, product_id, quantity, unit_price, unit_cost) VALUES
    (12, 2, 5, 449.99, 210.00), (12, 7, 5, 89.99, 38.00),
    (13, 8, 20, 199.99, 12.00), (13, 12, 3, 299.99, 80.00),
    (14, 2, 3, 449.99, 210.00), (14, 1, 10, 79.99, 32.00),
    (15, 8, 25, 199.99, 12.00), (15, 15, 10, 89.99, 8.00);

-- Foundry Works
INSERT INTO orders (customer_id, status, region, ordered_at) VALUES
    (6, 'completed', 'South', now() - interval '8 months'),
    (6, 'completed', 'South', now() - interval '45 days');

INSERT INTO order_items (order_id, product_id, quantity, unit_price, unit_cost) VALUES
    (16, 5, 1, 699.99, 380.00), (16, 10, 10, 19.99, 7.00),
    (17, 6, 1, 399.99, 175.00), (17, 11, 3, 39.99, 14.00);

-- GreenLeaf Organics — low-value, recent
INSERT INTO orders (customer_id, status, region, ordered_at) VALUES
    (7, 'completed', 'East', now() - interval '4 months'),
    (7, 'completed', 'East', now() - interval '15 days');

INSERT INTO order_items (order_id, product_id, quantity, unit_price, unit_cost) VALUES
    (18, 9, 3, 49.99, 5.00), (18, 10, 5, 19.99, 7.00),
    (19, 9, 3, 49.99, 5.00), (19, 11, 2, 39.99, 14.00);

-- Harbor Freight Tools
INSERT INTO orders (customer_id, status, region, ordered_at) VALUES
    (8, 'completed', 'West', now() - interval '6 months'),
    (8, 'completed', 'West', now() - interval '3 months'),
    (8, 'refunded',  'West', now() - interval '1 month');

INSERT INTO order_items (order_id, product_id, quantity, unit_price, unit_cost) VALUES
    (20, 1, 20, 79.99, 32.00), (20, 3, 20, 59.99, 22.00),
    (21, 4, 15, 49.99, 18.00), (21, 10, 30, 19.99, 7.00),
    (22, 2, 2, 449.99, 210.00);

-- Ironclad Consulting — Services buyer
INSERT INTO orders (customer_id, status, region, ordered_at) VALUES
    (9, 'completed', 'North', now() - interval '7 months'),
    (9, 'completed', 'North', now() - interval '2 months');

INSERT INTO order_items (order_id, product_id, quantity, unit_price, unit_cost) VALUES
    (23, 12, 5, 299.99, 80.00), (23, 8, 5, 199.99, 12.00),
    (24, 12, 8, 299.99, 80.00), (24, 15, 5, 89.99, 8.00);

-- JetSet Media
INSERT INTO orders (customer_id, status, region, ordered_at) VALUES
    (10, 'completed', 'South', now() - interval '5 months'),
    (10, 'completed', 'South', now() - interval '10 days');

INSERT INTO order_items (order_id, product_id, quantity, unit_price, unit_cost) VALUES
    (25, 7, 4, 89.99, 38.00), (25, 13, 4, 129.99, 55.00),
    (26, 7, 2, 89.99, 38.00), (26, 4, 3, 49.99, 18.00);

-- KineticEdge — last order 110 days ago (churned)
INSERT INTO orders (customer_id, status, region, ordered_at) VALUES
    (11, 'completed', 'East', now() - interval '5 months'),
    (11, 'completed', 'East', now() - interval '110 days');

INSERT INTO order_items (order_id, product_id, quantity, unit_price, unit_cost) VALUES
    (27, 8, 8, 199.99, 12.00), (27, 9, 8, 49.99, 5.00),
    (28, 8, 10, 199.99, 12.00), (28, 15, 3, 89.99, 8.00);

-- Luminary Labs — high-value Enterprise
INSERT INTO orders (customer_id, status, region, ordered_at) VALUES
    (12, 'completed', 'West', now() - interval '4 months'),
    (12, 'completed', 'West', now() - interval '1 month');

INSERT INTO order_items (order_id, product_id, quantity, unit_price, unit_cost) VALUES
    (29, 2, 10, 449.99, 210.00), (29, 1, 10, 79.99, 32.00), (29, 3, 10, 59.99, 22.00),
    (30, 8, 30, 199.99, 12.00),  (30, 12, 5, 299.99, 80.00);

-- MapleCrest Bakery — Consumer, low-value
INSERT INTO orders (customer_id, status, region, ordered_at) VALUES
    (13, 'completed', 'North', now() - interval '3 months'),
    (13, 'completed', 'North', now() - interval '5 days');

INSERT INTO order_items (order_id, product_id, quantity, unit_price, unit_cost) VALUES
    (31, 9, 1, 49.99, 5.00), (31, 10, 2, 19.99, 7.00),
    (32, 9, 2, 49.99, 5.00), (32, 11, 1, 39.99, 14.00);

-- NorthStar Logistics — recent customer
INSERT INTO orders (customer_id, status, region, ordered_at) VALUES
    (14, 'completed', 'South', now() - interval '2 months'),
    (14, 'completed', 'South', now() - interval '3 weeks');

INSERT INTO order_items (order_id, product_id, quantity, unit_price, unit_cost) VALUES
    (33, 5, 2, 699.99, 380.00), (33, 6, 2, 399.99, 175.00),
    (34, 12, 3, 299.99, 80.00), (34, 8, 5, 199.99, 12.00);

-- Orion Financial — newest customer, single order
INSERT INTO orders (customer_id, status, region, ordered_at) VALUES
    (15, 'completed', 'East', now() - interval '3 weeks');

INSERT INTO order_items (order_id, product_id, quantity, unit_price, unit_cost) VALUES
    (35, 8, 20, 199.99, 12.00), (35, 12, 4, 299.99, 80.00), (35, 15, 10, 89.99, 8.00);

-- ── Useful views for the AI to leverage ──────────────────────

CREATE OR REPLACE VIEW vw_order_revenue AS
SELECT
    o.id                                          AS order_id,
    o.customer_id,
    c.name                                        AS customer_name,
    c.region,
    c.segment,
    o.status,
    o.ordered_at,
    SUM(oi.quantity * oi.unit_price)              AS revenue,
    SUM(oi.quantity * oi.unit_cost)               AS cost,
    SUM(oi.quantity * (oi.unit_price - oi.unit_cost)) AS gross_profit
FROM orders o
JOIN customers c ON c.id = o.customer_id
JOIN order_items oi ON oi.order_id = o.id
GROUP BY o.id, o.customer_id, c.name, c.region, c.segment, o.status, o.ordered_at;

CREATE OR REPLACE VIEW vw_product_sales AS
SELECT
    p.id                                              AS product_id,
    p.name                                            AS product_name,
    p.sku,
    cat.name                                          AS category,
    SUM(oi.quantity)                                  AS units_sold,
    SUM(oi.quantity * oi.unit_price)                  AS revenue,
    SUM(oi.quantity * oi.unit_cost)                   AS cost,
    SUM(oi.quantity * (oi.unit_price - oi.unit_cost)) AS gross_profit,
    ROUND(
        100.0 * SUM(oi.quantity * (oi.unit_price - oi.unit_cost))
        / NULLIF(SUM(oi.quantity * oi.unit_price), 0), 2
    )                                                 AS margin_pct,
    MAX(o.ordered_at)                                 AS last_sold_at
FROM products p
JOIN categories cat ON cat.id = p.category_id
LEFT JOIN order_items oi ON oi.product_id = p.id
LEFT JOIN orders o ON o.id = oi.order_id AND o.status = 'completed'
GROUP BY p.id, p.name, p.sku, cat.name;

CREATE OR REPLACE VIEW vw_customer_last_order AS
SELECT
    c.id          AS customer_id,
    c.name        AS customer_name,
    c.email,
    c.region,
    c.segment,
    MAX(o.ordered_at)                          AS last_order_at,
    COUNT(o.id)                                AS total_orders,
    SUM(oi.quantity * oi.unit_price)           AS lifetime_revenue,
    NOW() - MAX(o.ordered_at)                  AS days_since_last_order
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id AND o.status = 'completed'
LEFT JOIN order_items oi ON oi.order_id = o.id
GROUP BY c.id, c.name, c.email, c.region, c.segment;
