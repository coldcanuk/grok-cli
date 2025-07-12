"""
Request Management for Grok CLI
Handles batching, caching, and rate limiting
"""

import asyncio
import time
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import hashlib

import os

class RequestPriority(Enum):
    HIGH = 1      # User-initiated requests
    MEDIUM = 2    # Tool calls
    LOW = 3       # Background operations

@dataclass
class BatchedRequest:
    operation: str
    params: Dict[str, Any]
    priority: RequestPriority
    timestamp: float
    cache_key: Optional[str] = None

class RequestManager:
    def __init__(self, min_delay_seconds: float = 0.5):
        self.min_delay_seconds = min_delay_seconds
        self.last_request_time = 0.0
        self.request_queue = []
        self.cache = {}
        self.batch_size = 5
        self.batch_timeout = 2.0  # seconds
        
    def _generate_cache_key(self, operation: str, params: Dict[str, Any]) -> str:
        """Generate a cache key for the request"""
        cache_data = f"{operation}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _is_cacheable(self, operation: str) -> bool:
        """Check if an operation can be cached"""
        cacheable_ops = {"read_file", "list_files", "list_files_recursive"}
        return operation in cacheable_ops
    
    def add_request(self, operation: str, params: Dict[str, Any], 
                   priority: RequestPriority = RequestPriority.MEDIUM) -> str:
        """Add a request to the queue"""
        cache_key = None
        if self._is_cacheable(operation):
            cache_key = self._generate_cache_key(operation, params)
            if cache_key in self.cache:
                # Return cached result immediately
                return self.cache[cache_key]
        
        request = BatchedRequest(
            operation=operation,
            params=params,
            priority=priority,
            timestamp=time.time(),
            cache_key=cache_key
        )
        
        self.request_queue.append(request)
        return None  # Will be processed in batch
    
    def _can_batch_together(self, requests: List[BatchedRequest]) -> bool:
        """Check if requests can be batched together"""
        if len(requests) <= 1:
            return True
        
        # Group similar operations
        operations = set(req.operation for req in requests)
        
        # File operations can be batched
        file_ops = {"read_file", "list_files", "create_file"}
        if operations.issubset(file_ops):
            return True
        
        # Search operations should be separate
        if "brave_search" in operations:
            return len(operations) == 1
        
        return False
    
    def _batch_file_operations(self, requests: List[BatchedRequest]) -> Dict[str, Any]:
        """Batch multiple file operations into a single efficient operation"""
        results = {}
        
        # Group by operation type
        reads = [r for r in requests if r.operation == "read_file"]
        lists = [r for r in requests if r.operation in ["list_files", "list_files_recursive"]]
        creates = [r for r in requests if r.operation == "create_file"]
        
        # Process reads efficiently
        for req in reads:
            filename = req.params["filename"]
            try:
                with open(filename, "r") as f:
                    content = f.read()
                result = {"success": True, "content": content}
                results[req.cache_key or f"read_{filename}"] = result
                
                # Cache the result
                if req.cache_key:
                    self.cache[req.cache_key] = result
            except Exception as e:
                results[req.cache_key or f"read_{filename}"] = {"error": str(e)}
        
        # Process list operations
        for req in lists:
            directory = req.params.get("directory", ".")
            recursive = req.operation == "list_files_recursive"
            try:
                if recursive:
                    files = []
                    for root, dirs, filenames in os.walk(directory):
                        for filename in filenames:
                            files.append(os.path.relpath(os.path.join(root, filename), directory))
                else:
                    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
                result = {"success": True, "files": files}
                results[req.cache_key or f"list_{directory}"] = result
                
                if req.cache_key:
                    self.cache[req.cache_key] = result
            except Exception as e:
                results[req.cache_key or f"list_{directory}"] = {"error": str(e)}
        
        # Process create operations
        for req in creates:
            filename = req.params["filename"]
            content = req.params.get("content", "")
            try:
                with open(filename, "w") as f:
                    f.write(content)
                result = {"success": True, "message": f"File '{filename}' created"}
                results[req.cache_key or f"create_{filename}"] = result
                
                if req.cache_key:
                    self.cache[req.cache_key] = result
            except Exception as e:
                results[req.cache_key or f"create_{filename}"] = {"error": str(e)}
        
        return results
    
    def _should_delay_request(self) -> float:
        """Calculate how long to wait before next request"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_delay_seconds:
            return self.min_delay_seconds - elapsed
        return 0.0
    
    async def process_queue(self) -> Dict[str, Any]:
        """Process queued requests in batches"""
        if not self.request_queue:
            return {}
        
        # Wait for minimum delay
        delay = self._should_delay_request()
        if delay > 0:
            await asyncio.sleep(delay)
        
        # Sort by priority and timestamp
        self.request_queue.sort(key=lambda x: (x.priority.value, x.timestamp))
        
        # Take a batch
        batch = self.request_queue[:self.batch_size]
        self.request_queue = self.request_queue[self.batch_size:]
        
        # Process the batch
        if self._can_batch_together(batch):
            results = self._batch_file_operations(batch)
        else:
            # Process individually with delays
            results = {}
            for req in batch:
                # Add small delays between individual requests
                if req != batch[0]:
                    await asyncio.sleep(0.1)
                
                # Simple individual processing - delegate to appropriate handler
                result = {"error": "Individual tool execution not implemented in RequestManager"}
                results[req.cache_key or f"{req.operation}_{req.timestamp}"] = result
                
                if req.cache_key and "success" in result:
                    self.cache[req.cache_key] = result
        
        self.last_request_time = time.time()
        return results
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        return {
            "queue_length": len(self.request_queue),
            "cache_size": len(self.cache),
            "last_request_time": self.last_request_time,
            "priorities": {
                "high": len([r for r in self.request_queue if r.priority == RequestPriority.HIGH]),
                "medium": len([r for r in self.request_queue if r.priority == RequestPriority.MEDIUM]),
                "low": len([r for r in self.request_queue if r.priority == RequestPriority.LOW])
            }
        }
    
    def clear_cache(self):
        """Clear the request cache"""
        self.cache.clear()
