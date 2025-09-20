from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

# Domain Models
class DomainBase(BaseModel):
    domain_name: str
    domain_enabled: str = "true"

class DomainCreate(DomainBase):
    pass

class DomainUpdate(BaseModel):
    domain_name: Optional[str] = None
    domain_enabled: Optional[str] = None

class Domain(DomainBase):
    domain_uuid: UUID
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Contact Models
class ContactBase(BaseModel):
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_description: Optional[str] = None

class ContactCreate(ContactBase):
    pass

class ContactUpdate(ContactBase):
    pass

class Contact(ContactBase):
    contact_uuid: UUID
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# User Models
class UserBase(BaseModel):
    username: Optional[str] = None

class UserCreate(UserBase):
    domain_uuid: UUID
    contact_uuid: Optional[UUID] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    contact_uuid: Optional[UUID] = None

class User(UserBase):
    user_uuid: UUID
    domain_uuid: UUID
    contact_uuid: Optional[UUID] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Extension Models
class ExtensionBase(BaseModel):
    extension: str
    number_alias: Optional[str] = None
    extension_type: Optional[str] = None
    enabled: str = "true"
    password: Optional[str] = None
    mwi_account: Optional[str] = None
    auth_acl: Optional[str] = None
    cidr: Optional[str] = None
    call_group: Optional[str] = None
    call_screen_enabled: Optional[str] = None
    user_record: Optional[str] = None
    hold_music: Optional[str] = None
    toll_allow: Optional[str] = None
    accountcode: Optional[str] = None
    user_context: Optional[str] = None
    effective_caller_id_name: Optional[str] = None
    effective_caller_id_number: Optional[str] = None
    outbound_caller_id_name: Optional[str] = None
    outbound_caller_id_number: Optional[str] = None
    emergency_caller_id_name: Optional[str] = None
    emergency_caller_id_number: Optional[str] = None
    missed_call_app: Optional[str] = None
    missed_call_data: Optional[str] = None
    directory_first_name: Optional[str] = None
    directory_last_name: Optional[str] = None
    directory_visible: Optional[str] = None
    directory_exten_visible: Optional[str] = None
    limit_max: Optional[str] = None
    call_timeout: Optional[str] = None
    max_registrations: Optional[str] = None
    limit_destination: Optional[str] = None
    sip_force_contact: Optional[str] = None
    sip_force_expires: Optional[str] = None
    nibble_account: Optional[str] = None
    sip_bypass_media: Optional[str] = None
    absolute_codec_string: Optional[str] = None
    force_ping: Optional[str] = None
    forward_all_enabled: Optional[str] = None
    forward_all_destination: Optional[str] = None
    forward_busy_enabled: Optional[str] = None
    forward_busy_destination: Optional[str] = None
    forward_no_answer_enabled: Optional[str] = None
    forward_no_answer_destination: Optional[str] = None
    forward_user_not_registered_enabled: Optional[str] = None
    forward_user_not_registered_destination: Optional[str] = None
    follow_me_uuid: Optional[UUID] = None
    follow_me_enabled: Optional[str] = None
    dial_string: Optional[str] = None
    extension_language: Optional[str] = None
    extension_dialect: Optional[str] = None
    extension_voice: Optional[str] = None
    random: Optional[str] = None

class ExtensionCreate(ExtensionBase):
    domain_uuid: UUID

class ExtensionUpdate(BaseModel):
    extension: Optional[str] = None
    number_alias: Optional[str] = None
    extension_type: Optional[str] = None
    enabled: Optional[str] = None
    password: Optional[str] = None
    mwi_account: Optional[str] = None
    auth_acl: Optional[str] = None
    cidr: Optional[str] = None
    call_group: Optional[str] = None
    call_screen_enabled: Optional[str] = None
    user_record: Optional[str] = None
    hold_music: Optional[str] = None
    toll_allow: Optional[str] = None
    accountcode: Optional[str] = None
    user_context: Optional[str] = None
    effective_caller_id_name: Optional[str] = None
    effective_caller_id_number: Optional[str] = None
    outbound_caller_id_name: Optional[str] = None
    outbound_caller_id_number: Optional[str] = None
    emergency_caller_id_name: Optional[str] = None
    emergency_caller_id_number: Optional[str] = None
    missed_call_app: Optional[str] = None
    missed_call_data: Optional[str] = None
    directory_first_name: Optional[str] = None
    directory_last_name: Optional[str] = None
    directory_visible: Optional[str] = None
    directory_exten_visible: Optional[str] = None
    limit_max: Optional[str] = None
    call_timeout: Optional[str] = None
    max_registrations: Optional[str] = None
    limit_destination: Optional[str] = None
    sip_force_contact: Optional[str] = None
    sip_force_expires: Optional[str] = None
    nibble_account: Optional[str] = None
    sip_bypass_media: Optional[str] = None
    absolute_codec_string: Optional[str] = None
    force_ping: Optional[str] = None
    forward_all_enabled: Optional[str] = None
    forward_all_destination: Optional[str] = None
    forward_busy_enabled: Optional[str] = None
    forward_busy_destination: Optional[str] = None
    forward_no_answer_enabled: Optional[str] = None
    forward_no_answer_destination: Optional[str] = None
    forward_user_not_registered_enabled: Optional[str] = None
    forward_user_not_registered_destination: Optional[str] = None
    follow_me_uuid: Optional[UUID] = None
    follow_me_enabled: Optional[str] = None
    dial_string: Optional[str] = None
    extension_language: Optional[str] = None
    extension_dialect: Optional[str] = None
    extension_voice: Optional[str] = None
    random: Optional[str] = None

