--	dialplan.lua
--	Part of FusionPBX
--	Copyright (C) 2013-2024 Mark J Crane <markjcrane@fusionpbx.com>
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

--includes
	local cache = require"functions.cache"
	local log = require"functions.log"["xml_handler"]

--include xml library
	local Xml = require "functions.xml";

--connect to the database
	local Database = require "functions.database";
	dbh = Database.new('system');

--needed for cli-command xml_locate dialplan
	if (call_context == nil) then
		call_context = "public";
	end

--get the dialplan mode from the cache
	dialplan_destination_key = "dialplan:destination";
	dialplan_destination, err = cache.get(dialplan_destination_key);

--if not found in the cache then set default
	if (err == 'NOT FOUND') then
		--set the default dialplan destination
		dialplan_destination = "destination_number";
		
		--cache the default value
		if (dialplan_destination) then
			local ok, err = cache.set(dialplan_destination_key, dialplan_destination, expire["dialplan"]);
		end

		--send a message to the log
		if (debug['cache']) then
			log.notice(dialplan_destination_key.." source: default destination: "..dialplan_destination);
		end
	else
		--send a message to the log
		if (debug['cache']) then
			log.notice(dialplan_destination_key.." source: cache destination: "..dialplan_destination);
		end
	end

--get the dialplan mode from the cache
	dialplan_mode_key = "dialplan:mode";
	dialplan_mode, err = cache.get(dialplan_mode_key);

--if not found in the cache then set default
	if (err == 'NOT FOUND') then
		--set the default dialplan mode
		dialplan_mode = "multiple";
		
		--cache the default value
		if (dialplan_mode) then
			local ok, err = cache.set(dialplan_mode_key, dialplan_mode, expire["dialplan"]);
		end

		--send a message to the log
		if (debug['cache']) then
			log.notice(dialplan_mode_key.." source: default mode: "..dialplan_mode);
		end
	else
		--send a message to the log
		if (debug['cache']) then
			log.notice(dialplan_mode_key.." source: cache mode: "..dialplan_mode);
		end
	end

--set the defaults
	if (dialplan_mode == nil or dialplan_mode == '') then
		dialplan_mode = "multiple";
	end
	domain_name = 'global';

--get the context
	local context_name = call_context;
	if (call_context == "public" or string.sub(call_context, 0, 7) == "public@" or string.sub(call_context, -7) == ".public") then
		context_name = 'public';
	end

--use alternative sip_to_user instead of the default
	if (dialplan_destination == '${sip_to_user}' or dialplan_destination == 'sip_to_user') then
		destination_number = api:execute("url_decode", sip_to_user);
	end

--use alternative sip_req_user instead of the default
	if (dialplan_destination == '${sip_req_user}' or dialplan_destination == 'sip_req_user') then
		destination_number = api:execute("url_decode", sip_req_user);
	end

--set the dialplan cache key
	local dialplan_cache_key = "dialplan:" .. call_context;
	if (context_name == 'public' and dialplan_mode == "single") then
		dialplan_cache_key = "dialplan:" .. call_context .. ":" .. destination_number;
	end

--log the dialplan mode and dialplan cache key
	freeswitch.consoleLog("notice", "[xml_handler] ".. dialplan_mode .. " key:" .. dialplan_cache_key .. "\n");

--get the cache
	XML_STRING, err = cache.get(dialplan_cache_key);
	if (debug['cache']) then
		if XML_STRING then
			log.notice(dialplan_cache_key.." source: cache");
		elseif err ~= 'NOT FOUND' then
			log.notice("get element from the cache: " .. err);
		end
	end

