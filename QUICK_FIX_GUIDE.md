# Quick Fix Verification and Troubleshooting

## Immediate Actions to Take

### 1. Upload Modified Files to Server
```bash
# On your local machine (if using SCP/SFTP)
scp scripts/action/acl.lua root@your-server:/root/xml-handler/scripts/action/
scp scripts/index.lua root@your-server:/root/xml-handler/scripts/

# Or if you're editing directly on server, verify the changes were saved
```

### 2. Reload Lua Module in FreeSWITCH
```bash
# Connect to FreeSWITCH CLI
fs_cli

# Reload the Lua module
reload mod_lua
```

### 3. Test ACL Reload
```bash
# In FreeSWITCH CLI
reload acl

# You should now see these logs:
# [notice] [xml_handler] Handling acl.conf configuration request
# [notice] [acl] Starting ACL configuration generation
# [notice] [acl] Fetching whitelist from database
# etc...
```

### 4. Verify ACL Is Applied
```bash
# In FreeSWITCH CLI
show acl

# This should now show your database ACLs, not just the static file content
```

---

## Troubleshooting Checklist

### ❌ Problem: Still see "params object is NULL" error

**Cause:** FreeSWITCH is not properly passing the params object to Lua.

**Solutions:**
1. Check lua.conf.xml is in the correct location: `/usr/local/freeswitch/conf/autoload_configs/lua.conf.xml`
2. Verify the xml-handler-script parameter:
   ```xml
   <param name="xml-handler-script" value="/root/xml-handler/scripts/app.lua xml_handler"/>
   ```
3. Restart FreeSWITCH completely: `shutdown` then start again

---

### ❌ Problem: No logs showing "[acl]" prefix

**Cause:** The acl.lua file is not being executed.

**Solutions:**
1. Check that index.lua was updated correctly
2. Verify scripts_dir is set correctly in config.conf
3. Enable debug mode:
   ```lua
   -- In config.conf
   debug.xml_request = true
   ```
4. Check file permissions:
   ```bash
   chmod +x /root/xml-handler/scripts/action/acl.lua
   chmod +x /root/xml-handler/scripts/index.lua
   ```

---

### ❌ Problem: "database connection failed"

**Cause:** Database credentials or connection issue.

**Solutions:**
1. Check config.conf database settings:
   ```ini
   database.system.type = pgsql  # or mysql
   database.system.host = 127.0.0.1
   database.system.port = 5432
   database.system.name = your_database
   database.system.username = your_user
   database.system.password = your_password
   ```
2. Test database connection manually:
   ```bash
   psql -h 127.0.0.1 -U your_user -d your_database
   # or for MySQL:
   mysql -h 127.0.0.1 -u your_user -p your_database
   ```
3. Check if database table exists:
   ```sql
   SELECT * FROM fs_configuration WHERE config_type IN ('acl-white-list', 'acl-single');
   ```

---

### ❌ Problem: ACL XML generated but not applied

**Cause:** Static acl.conf.xml file is taking precedence.

**Solution:**
1. Temporarily rename the static file:
   ```bash
   cd /usr/local/freeswitch/conf/autoload_configs
   mv acl.conf.xml acl.conf.xml.backup
   ```
2. Reload ACL:
   ```bash
   # In FreeSWITCH CLI
   reload acl
   ```
3. Now FreeSWITCH MUST use your dynamic ACL handler

---

### ❌ Problem: "attempt to call global 'freeswitch' (a nil value)"

**Cause:** Running the script outside of FreeSWITCH context.

**Solution:**
- Don't run `lua acl.lua` directly from bash
- Only run via FreeSWITCH: `reload acl` or through XML handler

---

### ❌ Problem: Empty ACL list after reload

**Cause:** No data in database or query is returning empty results.

**Solutions:**
1. Check database has ACL entries:
   ```sql
   SELECT config_type, xml_content FROM fs_configuration 
   WHERE config_type IN ('acl-white-list', 'acl-single');
   ```
2. Insert test data:
   ```sql
   INSERT INTO fs_configuration (config_type, xml_content) 
   VALUES ('acl-white-list', '<node type="allow" cidr="127.0.0.1/32"/>');
   ```
3. Check logs for "Loaded X ACL entries" - if X is 0, database is empty

---

## Verification Commands

### Check FreeSWITCH is using correct lua.conf.xml
```bash
# FreeSWITCH CLI
xml_locate configuration lua.conf

# Should show your xml-handler-script configuration
```

