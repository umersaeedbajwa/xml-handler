from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import UUID
import uuid
from app.database import baseDB
from app.utils.cache import invalidate_extension_cache, invalidate_domain_cache, invalidate_user_cache
from app.models.freeswitch_models import (
    Domain, DomainCreate, DomainUpdate,
    Contact, ContactCreate, ContactUpdate,
    User, UserCreate, UserUpdate,
    Extension, ExtensionCreate, ExtensionUpdate,
    ExtensionUser, ExtensionUserCreate,
    ExtensionSetting, ExtensionSettingCreate, ExtensionSettingUpdate,
    Voicemail, VoicemailCreate, VoicemailUpdate,
    DefaultSetting, DefaultSettingCreate, DefaultSettingUpdate,
    Dialplan, DialplanCreate, DialplanUpdate,
    Registration
)

router = APIRouter(prefix="/api/freeswitch", tags=["FreeSWITCH Management"])

# Domain endpoints
@router.get("/domains", response_model=List[Domain])
async def get_domains():
    query = "SELECT * FROM v_domains ORDER BY domain_name"
    return await baseDB.fetch_all(query)

@router.get("/domains/{domain_uuid}", response_model=Domain)
async def get_domain(domain_uuid: UUID):
    query = "SELECT * FROM v_domains WHERE domain_uuid = $1"
    domain = await baseDB.fetch_one(query, str(domain_uuid))
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    return domain

@router.post("/domains", response_model=Domain)
async def create_domain(domain: DomainCreate):
    domain_uuid = str(uuid.uuid4())
    query = """
        INSERT INTO v_domains (domain_uuid, domain_name, domain_enabled)
        VALUES ($1, $2, $3)
        RETURNING *
    """
    result = await baseDB.fetch_one(query, domain_uuid, domain.domain_name, domain.domain_enabled)
    return result

@router.put("/domains/{domain_uuid}", response_model=Domain)
async def update_domain(domain_uuid: UUID, domain: DomainUpdate):
    # Check if domain exists
    existing = await baseDB.fetch_one("SELECT * FROM v_domains WHERE domain_uuid = $1", str(domain_uuid))
    if not existing:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    update_data = domain.dict(exclude_unset=True)
    if not update_data:
        return existing
    
    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"UPDATE v_domains SET {set_clause} WHERE domain_uuid = $1 RETURNING *"
    values = [str(domain_uuid)] + list(update_data.values())
    
    result = await baseDB.fetch_one(query, *values)
    
    # Invalidate domain cache after update
    await invalidate_domain_cache(existing['domain_name'])
    if 'domain_name' in update_data and update_data['domain_name'] != existing['domain_name']:
        await invalidate_domain_cache(update_data['domain_name'])
    
    return result

@router.delete("/domains/{domain_uuid}")
async def delete_domain(domain_uuid: UUID):
    # Get domain info before deletion for cache invalidation
    existing = await baseDB.fetch_one("SELECT * FROM v_domains WHERE domain_uuid = $1", str(domain_uuid))
    if not existing:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    query = "DELETE FROM v_domains WHERE domain_uuid = $1"
    result = await baseDB.execute(query, str(domain_uuid))
    
    # Invalidate domain cache after deletion
    await invalidate_domain_cache(existing['domain_name'])
    
    return {"message": "Domain deleted successfully"}

# Contact endpoints
@router.get("/contacts", response_model=List[Contact])
async def get_contacts():
    query = "SELECT * FROM v_contacts ORDER BY contact_name"
    return await baseDB.fetch_all(query)

@router.get("/contacts/{contact_uuid}", response_model=Contact)
async def get_contact(contact_uuid: UUID):
    query = "SELECT * FROM v_contacts WHERE contact_uuid = $1"
    contact = await baseDB.fetch_one(query, str(contact_uuid))
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.post("/contacts", response_model=Contact)
async def create_contact(contact: ContactCreate):
    contact_uuid = str(uuid.uuid4())
    query = """
        INSERT INTO v_contacts (contact_uuid, contact_name, contact_email, contact_description)
        VALUES ($1, $2, $3, $4)
        RETURNING *
    """
    result = await baseDB.fetch_one(
        query, contact_uuid, contact.contact_name, 
        contact.contact_email, contact.contact_description
    )
    return result

