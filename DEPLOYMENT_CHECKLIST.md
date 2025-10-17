# ACL Fix Deployment Checklist

## Pre-Deployment Verification

### ☐ Backup Current Files
```bash
# On your FreeSWITCH server
cd /root/xml-handler
cp scripts/action/acl.lua scripts/action/acl.lua.backup
cp scripts/index.lua scripts/index.lua.backup
cp /usr/local/freeswitch/conf/autoload_configs/acl.conf.xml \
   /usr/local/freeswitch/conf/autoload_configs/acl.conf.xml.backup
```

### ☐ Verify Database Has ACL Data
```sql
-- Connect to your database
SELECT config_type, xml_content 
FROM fs_configuration 
WHERE config_type IN ('acl-white-list', 'acl-single');

-- If no results, add test data:
INSERT INTO fs_configuration (config_type, xml_content) 
VALUES ('acl-white-list', '<node type="allow" cidr="127.0.0.1/32"/>');
```

### ☐ Check Current ACL State
```bash
# FreeSWITCH CLI
fs_cli
show acl

# Take note of current ACLs for comparison
```

---

## Deployment Steps

### Step 1: Upload Fixed Files
```bash
# From your Windows machine (where xml-handler folder is)
# Use WinSCP, FileZilla, or command line SCP

# Example using SCP (if you have it installed):
scp d:\Nexis\xml-handler\scripts\action\acl.lua root@your-server:/root/xml-handler/scripts/action/
scp d:\Nexis\xml-handler\scripts\index.lua root@your-server:/root/xml-handler/scripts/

# Or use your preferred SFTP client
```

### ☐ File Upload Confirmed
- [ ] acl.lua uploaded successfully
- [ ] index.lua uploaded successfully

---

### Step 2: Verify File Permissions
```bash
# On FreeSWITCH server
cd /root/xml-handler/scripts
chmod 644 action/acl.lua
chmod 644 index.lua
chown freeswitch:freeswitch action/acl.lua
chown freeswitch:freeswitch index.lua
```

### ☐ Permissions Set
- [ ] Files are readable by FreeSWITCH user
- [ ] Ownership is correct

---

### Step 3: Reload Lua Module
```bash
# FreeSWITCH CLI
fs_cli
reload mod_lua
```

### ☐ Module Reloaded
- [ ] No errors in console
- [ ] Lua module reloaded successfully

**Expected output:**
```
+OK Reloading XML
+OK module unloaded
+OK module loaded
```

---

### Step 4: Test ACL Reload
```bash
# FreeSWITCH CLI (still in fs_cli)
reload acl
```

### ☐ Check for Success Indicators

**You should see these logs:**
- [ ] `[notice] [xml_handler] Handling acl.conf configuration request`
- [ ] `[notice] [acl] Starting ACL configuration generation`
- [ ] `[notice] [acl] Fetching whitelist from database`
- [ ] `[notice] [acl] Whitelist entries loaded`
- [ ] `[notice] [acl] Fetching individual ACL entries from database`
- [ ] `[notice] [acl] Loaded X ACL entries from database`
- [ ] `[notice] [acl] Generated complete ACL XML configuration`
- [ ] `[notice] [acl] XML_STRING length: XXXX bytes`

**If you DON'T see these logs, STOP and troubleshoot!**

---

### Step 5: Verify ACL Applied
```bash
# FreeSWITCH CLI
show acl
```

### ☐ Verify Output
- [ ] ACLs from database are shown
- [ ] New ACLs appear that weren't there before
- [ ] ACL list matches database content

---

### Step 6: Test with Database Change
```sql
-- Add a new ACL entry
INSERT INTO fs_configuration (config_type, xml_content) 
VALUES ('acl-single', 
'<list name="test_dynamic_acl" default="deny">
    <node type="allow" cidr="10.10.10.10/32"/>
</list>');
```

```bash
# FreeSWITCH CLI
reload acl
show acl | grep test_dynamic_acl
```

### ☐ Dynamic Update Works
- [ ] New ACL appears in output
- [ ] Database changes are reflected in FreeSWITCH

---

## Post-Deployment Verification

### ☐ Test ACL Enforcement
```bash
# Test from allowed IP - should succeed
# Test from denied IP - should fail

# Check FreeSWITCH logs for ACL denials
tail -f /var/log/freeswitch/freeswitch.log | grep -i "acl"
```

### ☐ Performance Check
- [ ] FreeSWITCH is responsive
- [ ] Call processing works normally
- [ ] No memory leaks (check `top` or `htop`)

### ☐ Log Review
```bash
# Check for any errors
grep -i "error\|fail" /var/log/freeswitch/freeswitch.log | tail -20
```

---

## Rollback Plan (If Needed)

### If Something Goes Wrong:

#### Option 1: Restore Backup Files
```bash
cd /root/xml-handler
mv scripts/action/acl.lua.backup scripts/action/acl.lua
mv scripts/index.lua.backup scripts/index.lua

# FreeSWITCH CLI
reload mod_lua
```

