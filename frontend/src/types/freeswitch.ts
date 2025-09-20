// FreeSWITCH Data Types
export interface Domain {
  domain_uuid: string;
  domain_name: string;
  domain_enabled: string;
  created_at?: string;
}

export interface DomainCreate {
  domain_name: string;
  domain_enabled?: string;
}

export interface DomainUpdate {
  domain_name?: string;
  domain_enabled?: string;
}

export interface Contact {
  contact_uuid: string;
  contact_name?: string;
  contact_email?: string;
  contact_description?: string;
  created_at?: string;
}

export interface ContactCreate {
  contact_name?: string;
  contact_email?: string;
  contact_description?: string;
}

export interface ContactUpdate {
  contact_name?: string;
  contact_email?: string;
  contact_description?: string;
}

export interface User {
  user_uuid: string;
  domain_uuid: string;
  contact_uuid?: string;
  username?: string;
  created_at?: string;
}

export interface UserCreate {
  domain_uuid: string;
  contact_uuid?: string;
  username?: string;
}

export interface UserUpdate {
  username?: string;
  contact_uuid?: string;
}

export interface Extension {
  extension_uuid: string;
  domain_uuid: string;
  extension: string;
  number_alias?: string;
  extension_type?: string;
  enabled: string;
  password?: string;
  mwi_account?: string;
  auth_acl?: string;
  cidr?: string;
  call_group?: string;
  call_screen_enabled?: string;
  user_record?: string;
  hold_music?: string;
  toll_allow?: string;
  accountcode?: string;
  user_context?: string;
  effective_caller_id_name?: string;
  effective_caller_id_number?: string;
  outbound_caller_id_name?: string;
  outbound_caller_id_number?: string;
  emergency_caller_id_name?: string;
  emergency_caller_id_number?: string;
  missed_call_app?: string;
  missed_call_data?: string;
  directory_first_name?: string;
  directory_last_name?: string;
  directory_visible?: string;
  directory_exten_visible?: string;
  limit_max?: string;
  call_timeout?: string;
  max_registrations?: string;
  limit_destination?: string;
  sip_force_contact?: string;
  sip_force_expires?: string;
  nibble_account?: string;
  sip_bypass_media?: string;
  absolute_codec_string?: string;
  force_ping?: string;
  forward_all_enabled?: string;
  forward_all_destination?: string;
  forward_busy_enabled?: string;
  forward_busy_destination?: string;
  forward_no_answer_enabled?: string;
  forward_no_answer_destination?: string;
  forward_user_not_registered_enabled?: string;
  forward_user_not_registered_destination?: string;
  follow_me_uuid?: string;
  follow_me_enabled?: string;
  dial_string?: string;
  extension_language?: string;
  extension_dialect?: string;
  extension_voice?: string;
  random?: string;
  created_at?: string;
}

export interface ExtensionCreate {
  domain_uuid: string;
  extension: string;
  number_alias?: string;
  extension_type?: string;
  enabled?: string;
  password?: string;
  mwi_account?: string;
  auth_acl?: string;
  cidr?: string;
  call_group?: string;
  call_screen_enabled?: string;
  user_record?: string;
  hold_music?: string;
  toll_allow?: string;
  accountcode?: string;
  user_context?: string;
  effective_caller_id_name?: string;
  effective_caller_id_number?: string;
  outbound_caller_id_name?: string;
  outbound_caller_id_number?: string;
  emergency_caller_id_name?: string;
  emergency_caller_id_number?: string;
  missed_call_app?: string;
  missed_call_data?: string;
  directory_first_name?: string;
  directory_last_name?: string;
  directory_visible?: string;
  directory_exten_visible?: string;
  limit_max?: string;
  call_timeout?: string;
  max_registrations?: string;
  limit_destination?: string;
  sip_force_contact?: string;
  sip_force_expires?: string;
  nibble_account?: string;
  sip_bypass_media?: string;
  absolute_codec_string?: string;
  force_ping?: string;
  forward_all_enabled?: string;
  forward_all_destination?: string;
  forward_busy_enabled?: string;
  forward_busy_destination?: string;
  forward_no_answer_enabled?: string;
  forward_no_answer_destination?: string;
  forward_user_not_registered_enabled?: string;
  forward_user_not_registered_destination?: string;
  follow_me_uuid?: string;
  follow_me_enabled?: string;
  dial_string?: string;
  extension_language?: string;
  extension_dialect?: string;
  extension_voice?: string;
  random?: string;
}

export interface ExtensionSetting {
  extension_setting_uuid: string;
  extension_uuid: string;
  extension_setting_type: string; // 'param' | 'variable'
  extension_setting_name: string;
  extension_setting_value?: string;
  extension_setting_enabled: string;
  created_at?: string;
}

export interface ExtensionSettingCreate {
  extension_uuid: string;
  extension_setting_type: string;
  extension_setting_name: string;
  extension_setting_value?: string;
  extension_setting_enabled?: string;
}

export interface ExtensionSettingUpdate {
  extension_setting_type?: string;
  extension_setting_name?: string;
  extension_setting_value?: string;
  extension_setting_enabled?: string;
}

export interface Voicemail {
  voicemail_uuid: string;
  domain_uuid: string;
  voicemail_id: string;
  voicemail_enabled: string;
  voicemail_password?: string;
  voicemail_attach_file?: string;
  voicemail_local_after_email?: string;
  voicemail_mail_to?: string;
  created_at?: string;
}

export interface VoicemailCreate {
  domain_uuid: string;
  voicemail_id: string;
  voicemail_enabled?: string;
  voicemail_password?: string;
  voicemail_attach_file?: string;
  voicemail_local_after_email?: string;
  voicemail_mail_to?: string;
}

export interface VoicemailUpdate {
  voicemail_id?: string;
  voicemail_enabled?: string;
  voicemail_password?: string;
  voicemail_attach_file?: string;
  voicemail_local_after_email?: string;
  voicemail_mail_to?: string;
}

export interface Dialplan {
  dialplan_uuid: string;
  domain_uuid?: string;
  dialplan_name?: string;
  dialplan_context?: string;
  dialplan_xml?: string;
  dialplan_enabled: string;
  dialplan_order: number;
  created_at?: string;
}

export interface DialplanCreate {
  domain_uuid?: string;
  dialplan_name?: string;
  dialplan_context?: string;
  dialplan_xml?: string;
  dialplan_enabled?: string;
  dialplan_order?: number;
}

export interface DialplanUpdate {
  dialplan_name?: string;
  dialplan_context?: string;
  dialplan_xml?: string;
  dialplan_enabled?: string;
  dialplan_order?: number;
}

export interface Registration {
  reg_uuid: string;
  reg_user: string;
  realm: string;
  hostname?: string;
  expires?: number;
  created_at?: string;
}