@router.put("/contacts/{contact_uuid}", response_model=Contact)
async def update_contact(contact_uuid: UUID, contact: ContactUpdate):
    existing = await baseDB.fetch_one("SELECT * FROM v_contacts WHERE contact_uuid = $1", str(contact_uuid))
    if not existing:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    update_data = contact.dict(exclude_unset=True)
    if not update_data:
        return existing
    
    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"UPDATE v_contacts SET {set_clause} WHERE contact_uuid = $1 RETURNING *"
    values = [str(contact_uuid)] + list(update_data.values())
    
    result = await baseDB.fetch_one(query, *values)
    return result

@router.delete("/contacts/{contact_uuid}")
async def delete_contact(contact_uuid: UUID):
    query = "DELETE FROM v_contacts WHERE contact_uuid = $1"
    result = await baseDB.execute(query, str(contact_uuid))
    if result == 0:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"message": "Contact deleted successfully"}

# User endpoints
@router.get("/users", response_model=List[User])
async def get_users():
    query = "SELECT * FROM v_users ORDER BY username"
    return await baseDB.fetch_all(query)

@router.get("/users/{user_uuid}", response_model=User)
async def get_user(user_uuid: UUID):
    query = "SELECT * FROM v_users WHERE user_uuid = $1"
    user = await baseDB.fetch_one(query, str(user_uuid))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users", response_model=User)
async def create_user(user: UserCreate):
    user_uuid = str(uuid.uuid4())
    query = """
        INSERT INTO v_users (user_uuid, domain_uuid, contact_uuid, username)
        VALUES ($1, $2, $3, $4)
        RETURNING *
    """
    result = await baseDB.fetch_one(
        query, user_uuid, str(user.domain_uuid), 
        str(user.contact_uuid) if user.contact_uuid else None, user.username
    )
    return result

@router.put("/users/{user_uuid}", response_model=User)
async def update_user(user_uuid: UUID, user: UserUpdate):
    existing = await baseDB.fetch_one("SELECT * FROM v_users WHERE user_uuid = $1", str(user_uuid))
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user.dict(exclude_unset=True)
    if not update_data:
        return existing
    
    # Handle UUID fields
    if 'contact_uuid' in update_data and update_data['contact_uuid']:
        update_data['contact_uuid'] = str(update_data['contact_uuid'])
    
    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"UPDATE v_users SET {set_clause} WHERE user_uuid = $1 RETURNING *"
    values = [str(user_uuid)] + list(update_data.values())
    
    result = await baseDB.fetch_one(query, *values)
    
    # Invalidate user cache after update
    if result:
        domain_query = "SELECT domain_name FROM v_domains WHERE domain_uuid = $1"
        domain_info = await baseDB.fetch_one(domain_query, result['domain_uuid'])
        
        if domain_info:
            # Clear cache for both old and new username if changed
            await invalidate_user_cache(existing['username'], domain_info['domain_name'])
            if update_data.get('username') and update_data['username'] != existing['username']:
                await invalidate_user_cache(result['username'], domain_info['domain_name'])
    
    return result

@router.delete("/users/{user_uuid}")
async def delete_user(user_uuid: UUID):
    # Get user info before deletion for cache invalidation
    existing = await baseDB.fetch_one("SELECT * FROM v_users WHERE user_uuid = $1", str(user_uuid))
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    
    query = "DELETE FROM v_users WHERE user_uuid = $1"
    result = await baseDB.execute(query, str(user_uuid))
    
    # Invalidate user cache after deletion
    domain_query = "SELECT domain_name FROM v_domains WHERE domain_uuid = $1"
    domain_info = await baseDB.fetch_one(domain_query, existing['domain_uuid'])
    
    if domain_info:
        await invalidate_user_cache(existing['username'], domain_info['domain_name'])
    
    return {"message": "User deleted successfully"}

# Extension endpoints
@router.get("/extensions", response_model=List[Extension])
async def get_extensions():
    query = "SELECT * FROM v_extensions ORDER BY extension"
    return await baseDB.fetch_all(query)

