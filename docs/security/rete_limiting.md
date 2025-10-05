# Rate Limiting Implementation - DoS Protection

## Overview

This document describes the rate limiting implementation for the Note Management System to mitigate Denial of Service (DoS) attacks as identified in the security threat assessment.

## Threat Mitigation

**Threat ID**: 7. Potential Excessive Resource Consumption for Note Manage(4.0) or D2 Note  
**Priority**: High  
**Category**: Denial Of Service  
**Status**: Mitigation Implemented

## Implementation Details

### Rate Limiting Strategy

The system implements a **dual-layer rate limiting approach**:

1. **User-based Rate Limiting**: Limits requests per authenticated user
2. **IP-based Rate Limiting**: Limits requests per IP address (fallback for anonymous users)

### Rate Limits Configuration

#### Default Limits (Normal Operations)
- **User Limit**: 10 requests per 5 seconds
- **IP Limit**: 20 requests per 5 seconds
- **Time Window**: 5 seconds (sliding window)

#### Strict Limits (Sensitive Operations)
- **User Limit**: 5 requests per 5 seconds
- **IP Limit**: 10 requests per 5 seconds
- **Time Window**: 5 seconds (sliding window)

### Protected Endpoints

#### Note Management Endpoints (Normal Rate Limiting)
- `POST /partial/note/add` - Create note
- `POST /partial/note/<id>/edit` - Update note
- `POST /partial/class/<lesson_id>/notes/add` - Create lesson note
- `POST /partial/class/<lesson_id>/notes/<section_id>/edit` - Update lesson note
- `PUT /api/notes/<id>` - Update note (API)
- `POST /api/notes` - Create note (API)

#### Sensitive Endpoints (Strict Rate Limiting)
- `POST /partial/note/<id>/delete` - Delete note
- `DELETE /api/notes/<id>` - Delete note (API)

#### Integration Endpoints (Moderate Rate Limiting)
- `POST /api/integration/sync-note-to-lesson/<note_id>/<lesson_id>`
- `POST /api/integration/sync-lesson-to-note/<lesson_id>/<section_id>`

### Technical Implementation

#### Algorithm
- **Sliding Window**: Uses a sliding window algorithm with deque data structure
- **Thread-Safe**: Implements thread-safe operations using RLock
- **Memory Efficient**: Automatic cleanup of old entries to prevent memory leaks

#### Components

1. **Rate Limiter Middleware** (`app/presentation/middleware/rate_limiter.py`)
   - Core rate limiting logic
   - Sliding window implementation
   - Thread-safe request tracking

2. **Decorators**
   - `@rate_limit(user_limit, ip_limit, window)` - Normal rate limiting
   - `@strict_rate_limit(user_limit, ip_limit, window)` - Strict rate limiting

3. **Background Cleanup** (`app/core/rate_limiter_cleanup.py`)
   - Automatic cleanup of old rate limiting data
   - Prevents memory leaks
   - Runs every hour by default

4. **Configuration** (`app/config/settings.py`)
   - Centralized rate limiting configuration
   - Environment-specific settings

### Response Format

When rate limit is exceeded, the system returns:

```json
{
    "success": false,
    "message": "Rate limit exceeded. Too many requests from your account.",
    "error_code": "RATE_LIMIT_EXCEEDED_USER",
    "retry_after": 5
}
```

**HTTP Status Code**: 429 (Too Many Requests)

### Rate Limit Headers

The system includes informative headers in responses:

- `X-RateLimit-Limit-User`: Maximum requests allowed per user
- `X-RateLimit-Remaining-User`: Remaining requests for user
- `X-RateLimit-Limit-IP`: Maximum requests allowed per IP
- `X-RateLimit-Remaining-IP`: Remaining requests for IP
- `X-RateLimit-Window`: Time window in seconds

### Client IP Detection

The system properly detects client IP addresses considering proxy/load balancer scenarios:

1. `X-Forwarded-For` header (first IP)
2. `X-Real-IP` header
3. `request.remote_addr` (fallback)

### Memory Management

#### Automatic Cleanup
- Background task runs every hour
- Removes entries older than 1 hour
- Prevents memory leaks in long-running applications

#### Storage Efficiency
- Uses deque for O(1) append/pop operations
- Removes expired entries during rate limit checks
- Thread-safe cleanup operations

## Testing

### Manual Testing
Use the provided test script:
```bash
python test_rate_limiting.py
```

### Test Scenarios
1. **Normal Rate Limiting**: 15 requests in quick succession
2. **Rate Limit Reset**: Wait for window expiration and retry
3. **Concurrent Requests**: Multiple simultaneous requests
4. **IP-based Limiting**: Requests from different IP addresses

### Expected Results
- First 10 requests should succeed (user limit)
- Subsequent requests should return 429 status
- After 5-second window, requests should succeed again
- Concurrent requests should be properly limited

## Monitoring and Logging

### Metrics to Monitor
- Rate limit hit frequency
- Top rate-limited IP addresses
- User accounts hitting limits frequently
- Memory usage of rate limiter

### Logging
Rate limit violations are logged with:
- Timestamp
- IP address
- User ID (if authenticated)
- Endpoint accessed
- Rate limit type (user/IP)

## Configuration

### Environment Variables
```bash
# Rate limiting settings
RATE_LIMIT_USER_DEFAULT=10
RATE_LIMIT_IP_DEFAULT=20
RATE_LIMIT_WINDOW=5
RATE_LIMIT_STRICT_USER=5
RATE_LIMIT_STRICT_IP=10
```

### Customization
Rate limits can be customized per endpoint by modifying the decorator parameters:

```python
@rate_limit(user_limit=15, ip_limit=30, window=10)
def custom_endpoint():
    pass
```

## Security Considerations

### Bypass Prevention
- Rate limiting is applied before business logic
- Cannot be bypassed through authentication
- IP-based limiting prevents anonymous abuse

### Attack Mitigation
- **Volumetric Attacks**: Limited by request count
- **Slowloris Attacks**: Time window prevents sustained attacks
- **Distributed Attacks**: IP-based limiting helps
- **Account-based Attacks**: User-based limiting prevents abuse

### Limitations
- **Distributed DoS**: May require additional infrastructure-level protection
- **IP Spoofing**: Limited protection against sophisticated IP spoofing
- **Legitimate Traffic**: May affect legitimate users during attacks

## Maintenance

### Regular Tasks
1. Monitor rate limit hit rates
2. Adjust limits based on usage patterns
3. Review and update IP whitelist if needed
4. Monitor memory usage of rate limiter

### Scaling Considerations
- Current implementation is in-memory (single instance)
- For multi-instance deployments, consider Redis-based rate limiting
- Monitor memory usage as user base grows

## Compliance

This implementation addresses:
- **OWASP Top 10**: A06:2021 – Vulnerable and Outdated Components
- **CWE-770**: Allocation of Resources Without Limits or Throttling
- **NIST Cybersecurity Framework**: PR.DS-5 (Protections against data leaks)

## Future Enhancements

1. **Redis Backend**: For distributed rate limiting
2. **Dynamic Limits**: Adjust limits based on system load
3. **Whitelist/Blacklist**: IP-based allow/deny lists
4. **Advanced Analytics**: Rate limiting metrics dashboard
5. **Adaptive Limits**: Machine learning-based limit adjustment
