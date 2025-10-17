
--connect to the database
	local Database = require "functions.database"
	local log      = require "functions.log"["directory_acl"]
	local dbh = Database.new('system')
	
	-- Log that ACL generation has started
	freeswitch.consoleLog("notice", "[acl] Starting ACL configuration generation\n")

--include xml library
	local Xml = require "functions.xml";

--include json library
	local json
	if (debug["sql"]) then
		json = require "functions.lunajson"
	end

	local acl_white_list = ""
	-- Fetch whitelist
	local sql_white = [[SELECT xml_content FROM fs_configuration WHERE config_type = 'acl-white-list' LIMIT 1]]
	freeswitch.consoleLog("notice", "[acl] Fetching whitelist from database\n")
	dbh:query(sql_white, {}, function(row)
		if row.xml_content and #row.xml_content > 0 then
			acl_white_list = acl_white_list .. row.xml_content:gsub("^%s+", ""):gsub("%s+$", "") .. "\n"
			freeswitch.consoleLog("notice", "[acl] Added whitelist entry\n")
		end
	end)
	freeswitch.consoleLog("notice", "[acl] Whitelist entries loaded\n")

	local acl_fragments = ""
	-- Fetch all user ACLs (acl-single)
	local sql_user = [[SELECT xml_content FROM fs_configuration WHERE config_type = 'acl-single']]
	freeswitch.consoleLog("notice", "[acl] Fetching individual ACL entries from database\n")
	local acl_count = 0
	dbh:query(sql_user, {}, function(row)
		if row.xml_content and #row.xml_content > 0 then
			acl_fragments = acl_fragments .. row.xml_content:gsub("^%s+", ""):gsub("%s+$", "") .. "\n"
			acl_count = acl_count + 1
		end
	end)
	freeswitch.consoleLog("notice", "[acl] Loaded " .. acl_count .. " ACL entries from database\n")

	--build the xml
	local xml = Xml:new();
	xml:append([[<?xml version="1.0" encoding="UTF-8" standalone="no"?>]])
	xml:append([[<document type="freeswitch/xml">]])
	xml:append([[	<section name="configuration">]])


	-- Removed v_domains and v_extensions logic. Only generating ACL XML from fs_configuration.

	-- Insert ACL configuration as per fs_configuration
	xml:append([[		<configuration name="acl.conf" description="Network Lists">]])
	xml:append([[			<network-lists>]])
	xml:append([[				<list name="lan" default="allow">]])
	xml:append([[					<node type="deny" cidr="192.168.42.0/24"/>]])
	xml:append([[					<node type="allow" cidr="192.168.42.42/32"/>]])
	xml:append([[				</list>]])
	xml:append([[				<list name="socket_acl" default="deny">]])
	xml:append([[					<node type="allow" cidr="0.0.0.0/32"/>]])
	xml:append([[					<node type="allow" cidr="127.0.0.1/32"/>]])
	xml:append([[				</list>]])
	xml:append([[				<list name="domains" default="deny">]])
	xml:append([[					<node type="allow" domain="$${domain}"/>]])
	xml:append(acl_white_list)
	xml:append([[				</list>]])
	xml:append(acl_fragments)
	xml:append([[			</network-lists>]])
	xml:append([[		</configuration>]])

	xml:append([[	</section>]])
	xml:append([[</document>]])
	XML_STRING = xml:build();
	-- Write a clear runtime notice so logs show this action produced the ACL XML
	freeswitch.consoleLog("notice", "[acl] Generated complete ACL XML configuration\n");
	freeswitch.consoleLog("notice", "[acl] XML_STRING length: " .. #XML_STRING .. " bytes\n");
	if (debug["xml_string"]) then
		freeswitch.consoleLog("notice", "[acl] Full XML output:\n" .. XML_STRING .. "\n");
		log.notice("XML_STRING "..XML_STRING)
	end


--close the database connection
	dbh:release()