@router.get("/extensions/{extension_uuid}", response_model=Extension)
async def get_extension(extension_uuid: UUID):
    query = "SELECT * FROM v_extensions WHERE extension_uuid = $1"
    extension = await baseDB.fetch_one(query, str(extension_uuid))
    if not extension:
        raise HTTPException(status_code=404, detail="Extension not found")
    return extension

@router.post("/extensions", response_model=Extension)
async def create_extension(extension: ExtensionCreate):
    extension_uuid = str(uuid.uuid4())
    
    # Build the insert query dynamically
    fields = ["extension_uuid", "domain_uuid"] + [k for k in extension.dict().keys() if k != "domain_uuid"]
    placeholders = ", ".join([f"${i+1}" for i in range(len(fields))])
    field_names = ", ".join(fields)
    
    query = f"""
        INSERT INTO v_extensions ({field_names})
        VALUES ({placeholders})
        RETURNING *
    """
    
    values = [extension_uuid, str(extension.domain_uuid)] + [
        str(v) if isinstance(v, uuid.UUID) and v else v 
        for k, v in extension.dict().items() if k != "domain_uuid"
    ]
    
    result = await baseDB.fetch_one(query, *values)
    
    # Get domain name for cache invalidation
    domain_query = "SELECT domain_name FROM v_domains WHERE domain_uuid = $1"
    domain_info = await baseDB.fetch_one(domain_query, str(extension.domain_uuid))
    
    if domain_info and result:
        user_context = result.get('user_context', domain_info['domain_name'])
        await invalidate_extension_cache(
            extension=result['extension'],
            user_context=user_context,
            number_alias=result.get('number_alias')
        )
    
    return result

@router.put("/extensions/{extension_uuid}", response_model=Extension)
async def update_extension(extension_uuid: UUID, extension: ExtensionUpdate):
    existing = await baseDB.fetch_one("SELECT * FROM v_extensions WHERE extension_uuid = $1", str(extension_uuid))
    if not existing:
        raise HTTPException(status_code=404, detail="Extension not found")
    
    update_data = extension.dict(exclude_unset=True)
    if not update_data:
        return existing
    
    # Handle UUID fields
    for key in update_data:
        if 'uuid' in key and update_data[key]:
            update_data[key] = str(update_data[key])
    
    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"UPDATE v_extensions SET {set_clause} WHERE extension_uuid = $1 RETURNING *"
    values = [str(extension_uuid)] + list(update_data.values())
    
    result = await baseDB.fetch_one(query, *values)
    
    # Invalidate extension cache after update
    if result:
        # Get domain name for user_context
        domain_query = "SELECT domain_name FROM v_domains WHERE domain_uuid = $1"
        domain_info = await baseDB.fetch_one(domain_query, result['domain_uuid'])
        
        if domain_info:
            user_context = domain_info['domain_name']
            
            # Clear cache for both old and new extension/alias if changed
            await invalidate_extension_cache(
                extension=existing['extension'],
                user_context=user_context,
                number_alias=existing.get('number_alias')
            )
            
            # If extension number or alias changed, also clear new cache
            if (update_data.get('extension') and update_data['extension'] != existing['extension']) or \
               (update_data.get('number_alias') and update_data['number_alias'] != existing.get('number_alias')):
                await invalidate_extension_cache(
                    extension=result['extension'],
                    user_context=user_context,
                    number_alias=result.get('number_alias')
                )
    
    return result

@router.delete("/extensions/{extension_uuid}")
async def delete_extension(extension_uuid: UUID):
    # Get extension info before deletion for cache invalidation
    existing = await baseDB.fetch_one("SELECT * FROM v_extensions WHERE extension_uuid = $1", str(extension_uuid))
    if not existing:
        raise HTTPException(status_code=404, detail="Extension not found")
    
    query = "DELETE FROM v_extensions WHERE extension_uuid = $1"
    result = await baseDB.execute(query, str(extension_uuid))
    
    # Invalidate extension cache after deletion
    domain_query = "SELECT domain_name FROM v_domains WHERE domain_uuid = $1"
    domain_info = await baseDB.fetch_one(domain_query, existing['domain_uuid'])
    
    if domain_info:
        user_context = existing.get('user_context', domain_info['domain_name'])
        await invalidate_extension_cache(
            extension=existing['extension'],
            user_context=user_context,
            number_alias=existing.get('number_alias')
        )
    
    return {"message": "Extension deleted successfully"}

