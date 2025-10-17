# ACL Request Flow - Visual Diagram

## BEFORE (Broken) ❌

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FreeSWITCH                                  │
│                                                                     │
│  User runs: reload acl                                             │
│      ↓                                                             │
│  XML Request Generated:                                            │
│    - section: "configuration"                                      │
│    - key_value: "acl.conf"                                         │
└──────────────────────────────┬──────────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────────────┐
│                   lua.conf.xml Handler                               │
│                                                                      │
│  <param name="xml-handler-script"                                   │
│         value="/root/xml-handler/scripts/app.lua xml_handler"/>     │
└──────────────────────────────┬───────────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────────────┐
│                      app.lua                                         │
│                                                                      │
│  Loads: /root/xml-handler/scripts/index.lua                         │
└──────────────────────────────┬───────────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────────────┐
│                     index.lua (OLD CODE)                             │
│                                                                      │
│  if (XML_REQUEST["section"] == "configuration") then                │
│      configuration = scripts_dir..                                  │
│        "/app/xml_handler/resources/scripts/configuration/"..        │
│        XML_REQUEST["key_value"]..".lua"                             │
│                                                                      │
│      // Tries to load:                                              │
│      // /root/xml-handler/scripts/app/xml_handler/resources/        │
│      //   scripts/configuration/acl.conf.lua                        │
│                                                                      │
│      if (file_exists(configuration)) then                           │
│          dofile(configuration)                                      │
│      end                                                            │
│  end                                                                │
│                                                                      │
│  ❌ FILE DOESN'T EXIST!                                              │
│  ❌ NOTHING HAPPENS!                                                 │
└──────────────────────────────┬───────────────────────────────────────┘
                               ↓
                          NO HANDLER
                               ↓
┌──────────────────────────────────────────────────────────────────────┐
│                      FreeSWITCH                                      │
│                                                                      │
│  No XML returned from Lua handler                                   │
│      ↓                                                              │
│  Falls back to static file:                                         │
│    /usr/local/freeswitch/conf/autoload_configs/acl.conf.xml         │
│      ↓                                                              │
│  ❌ USES OLD STATIC ACL (Database changes ignored)                   │
└──────────────────────────────────────────────────────────────────────┘
```

---

## AFTER (Fixed) ✅

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FreeSWITCH                                  │
│                                                                     │
│  User runs: reload acl                                             │
│      ↓                                                             │
│  XML Request Generated:                                            │
│    - section: "configuration"                                      │
│    - key_value: "acl.conf"                                         │
└──────────────────────────────┬──────────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────────────┐
│                   lua.conf.xml Handler                               │
│                                                                      │
│  <param name="xml-handler-script"                                   │
│         value="/root/xml-handler/scripts/app.lua xml_handler"/>     │
└──────────────────────────────┬───────────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────────────┐
│                      app.lua                                         │
│                                                                      │
│  Loads: /root/xml-handler/scripts/index.lua                         │
└──────────────────────────────┬───────────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────────────┐
│                     index.lua (NEW CODE)                             │
│                                                                      │
│  if (XML_REQUEST["section"] == "configuration") then                │
│      ✅ NEW: Check for acl.conf specifically                         │
│      if (XML_REQUEST["key_value"] == "acl.conf") then               │
│          consoleLog("[xml_handler] Handling acl.conf request")      │
│          dofile(scripts_dir.."/action/acl.lua")                     │
│      else                                                           │
│          // Try default path for other configs                      │
│      end                                                            │
│  end                                                                │
│                                                                      │
│  ✅ MATCH! Executes acl.lua                                          │
└──────────────────────────────┬───────────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────────────┐
│              scripts/action/acl.lua (FIXED)                          │
│                                                                      │
│  ✅ Connect to database                                              │
│  ✅ Query: SELECT xml_content FROM fs_configuration                  │
│           WHERE config_type = 'acl-white-list'                      │
│  ✅ Query: SELECT xml_content FROM fs_configuration                  │
│           WHERE config_type = 'acl-single'                          │
│                                                                      │
│  ✅ Build XML:                                                       │
│      <?xml version="1.0"?>                                          │
│      <document type="freeswitch/xml">                               │
│        <section name="configuration">  ← FIXED! Was "directory"     │
│          <configuration name="acl.conf">                            │
│            <network-lists>                                          │
│              <!-- Static base lists -->                             │
│              <!-- Database whitelist entries -->                    │
│              <!-- Database ACL lists -->                            │
│            </network-lists>                                         │
│          </configuration>                                           │
│        </section>                                                   │
│      </document>                                                    │
│                                                                      │
│  ✅ Set: XML_STRING = generated_xml                                  │
│  ✅ Log: "[acl] Generated complete ACL XML configuration"           │
└──────────────────────────────┬───────────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────────────┐
│                      FreeSWITCH                                      │
│                                                                      │
│  ✅ Receives XML_STRING from Lua handler                             │
│  ✅ Parses XML in CORRECT section (configuration)                    │
│  ✅ Applies ACL configuration to runtime                             │
│  ✅ DYNAMIC DATABASE ACLs NOW ACTIVE!                                │
│                                                                      │
│  Console output:                                                    │
│    [notice] [xml_handler] Handling acl.conf configuration request   │
│    [notice] [acl] Starting ACL configuration generation             │
│    [notice] [acl] Fetching whitelist from database                  │
│    [notice] [acl] Whitelist entries loaded                          │
│    [notice] [acl] Fetching individual ACL entries from database     │
│    [notice] [acl] Loaded 5 ACL entries from database                │
│    [notice] [acl] Generated complete ACL XML configuration          │
│    [notice] [acl] XML_STRING length: 2048 bytes                     │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Side-by-Side Request Handling

### Configuration Section Request (reload acl)

| Step | BEFORE ❌ | AFTER ✅ |
|------|-----------|---------|
| 1. Request | section="configuration", key_value="acl.conf" | section="configuration", key_value="acl.conf" |
| 2. index.lua | Tries non-existent path | Checks `if (key_value == "acl.conf")` |
| 3. Routing | ❌ File not found, no action | ✅ Routes to `/action/acl.lua` |
| 4. XML Generation | ❌ Never happens | ✅ Queries database, builds XML |
| 5. XML Section | N/A | ✅ `<section name="configuration">` |
| 6. FreeSWITCH Result | ❌ Uses static file | ✅ Applies dynamic ACL |

---

### Directory Section Request (switch_load_network_lists)

| Step | BEFORE ❌ | AFTER ✅ |
|------|-----------|---------|
| 1. Request | section="directory", function="switch_load_network_lists" | section="directory", function="switch_load_network_lists" |
| 2. directory.lua | Checks event_calling_function | Checks event_calling_function |
| 3. Routing | Routes to `/action/acl.lua` | Routes to `/action/acl.lua` |
| 4. XML Generation | Queries database, builds XML | Queries database, builds XML |
| 5. XML Section | ❌ `<section name="directory">` | ✅ `<section name="configuration">` |
| 6. FreeSWITCH Result | ❌ Ignores (wrong section) | ✅ Applies ACL |

---

## XML Section Validation

FreeSWITCH has strict XML section validation:

```
┌────────────────────────────────────────────────────┐
│              FreeSWITCH XML Sections               │
├────────────────────────────────────────────────────┤
│                                                    │
│  configuration  →  ACL, Sofia, Dialplan Settings  │
│                    Module configs                  │
│                                                    │
│  directory      →  User auth, Gateways            │
│                    Domain lookups                  │
│                                                    │
│  dialplan       →  Call routing rules              │
│                                                    │
│  phrases        →  IVR phrases, TTS                │
│                                                    │
│  languages      →  Language-specific settings      │
│                                                    │
└────────────────────────────────────────────────────┘

