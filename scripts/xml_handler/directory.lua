--	directory.lua
--	Part of FusionPBX
--	Copyright (C) 2013 - 2021 Mark J Crane <markjcrane@fusionpbx.com>
--	All rights reserved.
--
--	Redistribution and use in source and binary forms, with or without
--	modification, are permitted provided that the following conditions are met:
--
--	1. Redistributions of source code must retain the above copyright notice,
--	   this list of conditions and the following disclaimer.
--
--	2. Redistributions in binary form must reproduce the above copyright
--	   notice, this list of conditions and the following disclaimer in the
--	   documentation and/or other materials provided with the distribution.
--
--	THIS SOFTWARE IS PROVIDED ''AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
--	INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
--	AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
--	AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
--	OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
--	SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
--	INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
--	CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
--	ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
--	POSSIBILITY OF SUCH DAMAGE.
--
--	Contributor(s):
--	Mark J Crane <markjcrane@fusionpbx.com>
--	Luis Daniel Lucio Quiroz <dlucio@okay.com.mx>

--set the default
	continue = true;

--debug: check if we have proper XML_REQUEST
	if (XML_REQUEST == nil) then
		freeswitch.consoleLog("warning", "[xml_handler][directory] XML_REQUEST is NULL - this may indicate improper script invocation\n");
	else
		freeswitch.consoleLog("notice", "[xml_handler][directory] XML_REQUEST section: " .. tostring(XML_REQUEST["section"]) .. "\n");
		freeswitch.consoleLog("notice", "[xml_handler][directory] XML_REQUEST key_value: " .. tostring(XML_REQUEST["key_value"]) .. "\n");
	end

--debug: log all available params
	-- if (params and params.serialize) then
	-- 	local serialized = params:serialize();
	-- 	if (serialized and serialized ~= "") then
	-- 		freeswitch.consoleLog("notice", "[xml_handler][directory] Available params:\n" .. serialized .. "\n");
	-- 	else
	-- 		freeswitch.consoleLog("notice", "[xml_handler][directory] params:serialize() returned empty\n");
	-- 	end
	-- end

--get the action
	action = params:getHeader("action");
	purpose = params:getHeader("purpose");
	--sip_auth - registration
	--group_call - call group has been called
	--user_call - user has been called
	freeswitch.consoleLog("info", "Action and Purpose " .. tostring(action) .. " : " .. tostring(purpose) .. "\n");

--additional information
	--event_calling_function = params:getHeader("Event-Calling-Function");

--set the variables as a string
	vm_mailto = "";

--include json library
	local json
	if (debug["sql"]) then
		json = require "functions.lunajson"
	end

--include xml library
	local Xml = require "functions.xml";

--include cache library
	local cache = require "functions.cache"

-- event source
	local event_calling_function = params:getHeader("Event-Calling-Function")
	local event_calling_file = params:getHeader("Event-Calling-File")

