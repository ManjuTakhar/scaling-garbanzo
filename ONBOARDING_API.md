# Onboarding API (Concise)

## What onboarding does
- Creates a new Tenant (organization)
- Creates a Workspace inside that tenant
- Adds the creator as WorkspaceMember with role "Owner"
- Optionally invites members by email:
  - Creates user records if they don’t exist
  - Adds them as WorkspaceMember with role "Member"
- Teams are not created during onboarding (they can be created later under the workspace)

## Endpoint
- POST `/api/onboarding`

Request body
```json
{
  "usage_type": "organization",  
  "workspace_name": "My Company Workspace",
  "team_members": [
    {"email": "john@example.com"},
    {"email": "jane@example.com"}
  ]
}
```

Response (summary)
```json
{
  "success": true,
  "tenant_id": "STR-...",
  "workspace_id": "WSP-...",
  "workspace_name": "My Company Workspace",
  "usage_type": "organization",
  "team_members_invited": 2,
  "message": "Your workspace has been created successfully!"
}
```

## Overall hierarchy
Tenant (Organization)
├── Workspaces (one or more)
│   ├── Workspace Members (Owner/Admin/Member)
│   ├── Teams (created later under a workspace)
│   ├── Projects
│   ├── Initiatives
│   └── Slack Channels
└── Users (belong to a tenant; join specific workspaces via Workspace Members)

## Data Models

### UsageType Enum
- `individual`: Personal projects, task management and productivity tracking for yourself
- `organization`: Team collaboration, project management, and organizational workflows

## Error Responses

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid data)
- `401`: Unauthorized (authentication required)
- `404`: Not Found (resource not found)
- `500`: Internal Server Error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```