--set the cache
	if (not XML_STRING) then

		--include json library
			local json
			if (debug["sql"]) then
				json = require "functions.lunajson"
			end

		--exits the script if we didn't connect properly
			assert(dbh:connected());

		-- set the start time of the query
			local start_time = os.time();

		-- set the timeout value as needed
			local timeout_seconds = 10;

		--get the hostname
			hostname = trim(api:execute("hostname", ""));

		--set the xml array and then concatenate the array to a string
			local xml = Xml:new();
			xml:append([[<?xml version="1.0" encoding="UTF-8" standalone="no"?>]]);
			xml:append([[<document type="freeswitch/xml">]]);
			xml:append([[	<section name="dialplan" description="">]]);
			xml:append([[		<context name="]] .. xml.sanitize(call_context) .. [[" destination_number="]] .. xml.sanitize(destination_number) .. [[" hostname="]] .. xml.sanitize(hostname) .. [[">]]);

		--get the dialplan xml from fs_configuration table
			if (context_name == 'public' and dialplan_mode == 'single') then
				--get the inbound route dialplan xml for specific destination number from fs_configuration table
				sql = "SELECT fc.xml_content "
				sql = sql .. "FROM fs_configuration fc "
				sql = sql .. "WHERE fc.config_type = 'inbound' "
				sql = sql .. "AND fc.config_name = :destination_number "
				sql = sql .. "AND fc.is_active = true "
				sql = sql .. "ORDER BY fc.id ASC ";
				local params = {destination_number = destination_number};
				if (debug["sql"]) then
					freeswitch.consoleLog("notice", "[dialplan] SQL: " .. sql .. "; params:" .. json.encode(params) .. "\n");
				end
				dbh:query(sql, params, function(row)
					dialplan_found = true;
					xml:append(row.xml_content);
				end);

				--handle not found
				if (dialplan_found == nil) then
					--check if the sql query timed out
					local current_time = os.time();
					local elapsed_time = current_time - start_time;
					if elapsed_time > timeout_seconds then
						--sql query timed out - unset the xml object to prevent the xml not found
						xml = nil;
					end

					if (xml ~= nil) then
						--sanitize the destination if not numeric
						if (type(destination_number) == "string") then
							destination_number = destination_number:gsub("^%+", "");
							destination_number = tonumber(destination_number);
							if (type(tonumber(destination_number)) ~= "number") then
								destination_number = 'not numeric';
							end
						end
						if (type(destination_number) == "numeric") then
							destination_number = tostring(destination_number);
						end

						--build 404 not found XML
						xml:append([[		<extension name="not-found" continue="false" uuid="9913df49-0757-414b-8cf9-bcae2fd81ae7">]]);
						xml:append([[			<condition field="" expression="">]]);
						xml:append([[				<action application="set" data="call_direction=inbound" inline="true"/>]]);
						xml:append([[				<action application="log" data="WARNING [inbound routes] 404 not found ${sip_network_ip} ]]..destination_number..[[" inline="true"/>]]);
						xml:append([[			</condition>]]);
						xml:append([[		</extension>]]);
					end
				end
			else
				--get the domain dialplan xml from fs_configuration table  
				sql = "SELECT fc.xml_content "
				sql = sql .. "FROM fs_configuration fc "
				sql = sql .. "JOIN tenants t ON t.id = fc.tenant_id "
				sql = sql .. "WHERE fc.config_type = 'dialplan' ";
				
				-- For public context or contexts with @ symbol, use exact match
				if (context_name == "public" or string.match(context_name, "@")) then
					sql = sql .. "AND fc.config_name = :call_context ";
				else
					-- For domain contexts, match against tenant name extracted from context
					local tenant_name = string.match(call_context, "([^@]+)")
					if tenant_name then
						sql = sql .. "AND t.name = :tenant_name ";
						params = {tenant_name = tenant_name};
					else
						sql = sql .. "AND fc.config_name = :call_context ";
						params = {call_context = call_context};
					end
				end
				
				sql = sql .. "AND fc.is_active = true "
				sql = sql .. "ORDER BY fc.id ASC ";
				
				if not params then
					params = {call_context = call_context};
				end
				
				if (debug["sql"]) then
					freeswitch.consoleLog("notice", "[dialplan] SQL: " .. sql .. "; params:" .. json.encode(params) .. "\n");
				end
				dbh:query(sql, params, function(row)
					dialplan_found = true;
					xml:append(row.xml_content);
				end);
			end

		--set the xml array and then concatenate the array to a string
			if (dialplan_found ~= nil and dialplan_found) then
				xml:append([[		</context>]]);
				xml:append([[	</section>]]);
				xml:append([[</document>]]);
				XML_STRING = xml:build();
			end

		--close the database connection
			dbh:release();

		--set the cache
			if (XML_STRING ~= nil) then
				local ok, err = cache.set(dialplan_cache_key, XML_STRING, expire["dialplan"]);
				if debug["cache"] then
					if ok then
						freeswitch.consoleLog("notice", "[xml_handler] " .. dialplan_cache_key .. " stored in the cache\n");
					else
						freeswitch.consoleLog("warning", "[xml_handler] " .. dialplan_cache_key .. " can not be stored in the cache: " .. tostring(err) .. "\n");
					end
				end
			end

		--send to the console
			if (debug["cache"]) then
				freeswitch.consoleLog("notice", "[xml_handler] " .. dialplan_cache_key .. " source: database\n");
			end
	else
		--send to the console
			if (debug["cache"]) then
				freeswitch.consoleLog("notice", "[xml_handler] " .. dialplan_cache_key .. " source: cache\n");
			end
	end --if XML_STRING

--send the xml to the console
	if (debug["xml_string"]) then
		local file = assert(io.open(temp_dir .. "/" .. dialplan_cache_key .. ".xml", "w"));
		file:write(XML_STRING);
		file:close();
	end