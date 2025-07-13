# Streaming Implementation Guide

## Overview
This document outlines the proper streaming implementation in GroKit to ensure real-time AI responses without UI refresh bugs.

## Critical Fixes Applied

### **Issue 1: SDK Bypassing Streaming** ✅ FIXED
**Problem**: When XAI SDK was available, streaming requests were routed to `_api_call_sdk()` which only supports non-streaming responses via `chat.sample()`.

**Solution**: Modified API routing in `engine.py:871-876`:
```python
if XAI_SDK_AVAILABLE and not stream:
    # Use SDK for non-streaming requests (more reliable)
    return self._api_call_sdk(messages, model, stream, tools, reasoning, retry_count, fun_messages)
else:
    # Use requests for streaming or when SDK unavailable
    return self._api_call_requests(key, messages, model, stream, tools, reasoning, retry_count, fun_messages)
```

### **Issue 2: Excessive Window Refreshing** ✅ FIXED
**Problem**: Every streaming chunk called `render_ai_window()` which redraws the entire window, causing flickering and clearing.

**Old problematic code** in `grokit.py`:
```python
# Re-render only the AI window  ❌ BAD
self.renderer.render_ai_window()
sys.stdout.flush()
```

**Solution**: Added efficient streaming update method in `grid_ui.py:464-515`:
```python
def update_message_content_streaming(self, message_index: int, new_content: str):
    """Update message content for streaming without full window refresh."""
    if 0 <= message_index < len(self.ai_content):
        # Update content
        self.ai_content[message_index]['content'] = new_content
        # Use efficient in-place update instead of full window refresh
        self._update_message_in_place(message_index)
```

**Updated streaming handler** in `grokit.py:891-894`:
```python
# Use new streaming update method to avoid full window refresh  ✅ GOOD
self.renderer.update_message_content_streaming(assistant_msg_index, streaming_content)
```

## Correct Streaming Flow

### **1. API Request Path**
```
User Input → GroKit → Engine.api_call()
                          ↓
                   stream=True?
                          ↓
                     YES → _api_call_requests() → Streaming Response
                          ↓
                     NO  → _api_call_sdk() → Complete Response
```

### **2. Streaming Response Handling**
```
Streaming Chunks → _handle_streaming_response()
                          ↓
              Parse JSON chunks for content deltas
                          ↓
           Update message via update_message_content_streaming()
                          ↓
              Minimal in-place UI update (no full refresh)
                          ↓
                Show streaming indicator only
```

### **3. UI Update Strategy**
- ✅ **GOOD**: `update_message_content_streaming()` - Updates content in-place
- ✅ **GOOD**: `_update_message_in_place()` - Shows minimal streaming indicator
- ❌ **BAD**: `render_ai_window()` - Redraws entire window, causes clearing
- ❌ **BAD**: `render_full_screen()` - Redraws everything, very expensive

## Testing and Validation

### **Streaming Configuration Test**
```python
# Verify API routing
engine.api_call("key", messages, "grok-4-0709", stream=False)  # → SDK
engine.api_call("key", messages, "grok-4-0709", stream=True)   # → Requests
```

### **UI Performance Test**
```python
# Test streaming updates don't cause full refreshes
renderer.update_message_content_streaming(0, "streaming content")
# Should NOT call render_ai_window() internally
```

### **Integration Test**
```python
# Mock streaming flow
chunks = ["Hello", " there", "!"]
for chunk in chunks:
    content += chunk
    renderer.update_message_content_streaming(msg_index, content)
# Result: Smooth incremental updates
```

## Prevention Guidelines

### **DO NOT** ❌
1. Call `render_ai_window()` during streaming
2. Call `render_full_screen()` during streaming  
3. Route streaming requests through SDK methods
4. Clear the window/terminal during streaming
5. Use `print()` statements that could interfere with positioning

### **DO** ✅
1. Use `update_message_content_streaming()` for streaming updates
2. Route streaming through `_api_call_requests()`
3. Use minimal cursor positioning for streaming indicators
4. Test with real streaming responses
5. Verify no window flicker during streaming

## Common Pitfalls

### **Pitfall 1: SDK Auto-Selection**
The engine might prefer SDK over requests. Always check the routing logic when stream=True.

### **Pitfall 2: Terminal Control Sequences**
Drawing boxes and borders can interfere with streaming. Use minimal updates only.

### **Pitfall 3: Full Redraws**
Any method that clears/redraws large areas will disrupt streaming. Keep updates targeted.

### **Pitfall 4: Cursor Position Loss**
Streaming updates can lose cursor position. Use absolute positioning when needed.

## Performance Characteristics

### **Before Fix**
- **Latency**: High (wait for complete response)
- **UI**: Flickering, clearing, poor UX
- **Responsiveness**: Blocked until completion

### **After Fix**  
- **Latency**: Real-time streaming
- **UI**: Smooth, incremental updates
- **Responsiveness**: Live feedback as AI types

## File Locations

### **Key Files Modified**
- `grok_cli/engine.py` - API routing fix (line 871-876)
- `grok_cli/grid_ui.py` - Streaming update methods (line 464-515)
- `grok_cli/grokit.py` - Streaming handler update (line 891-894)

### **Test Files**
- `test_streaming_fix.py` - Comprehensive streaming tests
- `test_clear_command.py` - Clear command functionality tests

## Version History
- **v1.0**: Original implementation with window refresh bug
- **v1.1**: Fixed SDK routing for streaming
- **v1.2**: Added efficient streaming UI updates
- **v1.3**: Comprehensive testing and validation

---

**⚠️ CRITICAL**: Always test streaming with real API calls to ensure smooth UX. The streaming experience is core to user satisfaction with GroKit.