--determine the correction action to perform
	if (purpose == "gateways") then
		dofile(scripts_dir.."/action/domains.lua");
	elseif (action == "message-count") then
		dofile(scripts_dir.."/action/message-count.lua");
	elseif (action == "group_call") then
		dofile(scripts_dir.."/action/group_call.lua");
	elseif (action == "reverse-auth-lookup") then
		dofile(scripts_dir.."/action/reverse-auth-lookup.lua");
	elseif (event_calling_function == "switch_xml_locate_domain") then
		dofile(scripts_dir.."/action/domains.lua");
	elseif (event_calling_function == "switch_load_network_lists") then
		dofile(scripts_dir.."/action/acl.lua");
	elseif (event_calling_function == "populate_database") and (event_calling_file == "mod_directory.c") then
		dofile(scripts_dir.."/action/directory.lua");
	else
		--handle action
			--all other directory actions: sip_auth, user_call
			--except for the action: group_call

		-- Do we need use proxy to make call to ext. reged on different FS
		--   true - send call to FS where ext reged
		--   false - send call directly to ext
			local USE_FS_PATH = xml_handler and xml_handler["fs_path"]
			if (USE_FS_PATH == 'true') then
				USE_FS_PATH = true;
			else
				USE_FS_PATH = false;
			end

		-- Make sance only for extensions with number_alias
		--  false - you should register with AuthID=UserID=Extension (default)
		--  true  - you should register with AuthID=Extension and UserID=Number Alias
		-- 	also in this case you need 2 records in cache for one extension
			local DIAL_STRING_BASED_ON_USERID = xml_handler and xml_handler["reg_as_number_alias"]

		-- Use number as presence_id
		-- When you have e.g. extension like `user-100` with number-alias `100`
		-- by default presence_id is `user-100`. This option allow use `100` as presence_id
			local NUMBER_AS_PRESENCE_ID = xml_handler and xml_handler["number_as_presence_id"]

			local sip_auth_method = params:getHeader("sip_auth_method")
			if sip_auth_method then
				sip_auth_method = sip_auth_method:upper();
			end

		-- Get UserID. If used UserID ~= AuthID then we have to disable `inbound-reg-force-matching-username`
		-- on sofia profile and check UserID=Number-Alias and AuthID=Extension on register manually.
		-- But in load balancing mode in proxy INVITE we have UserID equal to origin UserID but 
		-- AuthID equal to callee AuthID. (e.g. 105 call to 100 and one FS forward call to other FS
		-- then we have UserID=105 but AuthID=100).
		-- Because we do not verify source of INVITE (FS or user device) we have to accept any UserID
		-- for INVITE in such mode. So we just substitute correct UserID for check.
		-- !!! NOTE !!! do not change USE_FS_PATH before this check.
			local from_user = params:getHeader("sip_from_user")
			if USE_FS_PATH and sip_auth_method == 'INVITE' then
				from_user = user
			end

		-- Check eather we need build dial-string. Before request dial-string FusionPBX set `dialed_extension`
		-- variable. So if we have no such variable we do not need build dial-string.
			dialed_extension = params:getHeader("dialed_extension") or  params:getHeader("sip_auth_username");
			if (dialed_extension == nil) then
				freeswitch.consoleLog("notice", "[xml_handler][directory] dialed_extension is null\n");
				USE_FS_PATH = false;
			else
				freeswitch.consoleLog("notice", "[xml_handler][directory] dialed_extension is " .. dialed_extension .. "\n");
			end

			-- verify from_user and number alias for this methods
			local METHODS = {
				-- _ANY_    = true,
				REGISTER = true,
				-- INVITE   = true,
			}

			if (user == nil) then
				user = "";
			end

			if (from_user == "") or (from_user == nil) then
				from_user = user
			end

		--prevent processing for invalid user
			if (user == "*97") or (user == "") then
				source = "";
				continue = false;
			end

		-- cleanup
			XML_STRING = nil;

		-- get the cache. We can use cache only if we do not use `fs_path`
		-- or we do not need dial-string. In other way we have to use database.
			if (continue) and (not USE_FS_PATH) then
				if (cache.support() and domain_name) then
					local key, err = "directory:" .. (from_user or user) .. "@" .. domain_name
					XML_STRING, err = cache.get(key);

					if debug['cache'] then
						if not XML_STRING then
							freeswitch.consoleLog("notice", "[xml_handler][directory][cache] get key: " .. key .. " fail: " .. tostring(err) .. "\n")
						else
							freeswitch.consoleLog("notice", "[xml_handler][directory][cache] get key: " .. key .. " pass!" .. "\n")
						end
					end
				end
				-- source = XML_STRING and "cache" or "database";
				source = "database";
			end

		--show the params in the console
			--if (params:serialize() ~= nil) then
			--	freeswitch.consoleLog("notice", "[xml_handler][directory] Params:\n" .. params:serialize() .. "\n");
			--end

			local loaded_from_db = false
		--build the XML string from the database
			if (source == "database") or (USE_FS_PATH) then
				loaded_from_db = true

				--include Database class
					local Database = require "functions.database";

				--database connection
					if (continue) then
						--connect to the database
							dbh = Database.new('system');

						--exits the script if we didn't connect properly
							assert(dbh:connected());

						--get the tenant_id  
							if (tenant_id == nil) then
								--get the tenant_id from tenant name (domain_name)
									if (domain_name ~= nil) then
										local sql = "SELECT id FROM tenants "
											.. "WHERE name = :domain_name ";
										local params = {domain_name = domain_name};
										if (debug["sql"]) then
											freeswitch.consoleLog("notice", "[xml_handler] SQL: " .. sql .. "; params:" .. json.encode(params) .. "\n");
										end
										dbh:query(sql, params, function(rows)
											tenant_id = rows["id"];
										end);
									end
									freeswitch.consoleLog("notice", "[xml_handler][directory] tenant_id is " .. tostring(tenant_id) .. "\n");
							end
					end

				--dial string and other settings are now included in the pre-built XML content
					--no need to query default settings
 
				--prevent processing for invalid tenants
					if (tenant_id == nil) then
						continue = false;
					end

				--load balancing features are handled in the pre-built XML content
					--skipping USE_FS_PATH logic for simplified implementation

				--get the directory configuration from fs_configuration table
					if (continue) then
						local sql = "SELECT fc.xml_content FROM fs_configuration fc "
							.. "JOIN tenants t ON t.id = fc.tenant_id "
							.. "WHERE t.id = :tenant_id "
							.. "AND fc.config_type = 'directory' "
							.. "AND fc.config_name = :user "
							.. "AND fc.is_active = true ";
						local params = {tenant_id=tenant_id, user=user};
						if (debug["sql"]) then
							freeswitch.consoleLog("notice", "[xml_handler] SQL: " .. sql .. "; params:" .. json.encode(params) .. "\n");
						end
						continue = false;
						dbh:query(sql, params, function(row)
							--store the pre-built XML content
								continue = true;
								directory_xml_content = row.xml_content;
								freeswitch.consoleLog("notice", "[xml_handler][directory] Found directory configuration for user: " .. user .. "\n");
						end);
					end

				--extension settings are now included in the pre-built XML content
					--no need to query v_extension_settings table

				--voicemail settings are now included in the pre-built XML content
					--no need to query v_voicemails table

				--if the directory configuration does not exist set continue to false;
					if (directory_xml_content == nil) then
						continue = false;
					end

				--use the pre-built XML content from fs_configuration table
					if (continue and directory_xml_content) then
						XML_STRING = directory_xml_content;
						
						--close the database connection
						dbh:release();

						--set the cache
						if cache.support() then
							local key = "directory:" .. user .. "@" .. domain_name
							if debug['cache'] then
								freeswitch.consoleLog("notice", "[xml_handler][directory][cache] set key: " .. key .. "\n")
							end
							local ok, err = cache.set(key, XML_STRING, expire["directory"])
							if debug["cache"] and not ok then
								freeswitch.consoleLog("warning", "[xml_handler][directory][cache] set key: " .. key .. " fail: " .. tostring(err) .. "\n");
							end
						else
							if debug["cache"] then
								freeswitch.consoleLog("warning", "[xml_handler][directory][cache] not set key: " .. key .. " cache not supported\n");
							end
						end

						--send the xml to the console
						if (debug["xml_string"]) then
							local file = assert(io.open(temp_dir .. "/" .. user .. "@" .. domain_name .. ".xml", "w"));
							file:write(XML_STRING);
							file:close();
						end

						--send to the console
						if (debug["cache"]) then
							freeswitch.consoleLog("notice", "[xml_handler] directory:" .. user .. "@" .. domain_name .. " source: database\n");
						end
					end
			end

		--get the XML string from the cache
			if (source == "cache") then
				--send to the console
					if (debug["cache"]) then
						if (XML_STRING) then
							freeswitch.consoleLog("notice", "[xml_handler] directory:" .. user .. "@" .. domain_name .. " source: cache \n");
						end
					end
			end
	end --if action

--if the extension does not exist send "not found"
	if not XML_STRING then
		--send not found but do not cache it
			XML_STRING = [[<?xml version="1.0" encoding="UTF-8" standalone="no"?>
			<document type="freeswitch/xml">
				<section name="result">
					<result status="not found" />
				</section>
			</document>]];
		--set the cache
			--local key = "directory:" .. user .. "@" .. domain_name;
			--ok, err = cache.set(key, XML_STRING, expire["directory"]);
			--freeswitch.consoleLog("notice", "[xml_handler] " .. user .. "@" .. domain_name .. "\n");
	end

--send the xml to the console
	if (debug["xml_string"]) then
		freeswitch.consoleLog("notice", "[xml_handler] XML_STRING: \n" .. XML_STRING .. "\n");
	end