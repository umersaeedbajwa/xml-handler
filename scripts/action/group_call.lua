--	xml_handler.lua
--	Part of FusionPBX
--	Copyright (C) 2013 Mark J Crane <markjcrane@fusionpbx.com>
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
--	THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
--	INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
--	AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
--	AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
--	OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
--	SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
--	INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
--	CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
--	ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
--	POSSIBILITY OF SUCH DAMAGE.

--include xml library
	local Xml = require "functions.xml";

--include cache library
	local cache = require "functions.cache"

--get the cache
	local cache_key = "directory:groups:" .. user .. "@" .. domain_name;
	XML_STRING, err = cache.get(cache_key);
	
	if (debug['cache']) then
		if not XML_STRING then
			freeswitch.consoleLog("notice", "[xml_handler][group_call][cache] get key: " .. cache_key .. " fail: " .. tostring(err) .. "\n")
		else
			freeswitch.consoleLog("notice", "[xml_handler][group_call][cache] get key: " .. cache_key .. " pass!" .. "\n")
		end
	end

--set the cache
	if not XML_STRING then
		--connect to the database
			local Database = require "functions.database";
			local dbh = Database.new('system');

		--include json library
			local json
			if (debug["sql"]) then
				json = require "functions.lunajson"
			end

		--exits the script if we didn't connect properly
			assert(dbh:connected());

		--get the tenant_id
			if (tenant_id == nil) then
				--get the tenant_id
					if (domain_name ~= nil) then
						local sql = "SELECT id FROM tenants ";
						sql = sql .. "WHERE name = :domain_name ";
						local params = {domain_name = domain_name};
						if (debug["sql"]) then
							freeswitch.consoleLog("notice", "[xml_handler] SQL: " .. sql .. "; params: " .. json.encode(params) .. "\n");
						end
						dbh:query(sql, params, function(rows)
							tenant_id = rows["id"];
						end);
					end
			end

			if not tenant_id then
				freeswitch.consoleLog("warning", "[xml_handler] Can not find tenant name: " .. tostring(domain_name) .. "\n");
				return
			end

		--get the pre-built group call XML from fs_configuration
			local sql = [[
			SELECT fc.xml_content
			FROM fs_configuration fc
			WHERE fc.tenant_id = :tenant_id
			AND fc.config_type = 'groups'
			AND fc.config_name = :user
			AND fc.is_active = true
			]];
			local params = {tenant_id = tenant_id, user = user};
			if (debug["sql"]) then
				freeswitch.consoleLog("notice", "[xml_handler] SQL: " .. sql .. "; params: " .. json.encode(params) .. "\n");
			end
			
			group_found = false;
			dbh:query(sql, params, function(row)
				--use the pre-built XML content from fs_configuration table
				XML_STRING = row.xml_content;
				group_found = true;
				freeswitch.consoleLog("notice", "[xml_handler][group_call] Found group configuration for: " .. user .. "\n");
			end);

		--if no group configuration found, return not found
			if not group_found then
				XML_STRING = [[<?xml version="1.0" encoding="UTF-8" standalone="no"?>
				<document type="freeswitch/xml">
					<section name="result">
						<result status="not found" />
					</section>
				</document>]];
			end

		--close the database connection
			dbh:release();

		--set the cache
			if XML_STRING and cache.support() then
				local ok, err = cache.set(cache_key, XML_STRING, expire["directory"])
				if debug["cache"] then
					if ok then
						freeswitch.consoleLog("notice", "[xml_handler][group_call] " .. cache_key .. " stored in the cache\n");
					else
						freeswitch.consoleLog("warning", "[xml_handler][group_call] " .. cache_key .. " can not be stored in the cache: " .. tostring(err) .. "\n");
					end
				end
			end

		--send to the console
			if (debug["cache"]) then
				freeswitch.consoleLog("notice", "[xml_handler] " .. cache_key .. " source: database\n");
			end

	else
		--send to the console
			if (debug["cache"]) then
				if (XML_STRING) then
					freeswitch.consoleLog("notice", "[xml_handler] " .. cache_key .. " source: cache\n");
				end
			end
	end

--send the xml to the console
	if (debug["xml_string"]) then
		freeswitch.consoleLog("notice", "[xml_handler] directory:groups:"..domain_name.." XML_STRING: \n" .. XML_STRING .. "\n");
	end