"""
Persistent storage system for GroKit chat history and session data
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import shutil


class PersistentStorage:
    """Manage persistent storage for chat history and session data."""
    
    def __init__(self, src_path: str):
        self.src_path = Path(src_path).resolve()
        self.grok_dir = self.src_path / ".grok"
        self.history_dir = self.grok_dir / "history"
        self.session_dir = self.grok_dir / "session"
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Current session tracking
        self.session_id = self._generate_session_id()
        self.session_file = self.session_dir / f"session_{self.session_id}.json"
        
        # Initialize session
        self._init_session()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        self.grok_dir.mkdir(exist_ok=True)
        self.history_dir.mkdir(exist_ok=True)
        self.session_dir.mkdir(exist_ok=True)
        
        # Create .gitignore for sensitive data
        gitignore_path = self.grok_dir / ".gitignore"
        if not gitignore_path.exists():
            with open(gitignore_path, 'w') as f:
                f.write("# GroKit persistent data\n")
                f.write("session/\n")
                f.write("history/\n")
                f.write("*.json\n")
                f.write("*.log\n")
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"grokit_{timestamp}"
    
    def _init_session(self):
        """Initialize current session data."""
        session_data = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "src_path": str(self.src_path),
            "messages": [],
            "cost_tracking": {
                "total_cost": 0.0,
                "total_tokens": 0,
                "operations": []
            },
            "metadata": {
                "version": "1.0.0",
                "ui_mode": "grid",
                "features_used": []
            }
        }
        
        self._save_session_data(session_data)
    
    def _save_session_data(self, data: Dict):
        """Save session data to file."""
        try:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save session data: {e}")
    
    def _load_session_data(self) -> Dict:
        """Load current session data."""
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load session data: {e}")
        
        # Return empty session if load fails
        return {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "src_path": str(self.src_path),
            "messages": [],
            "cost_tracking": {"total_cost": 0.0, "total_tokens": 0, "operations": []},
            "metadata": {"version": "1.0.0", "ui_mode": "grid", "features_used": []}
        }
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Add a message to the chat history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Add to session
        session_data = self._load_session_data()
        session_data["messages"].append(message)
        self._save_session_data(session_data)
        
        # Also save to daily history file
        self._save_to_daily_history(message)
    
    def _save_to_daily_history(self, message: Dict):
        """Save message to daily history file."""
        today = datetime.now().strftime("%Y-%m-%d")
        history_file = self.history_dir / f"chat_{today}.json"
        
        # Load existing history or create new
        history_data = []
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
            except Exception:
                history_data = []
        
        # Add message with session context
        history_entry = {
            "session_id": self.session_id,
            "src_path": str(self.src_path),
            **message
        }
        history_data.append(history_entry)
        
        # Save updated history
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save daily history: {e}")
    
    def get_session_messages(self) -> List[Dict]:
        """Get all messages from current session."""
        session_data = self._load_session_data()
        return session_data.get("messages", [])
    
    def get_chat_history(self) -> List[Dict]:
        """Get chat history formatted for API calls (role and content only)."""
        messages = self.get_session_messages()
        
        # Convert to API format (only role and content)
        api_messages = []
        for msg in messages:
            api_msg = {
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            }
            api_messages.append(api_msg)
        
        return api_messages
    
    def get_recent_history(self, days: int = 7, limit: int = 100) -> List[Dict]:
        """Get recent chat history across sessions."""
        messages = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Scan history files
        for history_file in self.history_dir.glob("chat_*.json"):
            try:
                # Extract date from filename
                date_str = history_file.stem.replace("chat_", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                if file_date >= cutoff_date:
                    with open(history_file, 'r', encoding='utf-8') as f:
                        file_messages = json.load(f)
                        messages.extend(file_messages)
            except Exception as e:
                print(f"Warning: Could not read history file {history_file}: {e}")
        
        # Sort by timestamp and limit
        messages.sort(key=lambda x: x.get("timestamp", ""))
        return messages[-limit:] if limit else messages
    
    def clear_session_history(self):
        """Clear all messages from the current session while preserving session metadata."""
        session_data = self._load_session_data()
        
        # Clear messages but keep session metadata
        session_data["messages"] = []
        
        # Reset cost tracking for this session
        session_data["cost_tracking"] = {
            "total_cost": 0.0,
            "total_tokens": 0,
            "operations": []
        }
        
        # Save the cleared session
        self._save_session_data(session_data)
    
    def update_cost_tracking(self, cost: float, tokens: int, operation: str):
        """Update cost tracking information."""
        session_data = self._load_session_data()
        
        # Update totals
        session_data["cost_tracking"]["total_cost"] += cost
        session_data["cost_tracking"]["total_tokens"] += tokens
        
        # Add operation record
        operation_record = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "cost": cost,
            "tokens": tokens
        }
        session_data["cost_tracking"]["operations"].append(operation_record)
        
        self._save_session_data(session_data)
    
    def get_cost_summary(self) -> Dict:
        """Get cost tracking summary for current session."""
        session_data = self._load_session_data()
        cost_data = session_data.get("cost_tracking", {})
        
        start_time = datetime.fromisoformat(session_data.get("start_time", datetime.now().isoformat()))
        duration = datetime.now() - start_time
        
        return {
            "total_cost": cost_data.get("total_cost", 0.0),
            "total_tokens": cost_data.get("total_tokens", 0),
            "operations_count": len(cost_data.get("operations", [])),
            "session_duration": str(duration).split('.')[0],  # Remove microseconds
            "start_time": session_data.get("start_time"),
            "session_id": self.session_id
        }
    
    def add_feature_usage(self, feature: str):
        """Track feature usage for analytics."""
        session_data = self._load_session_data()
        features = session_data["metadata"].get("features_used", [])
        
        feature_entry = {
            "feature": feature,
            "timestamp": datetime.now().isoformat()
        }
        features.append(feature_entry)
        
        session_data["metadata"]["features_used"] = features
        self._save_session_data(session_data)
    
    def cleanup_old_data(self, keep_days: int = 30):
        """Clean up old session and history data."""
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        cleaned_files = 0
        
        # Clean old session files
        for session_file in self.session_dir.glob("session_*.json"):
            try:
                # Extract date from filename
                filename = session_file.stem
                if "grokit_" in filename:
                    date_str = filename.split("grokit_")[1][:8]  # YYYYMMDD
                    file_date = datetime.strptime(date_str, "%Y%m%d")
                    
                    if file_date < cutoff_date:
                        session_file.unlink()
                        cleaned_files += 1
            except Exception:
                continue
        
        # Clean old history files
        for history_file in self.history_dir.glob("chat_*.json"):
            try:
                date_str = history_file.stem.replace("chat_", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                if file_date < cutoff_date:
                    history_file.unlink()
                    cleaned_files += 1
            except Exception:
                continue
        
        return cleaned_files
    
    def export_session(self, export_path: Optional[str] = None) -> str:
        """Export current session to a file."""
        if not export_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = f"grokit_session_export_{timestamp}.json"
        
        session_data = self._load_session_data()
        
        # Add export metadata
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "export_version": "1.0.0",
            "session_data": session_data
        }
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            return export_path
        except Exception as e:
            raise Exception(f"Failed to export session: {e}")
    
    def get_session_stats(self) -> Dict:
        """Get comprehensive session statistics."""
        session_data = self._load_session_data()
        messages = session_data.get("messages", [])
        
        # Message statistics
        user_messages = [m for m in messages if m["role"] == "user"]
        assistant_messages = [m for m in messages if m["role"] == "assistant"]
        
        # Character counts
        user_chars = sum(len(m["content"]) for m in user_messages)
        assistant_chars = sum(len(m["content"]) for m in assistant_messages)
        
        return {
            "session_id": self.session_id,
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "total_characters": user_chars + assistant_chars,
            "user_characters": user_chars,
            "assistant_characters": assistant_chars,
            "features_used": len(session_data["metadata"].get("features_used", [])),
            "cost_summary": self.get_cost_summary()
        }
    
    @classmethod
    def get_available_sessions(cls, src_path: str) -> List[Dict]:
        """Get list of available previous sessions."""
        src_path = Path(src_path).resolve()
        session_dir = src_path / ".grok" / "session"
        
        if not session_dir.exists():
            return []
        
        sessions = []
        for session_file in session_dir.glob("session_*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                # Extract session info
                session_info = {
                    "file_path": str(session_file),
                    "session_id": session_data.get("session_id", "unknown"),
                    "start_time": session_data.get("start_time", ""),
                    "messages": session_data.get("messages", []),
                    "cost_tracking": session_data.get("cost_tracking", {}),
                    "metadata": session_data.get("metadata", {})
                }
                
                # Add computed fields
                messages = session_info["messages"]
                if messages:
                    session_info["message_count"] = len(messages)
                    session_info["last_message_time"] = messages[-1].get("timestamp", "")
                    
                    # Extract first user message as preview
                    user_messages = [m for m in messages if m.get("role") == "user"]
                    if user_messages:
                        first_msg = user_messages[0].get("content", "")
                        session_info["preview"] = first_msg[:100] + "..." if len(first_msg) > 100 else first_msg
                    else:
                        session_info["preview"] = "No user messages"
                else:
                    session_info["message_count"] = 0
                    session_info["last_message_time"] = ""
                    session_info["preview"] = "Empty session"
                
                # Add cost info
                cost_data = session_info["cost_tracking"]
                session_info["total_cost"] = cost_data.get("total_cost", 0.0)
                session_info["total_tokens"] = cost_data.get("total_tokens", 0)
                
                sessions.append(session_info)
                
            except Exception as e:
                # Skip corrupted session files
                print(f"Warning: Could not read session file {session_file}: {e}")
                continue
        
        # Sort by start time (newest first)
        sessions.sort(key=lambda x: x.get("start_time", ""), reverse=True)
        return sessions
    
    @classmethod
    def load_session_data(cls, session_file_path: str) -> Dict:
        """Load a specific session's data."""
        try:
            with open(session_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Could not load session from {session_file_path}: {e}")


class ClipboardHandler:
    """Handle clipboard operations for input enhancement."""
    
    @staticmethod
    def get_clipboard_text() -> Optional[str]:
        """Get text from system clipboard."""
        try:
            if os.name == 'nt':  # Windows
                import subprocess
                result = subprocess.run(['powershell', 'Get-Clipboard'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip()
            else:  # Linux/WSL
                try:
                    import subprocess
                    # Try xclip first
                    result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        return result.stdout
                except FileNotFoundError:
                    # Try wl-clipboard (Wayland)
                    try:
                        result = subprocess.run(['wl-paste'], 
                                              capture_output=True, text=True)
                        if result.returncode == 0:
                            return result.stdout
                    except FileNotFoundError:
                        pass
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def set_clipboard_text(text: str) -> bool:
        """Set text to system clipboard."""
        try:
            if os.name == 'nt':  # Windows
                import subprocess
                subprocess.run(['powershell', f'Set-Clipboard -Value "{text}"'], 
                             check=True)
                return True
            else:  # Linux/WSL
                try:
                    import subprocess
                    # Try xclip first
                    subprocess.run(['xclip', '-selection', 'clipboard'], 
                                 input=text, text=True, check=True)
                    return True
                except FileNotFoundError:
                    # Try wl-clipboard (Wayland)
                    try:
                        subprocess.run(['wl-copy'], 
                                     input=text, text=True, check=True)
                        return True
                    except FileNotFoundError:
                        pass
        except Exception:
            pass
        
        return False


# Test the persistence system
if __name__ == "__main__":
    print("Testing Persistence System...")
    
    # Create storage instance
    storage = PersistentStorage(".")
    
    # Test message storage
    print("Adding test messages...")
    storage.add_message("user", "Hello, this is a test message!")
    storage.add_message("assistant", "Hello! I can see this is working well.")
    storage.add_message("user", "Can you tell me about persistent storage?")
    storage.add_message("assistant", "Absolutely! The persistent storage system saves chat history to .grok/history/ and session data to .grok/session/.")
    
    # Test cost tracking
    print("Testing cost tracking...")
    storage.update_cost_tracking(0.0012, 150, "test_prompt")
    storage.update_cost_tracking(0.0043, 520, "test_response")
    
    # Test feature usage
    storage.add_feature_usage("grid_ui")
    storage.add_feature_usage("clipboard_paste")
    
    # Get session stats
    stats = storage.get_session_stats()
    print(f"Session Stats: {json.dumps(stats, indent=2)}")
    
    # Test clipboard
    clipboard = ClipboardHandler()
    clipboard_text = clipboard.get_clipboard_text()
    print(f"Clipboard content: {clipboard_text[:50] if clipboard_text else 'None'}...")
    
    print("Persistence system test complete!")