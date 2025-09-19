# FreeSWITCH Python Dialplan Handler - Full Version

**Complete feature set with advanced capabilities and extensive tooling.**

## 📂 Files

- **`dialplan_handler.py`** - Full-featured dialplan engine with logging (~800 lines)
- **`xml_server.py`** - Production HTTP server with debugging
- **`example.py`** - Comprehensive examples and demos
- **`dialplan_cli.py`** - Command-line management tool
- **`test_dialplan.py`** - Complete test suite
- **`demo_dialplan.py`** - Interactive demonstration

## 🚀 Quick Start

### 1. Setup Database with Examples
```bash
python example.py
```

### 2. Use CLI Tool
```bash
# List all extensions
python dialplan_cli.py list

# Add new extension
python dialplan_cli.py add --context default --extension "^(11[0-9][0-9])$" --action bridge --data "user/$1@${domain}" --order 100

# Export to XML files
python dialplan_cli.py export
```

### 3. Start Production Server
```bash
python xml_server.py localhost 8080 dialplan.db --debug
```

### 4. Run Tests
```bash
python test_dialplan.py
```

## 💡 Advanced Usage

```python
from dialplan_handler import DialplanHandler, DialplanDatabase

# Full initialization with logging
handler = DialplanHandler("pbx.db", cache_ttl=300, enable_logging=True)

# Complex multi-condition extension
extension_id = handler.add_extension("Sales Queue", "default", 200)

# Multiple conditions with different break behaviors
handler.add_condition(extension_id, "destination_number", "^(2000)$", "true", 1)
handler.add_condition(extension_id, "time", "09:00-17:00", "false", 2)  # No break

# Multiple actions
handler.add_action(extension_id, 1, "answer", "", 1)
handler.add_action(extension_id, 2, "queue", "sales@${domain}", 2)
handler.add_action(extension_id, 3, "playback", "queue-full.wav", 3)

# Advanced caching with statistics
cache_stats = handler.get_cache_stats()
print(f"Cache hit rate: {cache_stats['hit_rate']:.2%}")
```

## 🔧 CLI Tool Features

```bash
# Database management
python dialplan_cli.py init --domain example.com
python dialplan_cli.py backup dialplan_backup.db

# Extension management
python dialplan_cli.py search "bridge"
python dialplan_cli.py delete 1001
python dialplan_cli.py test-xml --context default --extension 1001

# Bulk operations
python dialplan_cli.py import extensions.csv
python dialplan_cli.py export --format xml --output dialplans/
```

## ✨ Advanced Features

- 🚀 **Performance Monitoring** - Detailed timing and cache statistics
- 📊 **Comprehensive Logging** - Debug, info, warning, error levels
- 🔍 **CLI Management** - Full command-line interface for operations
- 🧪 **Test Suite** - Comprehensive unit and integration tests
- 📈 **Caching Analytics** - Hit rates, performance metrics
- 🌐 **Multi-domain Support** - Complex tenant management
- 🔄 **Database Migration** - Schema versioning and updates
- 📋 **XML Validation** - Strict FreeSWITCH format checking
- 🛠️ **Developer Tools** - Interactive demos and examples

## 🎯 Production Features

- **Error Recovery** - Graceful handling of database issues
- **Connection Pooling** - Efficient database connections
- **Memory Management** - Smart cache eviction policies
- **Security** - SQL injection protection, input validation
- **Monitoring** - Health checks and performance metrics
- **Documentation** - Extensive inline documentation

## 🌟 Use Cases

- Production FreeSWITCH deployments
- Complex call routing scenarios
- Multi-tenant PBX systems
- Advanced development and testing
- Performance-critical applications
- Enterprise telephony solutions

**Perfect for:** Production deployments requiring full feature set and extensive tooling.
