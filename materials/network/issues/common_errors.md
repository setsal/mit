# Network Library - Common Issues and Troubleshooting

## Error 504: Gateway Timeout

### Description
The 504 Gateway Timeout error occurs when the network library cannot establish a connection within the specified timeout period.

### Common Causes
1. **Insufficient timeout value**: The default timeout of 30 seconds may not be enough for high-latency networks
2. **Network congestion**: Heavy traffic between client and server
3. **Firewall blocking**: Outbound connections may be blocked
4. **DNS resolution delays**: Slow DNS lookup

### Solutions

#### Solution 1: Increase Timeout
Increase the `timeout` parameter in your `/api/v1/connect` call:
```json
{
  "host": "example.com",
  "timeout": 60,
  "retry_count": 5
}
```

#### Solution 2: Check Network Configuration
Verify your firewall allows outbound connections on the target port.

#### Solution 3: Use Retry Logic
Set `retry_count` to a higher value (recommended: 3-5) to handle transient failures.

**Note**: If you need details about the timeout parameter configuration, consult the API_Ref agent.

---

## Error 401: Unauthorized

### Description
The 401 Unauthorized error indicates invalid or missing authentication credentials.

### Common Causes
1. **Missing Authorization header**: Token not provided
2. **Expired token**: Access token has expired
3. **Invalid token format**: Token is malformed

### Solutions

#### Solution 1: Verify Authorization Header
Ensure you include the `Authorization` header with format:
```
Authorization: Bearer <your-token>
```

#### Solution 2: Refresh Expired Token
If token is expired, obtain a new token from the authentication service.

#### Solution 3: Check Token Format
Ensure the token is a valid JWT or opaque token format.

**Note**: For token format specifications, consult the API_Ref agent.

---

## Connection Refused

### Description
The connection is actively refused by the target server.

### Common Causes
1. Service is not running
2. Wrong port number
3. IP address restrictions

### Solutions
1. Verify the service is running on the target host
2. Check the port number in your configuration
3. Ensure your IP is whitelisted
