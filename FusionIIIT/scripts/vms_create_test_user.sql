-- ============================================================
-- Create a security test user for VMS API authentication
--
-- Username: securitytest
-- Password: pass1234
-- Role:     is_staff = true
--
-- Run with:  psql -U fusion_admin -d fusionlab -f vms_create_test_user.sql
-- ============================================================

BEGIN;

-- 1. Insert into auth_user
INSERT INTO auth_user (
    password,
    last_login,
    is_superuser,
    username,
    first_name,
    last_name,
    email,
    is_staff,
    is_active,
    date_joined
)
VALUES (
    'pbkdf2_sha256$720000$c3c22d2521c0$oytHa4qUsmnfWvLnqMwNrSphez4GSLXDS58TuOuW6jc=',
    NULL,
    FALSE,
    'securitytest',
    'Security',
    'Test',
    'securitytest@fusion.local',
    TRUE,
    TRUE,
    NOW()
)
ON CONFLICT (username) DO NOTHING;

-- 2. Insert into globals_extrainfo so VMS views can resolve _current_staff(request)
--    PK (id) is a CharField(20), user_type must be 'staff'
INSERT INTO globals_extrainfo (
    id,
    user_id,
    title,
    sex,
    date_of_birth,
    user_status,
    address,
    phone_no,
    user_type,
    department_id,
    about_me,
    date_modified,
    last_selected_role
)
SELECT
    'securitytest',                                     -- id  (CharField PK)
    u.id,                                               -- user_id (FK → auth_user.id)
    'Mr.',                                              -- title
    'M',                                                -- sex
    '1990-01-01',                                       -- date_of_birth
    'PRESENT',                                          -- user_status
    '',                                                 -- address
    9999999999,                                         -- phone_no
    'staff',                                            -- user_type
    NULL,                                               -- department_id
    'VMS Security Test Account',                        -- about_me
    NULL,                                               -- date_modified
    NULL                                                -- last_selected_role
FROM auth_user u
WHERE u.username = 'securitytest'
ON CONFLICT (id) DO NOTHING;

COMMIT;