# Extension Settings endpoints
@router.get("/extension-settings", response_model=List[ExtensionSetting])
async def get_extension_settings():
    query = "SELECT * FROM v_extension_settings ORDER BY extension_setting_name"
    return await baseDB.fetch_all(query)

@router.get("/extension-settings/extension/{extension_uuid}", response_model=List[ExtensionSetting])
async def get_extension_settings_by_extension(extension_uuid: UUID):
    query = "SELECT * FROM v_extension_settings WHERE extension_uuid = $1 ORDER BY extension_setting_name"
    return await baseDB.fetch_all(query, str(extension_uuid))

@router.post("/extension-settings", response_model=ExtensionSetting)
async def create_extension_setting(setting: ExtensionSettingCreate):
    setting_uuid = str(uuid.uuid4())
    query = """
        INSERT INTO v_extension_settings (
            extension_setting_uuid, extension_uuid, extension_setting_type,
            extension_setting_name, extension_setting_value, extension_setting_enabled
        )
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING *
    """
    result = await baseDB.fetch_one(
        query, setting_uuid, str(setting.extension_uuid), setting.extension_setting_type,
        setting.extension_setting_name, setting.extension_setting_value, setting.extension_setting_enabled
    )
    return result

@router.put("/extension-settings/{setting_uuid}", response_model=ExtensionSetting)
async def update_extension_setting(setting_uuid: UUID, setting: ExtensionSettingUpdate):
    existing = await baseDB.fetch_one(
        "SELECT * FROM v_extension_settings WHERE extension_setting_uuid = $1", 
        str(setting_uuid)
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Extension setting not found")
    
    update_data = setting.dict(exclude_unset=True)
    if not update_data:
        return existing
    
    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"UPDATE v_extension_settings SET {set_clause} WHERE extension_setting_uuid = $1 RETURNING *"
    values = [str(setting_uuid)] + list(update_data.values())
    
    result = await baseDB.fetch_one(query, *values)
    return result

@router.delete("/extension-settings/{setting_uuid}")
async def delete_extension_setting(setting_uuid: UUID):
    query = "DELETE FROM v_extension_settings WHERE extension_setting_uuid = $1"
    result = await baseDB.execute(query, str(setting_uuid))
    if result == 0:
        raise HTTPException(status_code=404, detail="Extension setting not found")
    return {"message": "Extension setting deleted successfully"}

# Voicemail endpoints
@router.get("/voicemails", response_model=List[Voicemail])
async def get_voicemails():
    query = "SELECT * FROM v_voicemails ORDER BY voicemail_id"
    return await baseDB.fetch_all(query)

@router.get("/voicemails/{voicemail_uuid}", response_model=Voicemail)
async def get_voicemail(voicemail_uuid: UUID):
    query = "SELECT * FROM v_voicemails WHERE voicemail_uuid = $1"
    voicemail = await baseDB.fetch_one(query, str(voicemail_uuid))
    if not voicemail:
        raise HTTPException(status_code=404, detail="Voicemail not found")
    return voicemail

@router.post("/voicemails", response_model=Voicemail)
async def create_voicemail(voicemail: VoicemailCreate):
    voicemail_uuid = str(uuid.uuid4())
    query = """
        INSERT INTO v_voicemails (
            voicemail_uuid, domain_uuid, voicemail_id, voicemail_enabled,
            voicemail_password, voicemail_attach_file, voicemail_local_after_email,
            voicemail_mail_to
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING *
    """
    result = await baseDB.fetch_one(
        query, voicemail_uuid, str(voicemail.domain_uuid), voicemail.voicemail_id,
        voicemail.voicemail_enabled, voicemail.voicemail_password,
        voicemail.voicemail_attach_file, voicemail.voicemail_local_after_email,
        voicemail.voicemail_mail_to
    )
    return result

@router.put("/voicemails/{voicemail_uuid}", response_model=Voicemail)
async def update_voicemail(voicemail_uuid: UUID, voicemail: VoicemailUpdate):
    existing = await baseDB.fetch_one("SELECT * FROM v_voicemails WHERE voicemail_uuid = $1", str(voicemail_uuid))
    if not existing:
        raise HTTPException(status_code=404, detail="Voicemail not found")
    
    update_data = voicemail.dict(exclude_unset=True)
    if not update_data:
        return existing
    
    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"UPDATE v_voicemails SET {set_clause} WHERE voicemail_uuid = $1 RETURNING *"
    values = [str(voicemail_uuid)] + list(update_data.values())
    
    result = await baseDB.fetch_one(query, *values)
    return result

@router.delete("/voicemails/{voicemail_uuid}")
async def delete_voicemail(voicemail_uuid: UUID):
    query = "DELETE FROM v_voicemails WHERE voicemail_uuid = $1"
    result = await baseDB.execute(query, str(voicemail_uuid))
    if result == 0:
        raise HTTPException(status_code=404, detail="Voicemail not found")
    return {"message": "Voicemail deleted successfully"}

# Dialplan endpoints
@router.get("/dialplans", response_model=List[Dialplan])
async def get_dialplans():
    query = "SELECT * FROM v_dialplans ORDER BY dialplan_order, dialplan_name"
    return await baseDB.fetch_all(query)

@router.get("/dialplans/{dialplan_uuid}", response_model=Dialplan)
async def get_dialplan(dialplan_uuid: UUID):
    query = "SELECT * FROM v_dialplans WHERE dialplan_uuid = $1"
    dialplan = await baseDB.fetch_one(query, str(dialplan_uuid))
    if not dialplan:
        raise HTTPException(status_code=404, detail="Dialplan not found")
    return dialplan

@router.post("/dialplans", response_model=Dialplan)
async def create_dialplan(dialplan: DialplanCreate):
    dialplan_uuid = str(uuid.uuid4())
    query = """
        INSERT INTO v_dialplans (
            dialplan_uuid, domain_uuid, dialplan_name, dialplan_context,
            dialplan_xml, dialplan_enabled, dialplan_order
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING *
    """
    result = await baseDB.fetch_one(
        query, dialplan_uuid, 
        str(dialplan.domain_uuid) if dialplan.domain_uuid else None,
        dialplan.dialplan_name, dialplan.dialplan_context, dialplan.dialplan_xml,
        dialplan.dialplan_enabled, dialplan.dialplan_order
    )
    return result

@router.put("/dialplans/{dialplan_uuid}", response_model=Dialplan)
async def update_dialplan(dialplan_uuid: UUID, dialplan: DialplanUpdate):
    existing = await baseDB.fetch_one("SELECT * FROM v_dialplans WHERE dialplan_uuid = $1", str(dialplan_uuid))
    if not existing:
        raise HTTPException(status_code=404, detail="Dialplan not found")
    
    update_data = dialplan.dict(exclude_unset=True)
    if not update_data:
        return existing
    
    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"UPDATE v_dialplans SET {set_clause} WHERE dialplan_uuid = $1 RETURNING *"
    values = [str(dialplan_uuid)] + list(update_data.values())
    
    result = await baseDB.fetch_one(query, *values)
    return result

@router.delete("/dialplans/{dialplan_uuid}")
async def delete_dialplan(dialplan_uuid: UUID):
    query = "DELETE FROM v_dialplans WHERE dialplan_uuid = $1"
    result = await baseDB.execute(query, str(dialplan_uuid))
    if result == 0:
        raise HTTPException(status_code=404, detail="Dialplan not found")
    return {"message": "Dialplan deleted successfully"}

# Registrations (read-only)
@router.get("/registrations", response_model=List[Registration])
async def get_registrations():
    query = "SELECT * FROM registrations ORDER BY reg_user, realm"
    return await baseDB.fetch_all(query)

@router.get("/registrations/{reg_uuid}", response_model=Registration)
async def get_registration(reg_uuid: UUID):
    query = "SELECT * FROM registrations WHERE reg_uuid = $1"
    registration = await baseDB.fetch_one(query, str(reg_uuid))
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    return registration