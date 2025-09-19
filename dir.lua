-- FreeSWITCH Lua Directory and Dialplan Handler
-- Save this as /usr/local/freeswitch/scripts/directory.lua

-- Get the XML request parameters based on actual FreeSWITCH parameter names
local domain = params:getHeader("domain")
local key_name = params:getHeader("key")  -- This is "id" in your logs
local key_value = params:getHeader("user")  -- This is "1001" in your logs
local section = params:getHeader("section")
local tag_name = params:getHeader("tag")
local purpose = params:getHeader("purpose")
local action = params:getHeader("action")

-- Debug logging with actual parameter names
freeswitch.consoleLog("INFO", "Lua XML Handler - Section: " .. (section or "nil") .. 
                      " Action: " .. (action or "nil") ..
                      " Domain: " .. (domain or "nil") .. 
                      " Key: " .. (key_name or "nil") .. 
                      " User: " .. (key_value or "nil") ..
                      " Tag: " .. (tag_name or "nil"))

-- Additional debug for SIP auth
if action == "sip_auth" then
    freeswitch.consoleLog("INFO", "SIP Auth request detected for user: " .. (key_value or "unknown"))
end

-- Handle directory requests (section can be nil for SIP auth requests)
if section == "directory" or (action == "sip_auth" and key_name == "id") then
    -- Define our users
    local users = {
        ["1001"] = {
            password = "1234",
            vm_password = "1001"
        },
        ["1002"] = {
            password = "1234", 
            vm_password = "1002"
        }
    }
    
    if key_name == "id" and users[key_value] then
        local user = users[key_value]
        freeswitch.consoleLog("INFO", "Found user: " .. key_value .. " generating XML")
        XML_STRING = [[
<document type="freeswitch/xml">
  <section name="directory">
    <domain name="]] .. domain .. [[">
      <params>
        <param name="dial-string" value="{^^:sip_invite_domain=${dialed_domain}:presence_id=${dialed_user}@${dialed_domain}}${sofia_contact(*/${dialed_user}@${dialed_domain})}"/>
      </params>
      <groups>
        <group name="default">
          <users>
            <user id="]] .. key_value .. [[">
              <params>
                <param name="password" value="]] .. user.password .. [["/>
                <param name="vm-password" value="]] .. user.vm_password .. [["/>
              </params>
              <variables>
                <variable name="toll_allow" value="domestic,international,local"/>
                <variable name="accountcode" value="]] .. key_value .. [["/>
                <variable name="user_context" value="default"/>
                <variable name="effective_caller_id_name" value="Extension ]] .. key_value .. [["/>
                <variable name="effective_caller_id_number" value="]] .. key_value .. [["/>
                <variable name="outbound_caller_id_name" value="FreeSWITCH"/>
                <variable name="outbound_caller_id_number" value="]] .. key_value .. [["/>
                <variable name="callgroup" value="techsupport"/>
              </variables>
            </user>
          </users>
        </group>
      </groups>
    </domain>
  </section>
</document>]]
    else
        -- Return empty result for unknown users
        freeswitch.consoleLog("INFO", "User not found: " .. (key_value or "nil"))
        XML_STRING = [[
<document type="freeswitch/xml">
  <section name="directory">
    <result status="not found" />
  </section>
</document>]]
    end

-- Handle dialplan requests    
elseif section == "dialplan" then
    local context = params:getHeader("Caller-Context") or "default"
    local destination = params:getHeader("Caller-Destination-Number")
    
    if context == "default" then
        XML_STRING = [[
<document type="freeswitch/xml">
  <section name="dialplan" description="RE Dial Plan For FreeSWITCH">
    <context name="default">
    
      <!-- Extension to Extension calling -->
      <extension name="Local_Extension">
        <condition field="destination_number" expression="^(100[1-2])$">
          <action application="export" data="dialed_extension=$1"/>
          <action application="bind_meta_app" data="1 b s execute_extension::dx XML features"/>
          <action application="bind_meta_app" data="2 b s record_session::$${recordings_dir}/${caller_id_number}.${strftime(%Y-%m-%d-%H-%M-%S)}.wav"/>
          <action application="bind_meta_app" data="3 b s execute_extension::cf XML features"/>
          <action application="set" data="ringback=${us-ring}"/>
          <action application="set" data="transfer_ringback=$${hold_music}"/>
          <action application="set" data="call_timeout=30"/>
          <action application="set" data="hangup_after_bridge=true"/>
          <action application="set" data="continue_on_fail=true"/>
          <action application="bridge" data="user/${dialed_extension}@${domain_name}"/>
          <action application="answer"/>
          <action application="sleep" data="1000"/>
          <action application="bridge" data="loopback/app=voicemail:default ${domain_name} ${dialed_extension}"/>
        </condition>
      </extension>
      
      <!-- Echo test -->
      <extension name="echo">
        <condition field="destination_number" expression="^9996$">
          <action application="answer"/>
          <action application="echo"/>
        </condition>
      </extension>
      
      <!-- Hold music test -->
      <extension name="hold_music">
        <condition field="destination_number" expression="^9999$">
          <action application="answer"/>
          <action application="playback" data="$${hold_music}"/>
        </condition>
      </extension>
      
    </context>
  </section>
</document>]]
    else
        -- Return empty for other contexts
        XML_STRING = [[
<document type="freeswitch/xml">
  <section name="dialplan">
    <result status="not found" />
  </section>
</document>]]
    end
else
    -- Return empty for other sections
    XML_STRING = [[
<document type="freeswitch/xml">
  <result status="not found" />
</document>]]
end