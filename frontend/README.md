# XML Handler Frontend

A modern React-based frontend for managing call queues and agents in a telephony system.

## Features

### 🏠 Dashboard
- **System Overview**: Real-time statistics of queues, agents, and calls
- **Queue Status Cards**: Visual representation of each queue's current state
- **System Control**: Start/stop XML Handler system
- **Quick Actions**: Navigate to queue and agent management

### 📞 Queue Management
- **Queue CRUD Operations**: Create, read, update, and delete queues
- **Queue Configuration**: 
  - Queue name and extension
  - Call routing strategy (Ring All, Least Recent, Fewest Calls, etc.)
  - Max wait time and abandoned call settings
  - Context and descriptions
- **Agent Assignment**: Assign and remove agents from queues
- **Search and Filter**: Find queues by name, extension, or strategy

### 👥 Agent Management
- **Agent CRUD Operations**: Full agent lifecycle management
- **Agent Information**:
  - Agent ID and name
  - Contact information (phone/extension)
  - Status management (Available, Busy, Break, Unavailable)
  - Enable/disable functionality
- **Real-time Status Updates**: Change agent status on the fly
- **Search and Filter**: Find agents by name, status, or enabled state

### 🎛️ XML Handler (Real-time Operations)
- **Live Queue Monitoring**: Real-time view of queue status
- **Caller Management**:
  - Add callers to queue manually
  - Remove callers from queue
  - View waiting caller statistics
- **Call Assignment**: Manually assign calls to specific agents
- **Agent State Monitoring**: View real-time agent states and statuses

## Technology Stack

### Frontend Framework
- **React 19.1.0** with TypeScript
- **Vite** for fast development and building
- **React Router DOM** for client-side routing

### UI Library
- **Ant Design 5.26.4** - Complete UI component library
- **Ant Design Icons** - Comprehensive icon set
- **Ant Design Charts** - Data visualization components

### State Management
- **Zustand 5.0.6** - Lightweight state management
- Separate stores for:
  - Authentication (`authStore`)
  - Queues (`queueStore`) 
  - Agents (`agentStore`)
  - XML Handler (`queueManagerStore`)

### HTTP Client
- **Axios 1.10.0** with interceptors for:
  - Automatic authentication token handling
  - Request/response logging
  - Error handling with user-friendly messages
  - Loading state management

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn package manager

### Installation

1. **Navigate to frontend directory**
   ```bash
   cd queue-manager/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   The `.env` file is already configured with:
   ```
   VITE_API_BASE_URL=http://localhost:8000
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:5173`

## Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── Layout/          # Application layout components
│   ├── DataTable/       # Generic data table component
│   ├── QueueFormModal/  # Queue creation/editing modal
│   ├── AgentFormModal/  # Agent creation/editing modal
│   ├── StatsCard/       # Statistics display card
│   ├── QueueStatusCard/ # Queue status overview card
│   └── AgentCard/       # Agent information card
├── pages/               # Page components
│   ├── Dashboard.tsx    # Main dashboard
│   ├── Queues.tsx      # Queue management page
│   ├── Agents.tsx      # Agent management page
│   └── QueueManager.tsx # Real-time queue operations
├── store/               # Zustand stores
│   ├── authStore.ts     # Authentication state
│   ├── queueStore.ts    # Queue management state
│   ├── agentStore.ts    # Agent management state
│   └── queueManagerStore.ts # Real-time operations state
├── services/            # API and utility services
│   ├── api.ts          # Axios configuration and interceptors
│   └── messageService.ts # Global message handling
├── types/               # TypeScript type definitions
└── App.tsx             # Root application component
```

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm run lint` | Run ESLint |

## Features Overview

The frontend provides a complete interface for the queue management system with the following pages:

1. **Dashboard** - Overview of system status and quick actions
2. **Queues** - Manage call queues (create, edit, delete, assign agents)
3. **Agents** - Manage agents (create, edit, delete, status updates)
4. **XML Handler** - Real-time queue operations and monitoring

All components are built with TypeScript for type safety and use Zustand for state management with proper API integration.
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
