To ensure the code runs correctly, you need to:

1. Install a Redis Lua library, such as `lua-redis` or any compatible library.
2. Verify that the library is accessible in the Lua environment.

sudo apt update
sudo apt install luarocks

luarocks install redis-lua

sudo apt update
sudo apt install lua5.2 liblua5.2-dev

lua -e "local redis = require('redis'); print('Redis library loaded successfully!')"

sudo nano /etc/luarocks/config-5.2.lua
lua_version = "5.2"
variables = {
   LUA = "/usr/bin/lua5.2"
}