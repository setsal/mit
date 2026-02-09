# Authentication Errors Guide

## 401 Unauthorized

### Description
The request lacks valid authentication credentials or the provided credentials are invalid.

### Common Causes

1. **Missing Token**: No Authorization header provided
2. **Invalid Token**: Token is malformed or tampered
3. **Expired Token**: Token has passed its expiration time
4. **Wrong Token Type**: Using refresh token instead of access token

### Troubleshooting Steps

#### Step 1: Verify Header Format
Ensure Authorization header is present:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

#### Step 2: Check Token Expiration
Decode the JWT and verify `exp` claim:
```python
import jwt
decoded = jwt.decode(token, options={"verify_signature": False})
print(decoded["exp"])  # Unix timestamp
```

#### Step 3: Refresh Token
If expired, use refresh token to obtain new access token.

**Note**: For token format details, consult the OAuth agent.

---

## 403 Forbidden

### Description
The server understood the request but refuses to authorize it. This is different from 401 - the client is authenticated but lacks permission.

### Common Causes

1. **Insufficient Scope**: Token doesn't have required scope
2. **Resource Restrictions**: User doesn't have access to resource
3. **IP Restrictions**: Request from unauthorized IP

### Troubleshooting Steps

#### Step 1: Check Token Scopes
Verify the token includes required scopes:
```json
{
  "scope": "read write network:connect"
}
```

#### Step 2: Verify Resource Permissions
Ensure user has access to the requested resource.

#### Step 3: Request Additional Scopes
Re-authenticate with additional scopes in the authorization request.

**Note**: For scope definitions, consult the OAuth agent.

---

## Token Expiration Handling

### Best Practices

1. **Proactive Refresh**: Refresh tokens before expiration
2. **Grace Period**: Allow 5-minute buffer before expiration
3. **Retry Logic**: On 401, attempt token refresh and retry

### Token Refresh Flow
```
1. Detect 401 Unauthorized
2. Use refresh token to get new access token
3. Retry original request with new token
4. If refresh fails, re-authenticate user
```
