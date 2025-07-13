"""
Memory management system for GroKit chat history and session data lookup
"""

import os
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import glob


class MemoryManager:
    """Manages memory lookup functionality for chat history and session data."""
    
    def __init__(self, src_path: str):
        self.src_path = Path(src_path).resolve()
        self.grok_dir = self.src_path / ".grok"
        self.history_dir = self.grok_dir / "history"
        self.session_dir = self.grok_dir / "session"
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        self.grok_dir.mkdir(exist_ok=True)
        self.history_dir.mkdir(exist_ok=True)
        self.session_dir.mkdir(exist_ok=True)
    
    def search_memory(self, query: str, search_type: str = "recent_history", 
                     max_results: int = 5, time_range: Optional[str] = None) -> Dict[str, Any]:
        """
        Search through memory data based on query and parameters.
        
        Args:
            query: Search query string
            search_type: Type of search ("current_session", "recent_history", "all_history")
            max_results: Maximum number of results to return
            time_range: Optional time range filter
            
        Returns:
            Dictionary containing search results and metadata
        """
        try:
            results = []
            search_stats = {
                "query": query,
                "search_type": search_type,
                "files_searched": 0,
                "total_matches": 0,
                "time_range": time_range
            }
            
            if search_type == "current_session":
                results = self._search_current_session(query, max_results)
                search_stats["files_searched"] = 1
            elif search_type == "recent_history":
                results = self._search_recent_history(query, max_results, time_range)
            elif search_type == "all_history":
                results = self._search_all_history(query, max_results, time_range)
            else:
                return {"error": f"Invalid search_type: {search_type}"}
            
            search_stats["total_matches"] = len(results)
            
            return {
                "success": True,
                "results": results[:max_results],
                "stats": search_stats
            }
            
        except Exception as e:
            return {"error": f"Memory search failed: {str(e)}"}
    
    def _search_current_session(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search within the current session only."""
        results = []
        
        # Find the most recent session file
        session_files = list(self.session_dir.glob("session_*.json"))
        if not session_files:
            return results
        
        # Sort by modification time, get most recent
        latest_session = max(session_files, key=lambda f: f.stat().st_mtime)
        
        try:
            with open(latest_session, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Search through messages in current session
            for i, message in enumerate(session_data.get("messages", [])):
                if self._matches_query(message.get("content", ""), query):
                    results.append({
                        "type": "current_session",
                        "session_id": session_data.get("session_id", "unknown"),
                        "message_index": i,
                        "role": message.get("role", "unknown"),
                        "content": message.get("content", ""),
                        "timestamp": message.get("timestamp", ""),
                        "relevance_score": self._calculate_relevance(message.get("content", ""), query),
                        "source_file": str(latest_session)
                    })
                    
        except (json.JSONDecodeError, IOError) as e:
            pass  # Skip corrupted files
        
        # Sort by relevance score
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:max_results]
    
    def _search_recent_history(self, query: str, max_results: int, 
                              time_range: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search recent history files with optional time filtering."""
        results = []
        
        # Determine date range
        end_date = datetime.now()
        if time_range == "today":
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_range == "last_week":
            start_date = end_date - timedelta(days=7)
        elif time_range and re.match(r'\d{4}-\d{2}-\d{2}', time_range):
            try:
                start_date = datetime.strptime(time_range, "%Y-%m-%d")
                end_date = start_date + timedelta(days=1)
            except ValueError:
                start_date = end_date - timedelta(days=7)  # Default fallback
        else:
            start_date = end_date - timedelta(days=7)  # Default: last week
        
        # Search history files
        history_files = list(self.history_dir.glob("chat_*.json"))
        
        for history_file in history_files:
            try:
                # Check if file date is in range
                file_date_str = history_file.stem.replace("chat_", "")
                try:
                    file_date = datetime.strptime(file_date_str, "%Y-%m-%d")
                    if not (start_date <= file_date <= end_date):
                        continue
                except ValueError:
                    continue  # Skip files with invalid date format
                
                with open(history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                
                # Search through chat entries
                for entry in history_data:
                    if self._matches_query(entry.get("content", ""), query):
                        results.append({
                            "type": "history",
                            "session_id": entry.get("session_id", "unknown"),
                            "role": entry.get("role", "unknown"),
                            "content": entry.get("content", ""),
                            "timestamp": entry.get("timestamp", ""),
                            "relevance_score": self._calculate_relevance(entry.get("content", ""), query),
                            "source_file": str(history_file),
                            "date": file_date_str
                        })
                        
            except (json.JSONDecodeError, IOError):
                continue  # Skip corrupted files
        
        # Sort by relevance and timestamp
        results.sort(key=lambda x: (x["relevance_score"], x["timestamp"]), reverse=True)
        return results[:max_results]
    
    def _search_all_history(self, query: str, max_results: int, 
                           time_range: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search through all available history and session data."""
        results = []
        
        # Search session files
        session_files = list(self.session_dir.glob("session_*.json"))
        for session_file in session_files:
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                # Apply time filtering if specified
                if time_range and not self._file_in_time_range(session_file, time_range):
                    continue
                
                for i, message in enumerate(session_data.get("messages", [])):
                    if self._matches_query(message.get("content", ""), query):
                        results.append({
                            "type": "session",
                            "session_id": session_data.get("session_id", "unknown"),
                            "message_index": i,
                            "role": message.get("role", "unknown"),
                            "content": message.get("content", ""),
                            "timestamp": message.get("timestamp", ""),
                            "relevance_score": self._calculate_relevance(message.get("content", ""), query),
                            "source_file": str(session_file)
                        })
                        
            except (json.JSONDecodeError, IOError):
                continue
        
        # Search history files (reuse recent history logic)
        history_results = self._search_recent_history(query, max_results * 2, time_range)
        results.extend(history_results)
        
        # Remove duplicates and sort
        unique_results = []
        seen_content = set()
        
        for result in results:
            content_key = (result["content"][:100], result.get("timestamp", ""))
            if content_key not in seen_content:
                seen_content.add(content_key)
                unique_results.append(result)
        
        unique_results.sort(key=lambda x: (x["relevance_score"], x["timestamp"]), reverse=True)
        return unique_results[:max_results]
    
    def _matches_query(self, content: str, query: str) -> bool:
        """Check if content matches the search query."""
        if not content or not query:
            return False
        
        content_lower = content.lower()
        query_lower = query.lower()
        
        # Simple keyword matching - could be enhanced with fuzzy matching
        query_words = query_lower.split()
        
        # All words must be present
        return all(word in content_lower for word in query_words)
    
    def _calculate_relevance(self, content: str, query: str) -> float:
        """Calculate relevance score for content vs query."""
        if not content or not query:
            return 0.0
        
        content_lower = content.lower()
        query_lower = query.lower()
        query_words = query_lower.split()
        
        # Count word matches
        matches = sum(1 for word in query_words if word in content_lower)
        
        # Calculate percentage of query words found
        base_score = matches / len(query_words) if query_words else 0
        
        # Boost score for exact phrase matches
        if query_lower in content_lower:
            base_score += 0.5
        
        # Boost score for proximity (words close together)
        if len(query_words) > 1:
            for i in range(len(query_words) - 1):
                word1, word2 = query_words[i], query_words[i + 1]
                if word1 in content_lower and word2 in content_lower:
                    pos1 = content_lower.find(word1)
                    pos2 = content_lower.find(word2, pos1)
                    if 0 < pos2 - pos1 < 50:  # Words within 50 characters
                        base_score += 0.2
        
        return min(base_score, 1.0)  # Cap at 1.0
    
    def _file_in_time_range(self, file_path: Path, time_range: str) -> bool:
        """Check if file falls within specified time range."""
        if not time_range:
            return True
        
        try:
            file_stat = file_path.stat()
            file_time = datetime.fromtimestamp(file_stat.st_mtime)
            
            now = datetime.now()
            
            if time_range == "today":
                start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
                return file_time >= start_time
            elif time_range == "last_week":
                start_time = now - timedelta(days=7)
                return file_time >= start_time
            elif re.match(r'\d{4}-\d{2}-\d{2}', time_range):
                target_date = datetime.strptime(time_range, "%Y-%m-%d")
                return (target_date <= file_time < target_date + timedelta(days=1))
            
        except (OSError, ValueError):
            pass
        
        return True  # Default to include if can't determine
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about available memory data."""
        stats = {
            "session_files": 0,
            "history_files": 0,
            "total_sessions": 0,
            "total_messages": 0,
            "date_range": None,
            "storage_path": str(self.grok_dir)
        }
        
        try:
            # Count session files
            session_files = list(self.session_dir.glob("session_*.json"))
            stats["session_files"] = len(session_files)
            
            # Count history files  
            history_files = list(self.history_dir.glob("chat_*.json"))
            stats["history_files"] = len(history_files)
            
            # Count total messages and sessions
            total_messages = 0
            session_ids = set()
            
            for session_file in session_files:
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    session_ids.add(session_data.get("session_id", "unknown"))
                    total_messages += len(session_data.get("messages", []))
                except (json.JSONDecodeError, IOError):
                    continue
            
            stats["total_sessions"] = len(session_ids)
            stats["total_messages"] = total_messages
            
            # Determine date range
            if session_files:
                file_times = []
                for f in session_files:
                    try:
                        file_times.append(datetime.fromtimestamp(f.stat().st_mtime))
                    except OSError:
                        continue
                
                if file_times:
                    earliest = min(file_times)
                    latest = max(file_times)
                    stats["date_range"] = {
                        "earliest": earliest.isoformat(),
                        "latest": latest.isoformat()
                    }
            
        except Exception as e:
            stats["error"] = str(e)
        
        return stats