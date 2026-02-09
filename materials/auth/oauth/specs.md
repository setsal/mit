# OAuth 2.0 Specifications

## Supported Grant Types

### Authorization Code Grant
The most secure flow for server-side applications.

**Flow**:
1. User is redirected to authorization server
2. User authenticates and consents
3. Authorization code returned to redirect URI
4. Application exchanges code for tokens

**Required Parameters**:
- `response_type`: "code"
- `client_id`: Your application's client ID
- `redirect_uri`: Registered callback URL
- `scope`: Requested permissions
- `state`: CSRF protection token

### Client Credentials Grant
For server-to-server authentication without user context.

**Required Parameters**:
- `grant_type`: "client_credentials"
- `client_id`: Your application's client ID
- `client_secret`: Your application's secret

---

## Token Formats

### JWT (JSON Web Token)
Default format for access tokens.

**Structure**:
```
header.payload.signature
```

**Standard Claims**:
| Claim | Description |
|-------|-------------|
| `iss` | Token issuer |
| `sub` | Subject (user ID) |
| `aud` | Audience (intended recipient) |
| `exp` | Expiration timestamp |
| `iat` | Issued at timestamp |
| `scope` | Granted scopes |

### Token Lifetime
- **Access Token**: 1 hour
- **Refresh Token**: 30 days

---

## Scopes

### Available Scopes

| Scope | Description |
|-------|-------------|
| `read` | Read-only access |
| `write` | Write access |
| `admin` | Administrative access |
| `network:connect` | Connect to network services |
| `network:send` | Send data over connections |

### Scope Inheritance
- `admin` includes `read` and `write`
- `write` includes `read`
