# FreeSWITCH XML Handler - Full Stack Application

A comprehensive CRUD interface for managing FreeSWITCH directory tables with FastAPI backend and React frontend.

## Features

### Backend (FastAPI)
- ✅ Complete CRUD operations for all FreeSWITCH tables
- ✅ PostgreSQL database integration
- ✅ Pydantic models with validation
- ✅ RESTful API endpoints
- ✅ Auto-generated OpenAPI documentation

### Frontend (React + Ant Design)
- ✅ Modern React components with TypeScript
- ✅ Ant Design UI components
- ✅ Data tables with sorting, filtering, and pagination
- ✅ Modal forms for create/edit operations
- ✅ Navigation menu with FreeSWITCH management sections

### Database Tables
- **v_domains** - FreeSWITCH domains
- **v_extensions** - SIP extensions with all configuration options
- **v_contacts** - Contact information
- **v_users** - User accounts
- **v_extension_users** - Extension to user mappings
- **v_extension_settings** - Per-extension parameters and variables
- **v_voicemails** - Voicemail configurations
- **v_dialplans** - Dialplan entries
- **v_default_settings** - System default settings
- **registrations** - Current registrations (read-only)

## Setup Instructions

### Prerequisites
- Node.js (v16 or later)
- Python 3.8+
- PostgreSQL 12+

### Database Setup

1. Create a PostgreSQL database:
```sql
CREATE DATABASE freeswitch_db;
```

2. Run the database setup script:
```bash
psql -U postgres -d freeswitch_db -f database_setup.sql
```

This will create all tables and insert sample test data.

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Configure database connection in `app/database.py`:
```python
DATABASE_URL = "postgresql://username:password@localhost:5432/freeswitch_db"
```

4. Start the FastAPI server:
```bash
python run.py
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- FreeSWITCH endpoints: `http://localhost:8000/api/freeswitch/*`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure API base URL in `.env`:
```
VITE_API_BASE_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

### Access the Management Interface

1. Open `http://localhost:5173` in your browser
2. Login with your credentials
3. Navigate to FreeSWITCH section in the sidebar

### Available Management Pages

#### Domains Management
- View all domains
- Create new domains
- Edit domain settings
- Enable/disable domains

#### Extensions Management
- Comprehensive extension configuration
- SIP settings and passwords
- Caller ID configuration
- Directory information
- Call forwarding settings
- Advanced SIP parameters

#### Voicemails Management
- Voicemail box configuration
- Email settings
- Password management
- Enable/disable voicemail boxes

### API Endpoints

All endpoints support standard CRUD operations:

```
GET    /api/freeswitch/domains          # List all domains
POST   /api/freeswitch/domains          # Create domain
GET    /api/freeswitch/domains/{id}     # Get domain by ID
PUT    /api/freeswitch/domains/{id}     # Update domain
DELETE /api/freeswitch/domains/{id}     # Delete domain

GET    /api/freeswitch/extensions       # List all extensions
POST   /api/freeswitch/extensions       # Create extension
GET    /api/freeswitch/extensions/{id}  # Get extension by ID
PUT    /api/freeswitch/extensions/{id}  # Update extension
DELETE /api/freeswitch/extensions/{id}  # Delete extension

GET    /api/freeswitch/voicemails       # List all voicemails
POST   /api/freeswitch/voicemails       # Create voicemail
GET    /api/freeswitch/voicemails/{id}  # Get voicemail by ID
PUT    /api/freeswitch/voicemails/{id}  # Update voicemail
DELETE /api/freeswitch/voicemails/{id}  # Delete voicemail

# Similar patterns for contacts, users, extension-settings, dialplans
```

## Testing the System

### Sample Data
The database setup script includes sample data:
- 2 domains (`example.com`, `test.com`)
- 2 extensions (`1001`, `1002`)
- 2 contacts and users
- 2 voicemail boxes

### Test CRUD Operations

1. **Create a new domain:**
   - Go to Domains page
   - Click "Add Domain"
   - Enter domain name and enable it
   - Verify it appears in the table

2. **Create extensions:**
   - Go to Extensions page
   - Click "Add Extension"
   - Fill in extension details
   - Test various configuration options

3. **Test data relationships:**
   - Extensions are linked to domains
   - Voicemails reference domains
   - All foreign key relationships are enforced

### API Testing
Use the interactive API documentation at `http://localhost:8000/docs` to test endpoints directly.

## Development Notes

### Project Structure
```
├── backend/
│   ├── app/
│   │   ├── models/freeswitch_models.py    # Pydantic models
│   │   ├── routers/freeswitch_routes.py   # API endpoints
│   │   ├── database.py                    # DB connection
│   │   └── main.py                        # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/FreeSWITCH/         # React components
│   │   ├── services/freeswitchApi.ts      # API client
│   │   ├── types/freeswitch.ts           # TypeScript types
│   │   └── pages/                         # Page components
│   └── package.json
└── database_setup.sql                     # Database schema
```

### Key Features Implemented
- ✅ Complete CRUD operations for all tables
- ✅ Form validation and error handling
- ✅ Responsive design with Ant Design
- ✅ TypeScript for type safety
- ✅ Database relationships and constraints
- ✅ Sample data for testing

### Integration with FreeSWITCH
This system provides the database layer that FreeSWITCH directory.lua and dialplan.lua scripts can query to generate XML responses. The table structure matches the expected FreeSWITCH schema requirements.

## Next Steps

1. **Extend functionality:**
   - Add extension settings management
   - Implement dialplan management UI
   - Add contact management interface

2. **Enhance UI:**
   - Add bulk operations
   - Implement advanced filtering
   - Add data export/import features

3. **Production deployment:**
   - Add authentication middleware
   - Implement proper logging
   - Add database migrations
   - Setup Docker containers

## Support

For issues or questions, refer to the API documentation or check the database schema in `database_setup.sql`.