#### Option 2: Use Static ACL File
```bash
# Restore static ACL file
mv /usr/local/freeswitch/conf/autoload_configs/acl.conf.xml.backup \
   /usr/local/freeswitch/conf/autoload_configs/acl.conf.xml

# FreeSWITCH CLI
reloadxml
```

#### Option 3: Restart FreeSWITCH
```bash
# If all else fails
systemctl restart freeswitch
# or
/etc/init.d/freeswitch restart
```

---

## Troubleshooting Checklist

### ☐ Issue: No [acl] logs appearing

**Possible causes and fixes:**

- [ ] Check index.lua was actually updated
  ```bash
  grep "acl.conf" /root/xml-handler/scripts/index.lua
  # Should show: if (XML_REQUEST["key_value"] == "acl.conf")
  ```

- [ ] Check scripts_dir is set correctly
  ```bash
  grep "scripts_dir" /root/xml-handler/scripts/functions/config.lua
  ```

- [ ] Verify lua.conf.xml binding includes "configuration"
  ```bash
  grep "xml-handler-bindings" /usr/local/freeswitch/conf/autoload_configs/lua.conf.xml
  # Should show: directory,dialplan,configuration
  ```

---

### ☐ Issue: Database connection error

**Possible causes and fixes:**

- [ ] Check database is running
  ```bash
  systemctl status postgresql  # or mysql
  ```

- [ ] Verify config.conf database settings
  ```bash
  cat /root/xml-handler/scripts/config.conf | grep database
  ```

- [ ] Test database connection manually
  ```bash
  psql -h 127.0.0.1 -U your_user -d your_database
  ```

---

### ☐ Issue: ACL still using static file

**Possible causes and fixes:**

- [ ] Rename static ACL file to force dynamic handler
  ```bash
  mv /usr/local/freeswitch/conf/autoload_configs/acl.conf.xml \
     /usr/local/freeswitch/conf/autoload_configs/acl.conf.xml.disabled
  ```

- [ ] Check XML section is "configuration" not "directory"
  ```bash
  grep "section name=" /root/xml-handler/scripts/action/acl.lua
  # Should show: <section name="configuration">
  ```

- [ ] Enable debug mode
  ```bash
  # Edit config.conf
  debug.xml_string = true
  debug.xml_request = true
  
  # Reload and test
  reload mod_lua
  reload acl
  ```

---

### ☐ Issue: "params object is NULL" error

**Possible causes and fixes:**

- [ ] Verify lua.conf.xml has correct xml-handler-script
  ```xml
  <param name="xml-handler-script" value="/root/xml-handler/scripts/app.lua xml_handler"/>
  ```

- [ ] Check XML_REQUEST is populated
  - This indicates FreeSWITCH is not calling the script correctly
  - May need to restart FreeSWITCH entirely

- [ ] Restart FreeSWITCH
  ```bash
  systemctl restart freeswitch
  ```

---

## Success Criteria

### ✅ All Tests Passed

- [x] Fixed files uploaded
- [x] Lua module reloaded without errors
- [x] `reload acl` shows [acl] log messages
- [x] `show acl` displays database ACLs
- [x] Database changes appear after `reload acl`
- [x] ACL enforcement works (connections blocked/allowed correctly)
- [x] No errors in FreeSWITCH logs
- [x] Performance is normal

**If all boxes are checked: DEPLOYMENT SUCCESSFUL! 🎉**

---

## Maintenance Notes

### Regular Tasks

**Weekly:**
- Review ACL logs for denied connections
- Check database for stale ACL entries

**Monthly:**
- Test ACL reload functionality
- Verify database backups include fs_configuration table

**After Changes:**
- Always run `reload acl` after database changes
- Check `show acl` to verify changes applied
- Test with actual connections

---

## Quick Reference Commands

```bash
# Reload Lua module
reload mod_lua

# Reload ACL configuration
reload acl

# Show current ACLs
show acl

# Check FreeSWITCH status
status

# View logs in real-time
tail -f /var/log/freeswitch/freeswitch.log

# Search for ACL-related logs
grep -i "acl" /var/log/freeswitch/freeswitch.log | tail -50

# Test Lua script manually
luarun /root/xml-handler/scripts/action/acl.lua

# Restart FreeSWITCH (if needed)
systemctl restart freeswitch
```

---

## Documentation Reference

- **ACL_FIX_SUMMARY.md** - Overview of changes
- **ACL_FIX_ANALYSIS.md** - Technical deep-dive
- **BEFORE_AFTER_COMPARISON.md** - Visual comparison
- **ACL_REQUEST_FLOW_DIAGRAM.md** - Flow diagrams
- **QUICK_FIX_GUIDE.md** - Troubleshooting guide

---

## Contact Information

**If you encounter issues not covered in this checklist:**

1. Check FreeSWITCH logs first
2. Enable debug mode in config.conf
3. Review the documentation files
4. Check database connectivity
5. Verify file permissions

---

## Deployment Sign-Off

**Deployed by:** ___________________  
**Date:** ___________________  
**Time:** ___________________  
**Result:** ☐ Success  ☐ Partial  ☐ Rollback Required  

**Notes:**
_____________________________________________________________
_____________________________________________________________
_____________________________________________________________

---

**END OF CHECKLIST**
