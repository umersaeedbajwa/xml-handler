-- FreeSWITCH Database Setup Script for PostgreSQL
-- Run this script to create all necessary tables for the XML Handler

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS registrations CASCADE;
DROP TABLE IF EXISTS v_destinations CASCADE;
DROP TABLE IF EXISTS v_dialplans CASCADE;
DROP TABLE IF EXISTS v_default_settings CASCADE;
DROP TABLE IF EXISTS v_voicemails CASCADE;
DROP TABLE IF EXISTS v_extension_settings CASCADE;
DROP TABLE IF EXISTS v_extension_users CASCADE;
DROP TABLE IF EXISTS v_extensions CASCADE;
DROP TABLE IF EXISTS v_users CASCADE;
DROP TABLE IF EXISTS v_contacts CASCADE;
DROP TABLE IF EXISTS v_domains CASCADE;

-- Domains
CREATE TABLE v_domains (
  domain_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  domain_name TEXT NOT NULL UNIQUE,
  domain_enabled TEXT DEFAULT 'true',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Extensions
CREATE TABLE v_extensions (
  extension_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  domain_uuid UUID NOT NULL REFERENCES v_domains(domain_uuid) ON DELETE CASCADE,
  extension TEXT NOT NULL,
  number_alias TEXT,
  extension_type TEXT,
  enabled TEXT DEFAULT 'true',
  password TEXT,
  mwi_account TEXT,
  auth_acl TEXT,
  cidr TEXT,
  call_group TEXT,
  call_screen_enabled TEXT,
  user_record TEXT,
  hold_music TEXT,
  toll_allow TEXT,
  accountcode TEXT,
  user_context TEXT,
  effective_caller_id_name TEXT,
  effective_caller_id_number TEXT,
  outbound_caller_id_name TEXT,
  outbound_caller_id_number TEXT,
  emergency_caller_id_name TEXT,
  emergency_caller_id_number TEXT,
  missed_call_app TEXT,
  missed_call_data TEXT,
  directory_first_name TEXT,
  directory_last_name TEXT,
  directory_visible TEXT,
  directory_exten_visible TEXT,
  limit_max TEXT,
  call_timeout TEXT,
  max_registrations TEXT,
  limit_destination TEXT,
  sip_force_contact TEXT,
  sip_force_expires TEXT,
  nibble_account TEXT,
  sip_bypass_media TEXT,
  absolute_codec_string TEXT,
  force_ping TEXT,
  forward_all_enabled TEXT,
  forward_all_destination TEXT,
  forward_busy_enabled TEXT,
  forward_busy_destination TEXT,
  forward_no_answer_enabled TEXT,
  forward_no_answer_destination TEXT,
  forward_user_not_registered_enabled TEXT,
  forward_user_not_registered_destination TEXT,
  follow_me_uuid UUID,
  follow_me_enabled TEXT,
  dial_string TEXT,
  extension_language TEXT,
  extension_dialect TEXT,
  extension_voice TEXT,
  random TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX idx_v_extensions_domain_extension ON v_extensions(domain_uuid, extension);
CREATE INDEX idx_v_extensions_domain_number_alias ON v_extensions(domain_uuid, number_alias);

-- Extension ↔ User mapping
CREATE TABLE v_extension_users (
  extension_user_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  domain_uuid UUID NOT NULL REFERENCES v_domains(domain_uuid) ON DELETE CASCADE,
  extension_uuid UUID NOT NULL REFERENCES v_extensions(extension_uuid) ON DELETE CASCADE,
  user_uuid UUID NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX idx_ext_users_extension ON v_extension_users(extension_uuid);

-- Users
CREATE TABLE v_users (
  user_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  domain_uuid UUID NOT NULL REFERENCES v_domains(domain_uuid) ON DELETE CASCADE,
  contact_uuid UUID,
  username TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX idx_v_users_domain_user ON v_users(domain_uuid, user_uuid);

-- Contacts (basic)
CREATE TABLE v_contacts (
  contact_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  contact_name TEXT,
  contact_email TEXT,
  contact_description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Per-extension settings (params / variables)
CREATE TABLE v_extension_settings (
  extension_setting_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  extension_uuid UUID NOT NULL REFERENCES v_extensions(extension_uuid) ON DELETE CASCADE,
  extension_setting_type TEXT NOT NULL, -- 'param' | 'variable'
  extension_setting_name TEXT NOT NULL,
  extension_setting_value TEXT,
  extension_setting_enabled TEXT DEFAULT 'true',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX idx_ext_settings_extension ON v_extension_settings(extension_uuid);

-- Voicemails
CREATE TABLE v_voicemails (
  voicemail_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  domain_uuid UUID NOT NULL REFERENCES v_domains(domain_uuid) ON DELETE CASCADE,
  voicemail_id TEXT NOT NULL,
  voicemail_enabled TEXT DEFAULT 'true',
  voicemail_password TEXT,
  voicemail_attach_file TEXT,
  voicemail_local_after_email TEXT,
  voicemail_mail_to TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX idx_voicemails_domain_id ON v_voicemails(domain_uuid, voicemail_id);

-- Default settings (lazy_settings / v_default_settings)
CREATE TABLE v_default_settings (
  default_setting_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  default_setting_category TEXT NOT NULL,
  default_setting_subcategory TEXT NOT NULL,
  default_setting_name TEXT,
  default_setting_value TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX idx_default_settings_cat_sub ON v_default_settings(default_setting_category, default_setting_subcategory);

-- Dialplans (basic)
CREATE TABLE v_dialplans (
  dialplan_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  domain_uuid UUID REFERENCES v_domains(domain_uuid),
  dialplan_name TEXT,
  dialplan_context TEXT,
  dialplan_xml TEXT,
  dialplan_enabled TEXT DEFAULT 'true',
  dialplan_order INTEGER DEFAULT 100,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX idx_dialplans_domain_context ON v_dialplans(domain_uuid, dialplan_context);

-- Destinations (v_destinations)
CREATE TABLE v_destinations (
  destination_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  domain_uuid UUID REFERENCES v_domains(domain_uuid),
  destination_prefix TEXT,
  destination_area_code TEXT,
  destination_number TEXT,
  dialplan_uuid UUID REFERENCES v_dialplans(dialplan_uuid),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX idx_destinations_number ON v_destinations(domain_uuid, destination_number);

-- FreeSWITCH registrations (switch DB)
CREATE TABLE registrations (
  reg_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  reg_user TEXT NOT NULL,
  realm TEXT NOT NULL,
  hostname TEXT,
  expires INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX idx_reg_user_realm ON registrations(reg_user, realm);

-- Insert sample test data
BEGIN;

-- Sample domains
INSERT INTO v_domains(domain_uuid, domain_name, domain_enabled)
VALUES 
  ('11111111-1111-1111-1111-111111111111', 'example.com', 'true'),
  ('22222222-2222-2222-2222-222222222222', 'test.com', 'true');

-- Sample contacts
INSERT INTO v_contacts(contact_uuid, contact_name, contact_email)
VALUES 
  ('33333333-3333-3333-3333-333333333333', 'John Doe', 'john@example.com'),
  ('44444444-4444-4444-4444-444444444444', 'Jane Smith', 'jane@example.com');

-- Sample users
INSERT INTO v_users(user_uuid, domain_uuid, contact_uuid, username)
VALUES 
  ('55555555-5555-5555-5555-555555555555', '11111111-1111-1111-1111-111111111111', '33333333-3333-3333-3333-333333333333', 'john'),
  ('66666666-6666-6666-6666-666666666666', '11111111-1111-1111-1111-111111111111', '44444444-4444-4444-4444-444444444444', 'jane');

-- Sample extensions
INSERT INTO v_extensions(
  extension_uuid, domain_uuid, extension, number_alias, enabled, password,
  directory_first_name, directory_last_name, extension_type
)
VALUES 
  ('77777777-7777-7777-7777-777777777777', '11111111-1111-1111-1111-111111111111', '1001', '1001', 'true', 'secret123', 'John', 'Doe', 'fixed'),
  ('88888888-8888-8888-8888-888888888888', '11111111-1111-1111-1111-111111111111', '1002', '1002', 'true', 'secret456', 'Jane', 'Smith', 'fixed');

-- Sample extension-user mappings
INSERT INTO v_extension_users(extension_user_uuid, domain_uuid, extension_uuid, user_uuid)
VALUES 
  ('99999999-9999-9999-9999-999999999999', '11111111-1111-1111-1111-111111111111', '77777777-7777-7777-7777-777777777777', '55555555-5555-5555-5555-555555555555'),
  ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '11111111-1111-1111-1111-111111111111', '88888888-8888-8888-8888-888888888888', '66666666-6666-6666-6666-666666666666');

-- Sample voicemails
INSERT INTO v_voicemails(voicemail_uuid, domain_uuid, voicemail_id, voicemail_enabled, voicemail_password, voicemail_mail_to)
VALUES 
  ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '11111111-1111-1111-1111-111111111111', '1001', 'true', '1234', 'john@example.com'),
  ('cccccccc-cccc-cccc-cccc-cccccccccccc', '11111111-1111-1111-1111-111111111111', '1002', 'true', '5678', 'jane@example.com');

COMMIT;

-- Display table counts
SELECT 'v_domains' as table_name, COUNT(*) as record_count FROM v_domains
UNION ALL
SELECT 'v_extensions' as table_name, COUNT(*) as record_count FROM v_extensions
UNION ALL
SELECT 'v_users' as table_name, COUNT(*) as record_count FROM v_users
UNION ALL
SELECT 'v_contacts' as table_name, COUNT(*) as record_count FROM v_contacts
UNION ALL
SELECT 'v_voicemails' as table_name, COUNT(*) as record_count FROM v_voicemails;

-- Show sample data
SELECT 'Sample Domains:' as info;
SELECT domain_name, domain_enabled FROM v_domains;

SELECT 'Sample Extensions:' as info;
SELECT e.extension, e.directory_first_name, e.directory_last_name, d.domain_name 
FROM v_extensions e 
JOIN v_domains d ON e.domain_uuid = d.domain_uuid;