class Extension(ExtensionBase):
    extension_uuid: UUID
    domain_uuid: UUID
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Extension User Models
class ExtensionUserBase(BaseModel):
    pass

class ExtensionUserCreate(BaseModel):
    domain_uuid: UUID
    extension_uuid: UUID
    user_uuid: UUID

class ExtensionUser(ExtensionUserBase):
    extension_user_uuid: UUID
    domain_uuid: UUID
    extension_uuid: UUID
    user_uuid: UUID
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Extension Settings Models
class ExtensionSettingBase(BaseModel):
    extension_setting_type: str  # 'param' | 'variable'
    extension_setting_name: str
    extension_setting_value: Optional[str] = None
    extension_setting_enabled: str = "true"

class ExtensionSettingCreate(ExtensionSettingBase):
    extension_uuid: UUID

class ExtensionSettingUpdate(BaseModel):
    extension_setting_type: Optional[str] = None
    extension_setting_name: Optional[str] = None
    extension_setting_value: Optional[str] = None
    extension_setting_enabled: Optional[str] = None

class ExtensionSetting(ExtensionSettingBase):
    extension_setting_uuid: UUID
    extension_uuid: UUID
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Voicemail Models
class VoicemailBase(BaseModel):
    voicemail_id: str
    voicemail_enabled: str = "true"
    voicemail_password: Optional[str] = None
    voicemail_attach_file: Optional[str] = None
    voicemail_local_after_email: Optional[str] = None
    voicemail_mail_to: Optional[str] = None

class VoicemailCreate(VoicemailBase):
    domain_uuid: UUID

class VoicemailUpdate(BaseModel):
    voicemail_id: Optional[str] = None
    voicemail_enabled: Optional[str] = None
    voicemail_password: Optional[str] = None
    voicemail_attach_file: Optional[str] = None
    voicemail_local_after_email: Optional[str] = None
    voicemail_mail_to: Optional[str] = None

class Voicemail(VoicemailBase):
    voicemail_uuid: UUID
    domain_uuid: UUID
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Default Settings Models
class DefaultSettingBase(BaseModel):
    default_setting_category: str
    default_setting_subcategory: str
    default_setting_name: Optional[str] = None
    default_setting_value: Optional[str] = None

class DefaultSettingCreate(DefaultSettingBase):
    pass

class DefaultSettingUpdate(BaseModel):
    default_setting_category: Optional[str] = None
    default_setting_subcategory: Optional[str] = None
    default_setting_name: Optional[str] = None
    default_setting_value: Optional[str] = None

class DefaultSetting(DefaultSettingBase):
    default_setting_uuid: UUID
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Dialplan Models
class DialplanBase(BaseModel):
    dialplan_name: Optional[str] = None
    dialplan_context: Optional[str] = None
    dialplan_xml: Optional[str] = None
    dialplan_enabled: str = "true"
    dialplan_order: int = 100

class DialplanCreate(DialplanBase):
    domain_uuid: Optional[UUID] = None

class DialplanUpdate(BaseModel):
    dialplan_name: Optional[str] = None
    dialplan_context: Optional[str] = None
    dialplan_xml: Optional[str] = None
    dialplan_enabled: Optional[str] = None
    dialplan_order: Optional[int] = None

class Dialplan(DialplanBase):
    dialplan_uuid: UUID
    domain_uuid: Optional[UUID] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Registration Models (read-only, managed by FreeSWITCH)
class Registration(BaseModel):
    reg_uuid: UUID
    reg_user: str
    realm: str
    hostname: Optional[str] = None
    expires: Optional[int] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True