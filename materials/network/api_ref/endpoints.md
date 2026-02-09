# Network Library API Reference

## GET /api/v1/connect

Establishes a connection to the network service.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `host` | string | Yes | Target host address |
| `port` | integer | No | Port number (default: 443) |
| `timeout` | integer | No | Connection timeout in seconds (default: 30) |
| `retry_count` | integer | No | Number of retry attempts (default: 3) |

### Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | Yes | Bearer token for authentication |
| `X-Request-ID` | No | Unique request identifier for tracing |

### Response

```json
{
  "connection_id": "conn-12345",
  "status": "connected",
  "latency_ms": 45
}
```

### Error Codes

- `401 Unauthorized`: Invalid or missing authorization token
- `504 Gateway Timeout`: Connection timeout, check `timeout` parameter

---

## POST /api/v1/send

Sends data over an established connection.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `connection_id` | string | Yes | Connection ID from /connect |
| `data` | object | Yes | Data payload to send |
| `priority` | string | No | Priority level: "high", "normal", "low" |

### Response

```json
{
  "message_id": "msg-67890",
  "status": "sent",
  "bytes_sent": 1024
}
```
