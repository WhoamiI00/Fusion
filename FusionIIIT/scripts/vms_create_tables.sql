-- ============================================================
-- VMS module tables for an existing FusionIIIT (fusionlab) database
-- that already has all other modules (globals_extrainfo, etc.)
--
-- Run with:  psql -U fusion_admin -d fusionlab -f vms_create_tables.sql
-- ============================================================

BEGIN;

-- 1. vms_visitor
CREATE TABLE IF NOT EXISTS vms_visitor (
    id              SERIAL PRIMARY KEY,
    full_name       VARCHAR(120)  NOT NULL,
    id_number       VARCHAR(64)   NOT NULL UNIQUE,
    id_type         VARCHAR(20)   NOT NULL,
    contact_phone   VARCHAR(20)   NOT NULL,
    contact_email   VARCHAR(254)  NOT NULL DEFAULT '',
    photo_reference VARCHAR(256)  NOT NULL DEFAULT ''
);


-- 2. vms_blacklistentry
CREATE TABLE IF NOT EXISTS vms_blacklistentry (
    id          SERIAL PRIMARY KEY,
    id_number   VARCHAR(64)   NOT NULL,
    reason      VARCHAR(200)  NOT NULL,
    active      BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS vms_blacklistentry_id_number_idx
    ON vms_blacklistentry (id_number);


-- 3. vms_visit
CREATE TABLE IF NOT EXISTS vms_visit (
    id                        SERIAL PRIMARY KEY,
    purpose                   VARCHAR(200)  NOT NULL,
    host_name                 VARCHAR(120)  NOT NULL,
    host_department           VARCHAR(120)  NOT NULL,
    host_contact              VARCHAR(50)   NOT NULL DEFAULT '',
    expected_duration_minutes INTEGER       NOT NULL DEFAULT 60 CHECK (expected_duration_minutes >= 0),
    status                    VARCHAR(20)   NOT NULL DEFAULT 'registered',
    registered_at             TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    verified_at               TIMESTAMPTZ,
    pass_issued_at            TIMESTAMPTZ,
    entry_at                  TIMESTAMPTZ,
    exit_at                   TIMESTAMPTZ,
    denial_reason             VARCHAR(200)  NOT NULL DEFAULT '',
    denial_remarks            TEXT          NOT NULL DEFAULT '',
    is_vip                    BOOLEAN       NOT NULL DEFAULT FALSE,
    visitor_id                INTEGER       NOT NULL
                              REFERENCES vms_visitor(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS vms_visit_visitor_id_idx ON vms_visit (visitor_id);


-- 4. vms_visitorpass  (OneToOne with vms_visit)
CREATE TABLE IF NOT EXISTS vms_visitorpass (
    id               SERIAL PRIMARY KEY,
    pass_number      VARCHAR(32)   NOT NULL UNIQUE
                     DEFAULT ('VMS-' || UPPER(SUBSTR(MD5(RANDOM()::TEXT), 1, 10))),
    valid_from       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    valid_until      TIMESTAMPTZ   NOT NULL,
    authorized_zones VARCHAR(200)  NOT NULL DEFAULT 'public',
    status           VARCHAR(20)   NOT NULL DEFAULT 'pending',
    barcode_data     TEXT          NOT NULL DEFAULT '',
    is_vip_pass      BOOLEAN       NOT NULL DEFAULT FALSE,
    visit_id         INTEGER       NOT NULL UNIQUE
                     REFERENCES vms_visit(id) ON DELETE CASCADE
);


-- 5. vms_verificationlog
CREATE TABLE IF NOT EXISTS vms_verificationlog (
    id          SERIAL PRIMARY KEY,
    method      VARCHAR(20)   NOT NULL DEFAULT 'manual',
    result      BOOLEAN       NOT NULL DEFAULT FALSE,
    notes       TEXT          NOT NULL DEFAULT '',
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    verifier_id VARCHAR(20)
                REFERENCES globals_extrainfo(id) ON DELETE SET NULL,
    visit_id    INTEGER       NOT NULL
                REFERENCES vms_visit(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS vms_verificationlog_visit_id_idx    ON vms_verificationlog (visit_id);
CREATE INDEX IF NOT EXISTS vms_verificationlog_verifier_id_idx ON vms_verificationlog (verifier_id);


-- 6. vms_deniallog
CREATE TABLE IF NOT EXISTS vms_deniallog (
    id          SERIAL PRIMARY KEY,
    reason      VARCHAR(120)  NOT NULL,
    remarks     TEXT          NOT NULL DEFAULT '',
    escalated   BOOLEAN       NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    visit_id    INTEGER       NOT NULL
                REFERENCES vms_visit(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS vms_deniallog_visit_id_idx ON vms_deniallog (visit_id);


-- 7. vms_entryexitlog
CREATE TABLE IF NOT EXISTS vms_entryexitlog (
    id              SERIAL PRIMARY KEY,
    action          VARCHAR(10)   NOT NULL,
    gate_name       VARCHAR(120)  NOT NULL,
    items_declared  TEXT          NOT NULL DEFAULT '',
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    recorded_by_id  VARCHAR(20)
                    REFERENCES globals_extrainfo(id) ON DELETE SET NULL,
    visit_id        INTEGER       NOT NULL
                    REFERENCES vms_visit(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS vms_entryexitlog_visit_id_idx       ON vms_entryexitlog (visit_id);
CREATE INDEX IF NOT EXISTS vms_entryexitlog_recorded_by_id_idx ON vms_entryexitlog (recorded_by_id);


-- 8. vms_securityincident
CREATE TABLE IF NOT EXISTS vms_securityincident (
    id              SERIAL PRIMARY KEY,
    severity        VARCHAR(10)   NOT NULL,
    issue_type      VARCHAR(40)   NOT NULL DEFAULT 'other',
    description     TEXT          NOT NULL,
    status          VARCHAR(20)   NOT NULL DEFAULT 'open',
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    recorded_by_id  VARCHAR(20)
                    REFERENCES globals_extrainfo(id) ON DELETE SET NULL,
    visit_id        INTEGER
                    REFERENCES vms_visit(id) ON DELETE SET NULL,
    visitor_id      INTEGER
                    REFERENCES vms_visitor(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS vms_securityincident_recorded_by_id_idx ON vms_securityincident (recorded_by_id);
CREATE INDEX IF NOT EXISTS vms_securityincident_visit_id_idx       ON vms_securityincident (visit_id);
CREATE INDEX IF NOT EXISTS vms_securityincident_visitor_id_idx     ON vms_securityincident (visitor_id);


-- 9. Register migration so Django knows 0001_initial already ran
INSERT INTO django_migrations (app, name, applied)
VALUES ('vms', '0001_initial', NOW())
ON CONFLICT DO NOTHING;

INSERT INTO django_migrations (app, name, applied)
VALUES ('vms', '0002_visitorpass_barcode_data_to_text', NOW())
ON CONFLICT DO NOTHING;


COMMIT;
