# Microsoft Teams Integration (Mockup)

## Overview
This is a **mockup implementation** of Microsoft Teams integration. It simulates the OAuth flow and provides sample data without actually connecting to Microsoft Teams API.

## Features

### ✅ Implemented (Mockup)
- OAuth2 authorization flow (simulated)
- Sample teams data with:
  - 3 teams (Computer Science 101, Data Science Workshop, Web Development Team)
  - Multiple channels per team
  - Assignments with due dates
  - Team members and roles
  - Messages in channels
- Connection status tracking
- Disconnect functionality

### 🎯 API Endpoints

#### 1. **Authorization**
```
GET /microsoft_teams/authorize
```
Initiates the mock OAuth flow. Redirects to callback automatically.

#### 2. **OAuth Callback**
```
GET /microsoft_teams/oauth2callback
```
Handles the OAuth callback (mocked). Stores connection status in session.

#### 3. **Fetch Teams**
```
GET /microsoft_teams/fetch_teams
```
Returns all connected teams data (mock).

**Response:**
```json
{
  "success": true,
  "teams": [...],
  "count": 3
}
```

#### 4. **Get Team Details**
```
GET /microsoft_teams/team/<team_id>
```
Returns detailed information about a specific team.

#### 5. **Connection Status**
```
GET /microsoft_teams/status
```
Returns current connection status.

**Response:**
```json
{
  "connected": true,
  "teams_count": 3,
  "is_mock": true
}
```

#### 6. **Disconnect**
```
POST /microsoft_teams/disconnect
```
Disconnects Microsoft Teams and clears session data.

## Mock Data Structure

### Teams
```python
{
  'id': 'team-001',
  'displayName': 'Computer Science 101',
  'description': 'Introduction to Programming',
  'createdDateTime': '2024-09-01T08:00:00Z',
  'channels': [...],
  'assignments': [...],
  'members': [...]
}
```

### Channels
```python
{
  'id': 'channel-001',
  'displayName': 'General',
  'description': 'General discussion',
  'messages': [...]
}
```

### Assignments
```python
{
  'id': 'assign-001',
  'displayName': 'Introduction to Python',
  'instructions': 'Complete the Python basics tutorial...',
  'dueDateTime': '2024-09-15T23:59:00Z',
  'status': 'assigned',
  'points': 100
}
```

### Members
```python
{
  'displayName': 'Prof. Smith',
  'email': 'smith@university.edu',
  'role': 'owner'
}
```

## Usage

1. **Connect to Microsoft Teams**
   - Navigate to Class or Dev page
   - Click "Connect Microsoft Teams" button
   - System will simulate OAuth flow and redirect back
   - Mock data will be displayed

2. **View Connected Teams**
   - After connection, teams will appear in the Class page
   - Shows team name, description, channel count, assignments, and members

3. **Disconnect**
   - Click "Disconnect" button to remove the connection
   - All mock data will be cleared from session

## Session Storage

The mockup stores data in Flask session:
- `microsoft_teams_connected`: Boolean flag
- `microsoft_teams_access_token`: Mock access token
- `microsoft_teams_data`: Full mock teams data

## Converting to Real Implementation

To convert this to a real Microsoft Teams integration:

1. **Register Application in Azure AD**
   - Go to https://portal.azure.com
   - Register a new application
   - Get Client ID and Client Secret
   - Configure redirect URIs

2. **Update Environment Variables**
   ```bash
   export MS_CLIENT_ID='your-client-id'
   export MS_CLIENT_SECRET='your-client-secret'
   export MS_TENANT_ID='your-tenant-id'
   ```

3. **Replace Mock OAuth with Real OAuth**
   - Use `msal` library for Microsoft authentication
   - Implement real token exchange
   - Store tokens in database

4. **Implement Real API Calls**
   - Use Microsoft Graph API
   - Endpoints:
     - `/v1.0/me/joinedTeams` - Get teams
     - `/v1.0/teams/{id}/channels` - Get channels
     - `/v1.0/education/classes/{id}/assignments` - Get assignments

5. **Required Scopes**
   ```
   Team.ReadBasic.All
   Channel.ReadBasic.All
   ChannelMessage.Read.All
   EduAssignments.Read
   User.Read
   ```

## UI Integration

The mockup integrates seamlessly with the existing UI:
- Shows connection card in Class page
- Displays connected teams with statistics
- Uses consistent styling with Google Classroom integration
- Responsive design for mobile and desktop

## Notes

- ⚠️ This is a **mockup** - no real Microsoft Teams connection
- 📝 Data resets when session expires
- 🎨 UI is production-ready
- 🔄 Easy to convert to real implementation