When you put ACL in "directory" section:
  FreeSWITCH says: "This is user/gateway data, not config"
  Result: ❌ IGNORES IT

When you put ACL in "configuration" section:
  FreeSWITCH says: "This is a configuration, process it"
  Result: ✅ APPLIES IT
```

---

## Database Query Flow

```
┌─────────────────────────────────────────────────────────┐
│                  PostgreSQL/MySQL Database              │
│                                                         │
│  Table: fs_configuration                                │
│  ┌───────────────┬─────────────────────────────────┐   │
│  │ config_type   │ xml_content                     │   │
│  ├───────────────┼─────────────────────────────────┤   │
│  │ acl-white-list│ <node type="allow" cidr="..."/> │   │
│  │ acl-single    │ <list name="...">...</list>     │   │
│  │ acl-single    │ <list name="...">...</list>     │   │
│  └───────────────┴─────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────┘
                         ↓
                    acl.lua queries
                         ↓
        ┌────────────────────────────────┐
        │  Query 1: acl-white-list       │
        │  → Gets whitelist nodes        │
        │  → Adds to <list name="domains">│
        └────────────────────────────────┘
                         ↓
        ┌────────────────────────────────┐
        │  Query 2: acl-single           │
        │  → Gets individual ACL lists   │
        │  → Appends to <network-lists>  │
        └────────────────────────────────┘
                         ↓
        ┌────────────────────────────────┐
        │  Combine all into XML:         │
        │  <configuration name="acl.conf">│
        │    <network-lists>             │
        │      <list name="lan">...</list>│
        │      <list name="domains">     │
        │        [whitelist nodes]       │
        │      </list>                   │
        │      [individual ACL lists]    │
        │    </network-lists>            │
        │  </configuration>              │
        └────────────────────────────────┘
```

---

## The Critical Fix in One Image

```
BEFORE:                        AFTER:
┌───────────────┐             ┌───────────────┐
│  reload acl   │             │  reload acl   │
└───────┬───────┘             └───────┬───────┘
        ↓                             ↓
  ❌ Path not found            ✅ Routes to acl.lua
        ↓                             ↓
  ❌ No XML returned            ✅ Queries database
        ↓                             ↓
  ❌ Static file used     ✅ Builds XML (configuration section)
        ↓                             ↓
  ❌ Database ignored             ✅ Returns XML_STRING
        ↓                             ↓
  ❌ ACL not updated              ✅ FreeSWITCH applies ACL
        ↓                             ↓
    FAILURE                       SUCCESS
```

---

## Summary

**Two small changes, massive impact:**

1. Changed one line in `acl.lua`: `directory` → `configuration`
2. Added routing logic in `index.lua` to handle `acl.conf` requests

**Result:** FreeSWITCH now properly receives and applies your dynamic database ACLs! 🎉