### Check XML Handler Bindings
```bash
# Look for this in FreeSWITCH logs at startup
grep "xml-handler-bindings" /var/log/freeswitch/freeswitch.log

# Should show: directory,dialplan,configuration
```

### Test XML Generation Manually
```bash
# FreeSWITCH CLI
luarun /root/xml-handler/scripts/action/acl.lua

# This will show any Lua errors in the script
```

### Check Module Load Order
```bash
# FreeSWITCH CLI
module_exists mod_lua

# Should return: true
```

---

## Debug Mode

To see FULL XML output, enable debug mode:

1. Edit `scripts/config.conf`:
   ```ini
   debug.xml_string = true
   debug.xml_request = true
   debug.params = true
   ```

2. Reload Lua:
   ```bash
   reload mod_lua
   ```

3. Reload ACL:
   ```bash
   reload acl
   ```

4. Check logs - you'll see the complete generated XML

---

## Expected Success Indicators

When everything is working correctly, you'll see:

### ✅ In FreeSWITCH Logs (console or /var/log/freeswitch/freeswitch.log):
```
[notice] [xml_handler] Handling acl.conf configuration request
[notice] [acl] Starting ACL configuration generation
[notice] [acl] Fetching whitelist from database
[notice] [acl] Whitelist entries loaded
[notice] [acl] Fetching individual ACL entries from database
[notice] [acl] Loaded 3 ACL entries from database
[notice] [acl] Generated complete ACL XML configuration
[notice] [acl] XML_STRING length: 2048 bytes
```

### ✅ In FreeSWITCH CLI with `show acl`:
```
ACL name domains:
  allow domain $${domain}
  allow 192.168.1.0/24
  allow 10.0.0.0/8

ACL name my_custom_acl:
  deny 0.0.0.0/0
  allow 192.168.1.100/32
```

### ✅ Test ACL Enforcement:
```bash
# Try to connect from an allowed IP - should work
# Try to connect from a denied IP - should be blocked
```

---

## Quick Test Script

Create a simple test to verify database connectivity:

```bash
# Save as test_acl.lua
local Database = require "functions.database"
local dbh = Database.new('system')

print("Testing database connection...")

local sql = [[SELECT config_type, xml_content FROM fs_configuration WHERE config_type = 'acl-white-list' LIMIT 1]]
local found = false

dbh:query(sql, {}, function(row)
    print("Found ACL entry:")
    print("  Type: " .. row.config_type)
    print("  Content: " .. row.xml_content)
    found = true
end)

if not found then
    print("No ACL entries found in database!")
end

dbh:release()
print("Test complete")
```

Run it:
```bash
# FreeSWITCH CLI
luarun /root/xml-handler/scripts/test_acl.lua
```

---

## Common Configuration Mistakes

### ❌ Wrong: Mixing sections
```lua
xml:append([[<section name="directory">]])
xml:append([[  <configuration name="acl.conf">]])
```

### ✅ Correct: Proper section for ACL
```lua
xml:append([[<section name="configuration">]])
xml:append([[  <configuration name="acl.conf">]])
```

---

### ❌ Wrong: Hardcoded path in index.lua
```lua
dofile("/some/hardcoded/path/acl.lua")
```

### ✅ Correct: Use scripts_dir variable
```lua
dofile(scripts_dir.."/action/acl.lua")
```

---

### ❌ Wrong: No error handling
```lua
dbh:query(sql, {}, function(row)
    acl_list = acl_list .. row.xml_content
end)
```

### ✅ Correct: Check for nil/empty
```lua
dbh:query(sql, {}, function(row)
    if row.xml_content and #row.xml_content > 0 then
        acl_list = acl_list .. row.xml_content
    end
end)
```

---

## Need More Help?

### Check FreeSWITCH Logs
```bash
tail -f /var/log/freeswitch/freeswitch.log | grep -i "acl\|xml_handler"
```

### Enable Lua Debug
```bash
# In FreeSWITCH CLI
console loglevel debug
```

### Test Individual Components
1. Test database connection: Run test_acl.lua
2. Test XML generation: Check logs with debug enabled
3. Test XML application: Use `show acl` and test actual connections

---

## Summary

The fix is complete. The two critical changes were:

1. **Changed XML section from "directory" to "configuration"** in acl.lua
2. **Added explicit routing for acl.conf requests** in index.lua

These changes ensure that when you run `reload acl`, FreeSWITCH:
- Calls the correct XML handler
- Generates ACL XML from your database
- Applies the configuration in the correct XML section
- Uses your dynamic ACLs instead of the static file

**Next step:** Upload the fixed files and run `reload mod_lua` then `reload acl`!
