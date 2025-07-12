"""
Token counting and pricing calculation for Grok API usage.

This module provides comprehensive token counting and cost calculation
for all Grok API operations, including input/output tokens, cached tokens,
and special operations like live search.
"""

import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import os


@dataclass
class TokenUsage:
    """Represents token usage for a single API call."""
    input_tokens: int = 0
    output_tokens: int = 0
    cached_input_tokens: int = 0
    live_searches: int = 0
    model: str = "grok-4-0709"
    timestamp: str = ""
    operation_type: str = "chat"  # chat, tool_call, search, etc.
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class SessionCosts:
    """Tracks cumulative costs for a session."""
    total_input_cost: float = 0.0
    total_output_cost: float = 0.0
    total_cached_cost: float = 0.0
    total_search_cost: float = 0.0
    total_cost: float = 0.0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cached_tokens: int = 0
    total_searches: int = 0
    start_time: str = ""
    operations: List[TokenUsage] = None
    
    def __post_init__(self):
        if not self.start_time:
            self.start_time = datetime.now(timezone.utc).isoformat()
        if self.operations is None:
            self.operations = []


class GrokPricing:
    """Manages pricing information for different Grok models."""
    
    # Pricing per 1M tokens (USD)
    PRICING_MATRIX = {
        "grok-beta": {
            "input": 5.00,
            "output": 15.00,
            "cached_input": 5.00,  # No cached pricing for beta
        },
        "grok-4": {
            "input": 3.00,
            "output": 15.00,
            "cached_input": 0.75,
        },
        "grok-4-0709": {
            "input": 3.00,
            "output": 15.00,
            "cached_input": 0.75,
        },
        "grok-3-mini": {
            "input": 1.00,  # Estimated lower cost for mini model
            "output": 3.00,  # Estimated lower cost for mini model
            "cached_input": 0.25,  # Estimated
        }
    }
    
    # Live search pricing per 1K searches
    LIVE_SEARCH_COST_PER_1K = 25.00
    
    @classmethod
    def get_model_pricing(cls, model: str) -> Dict[str, float]:
        """Get pricing for a specific model."""
        return cls.PRICING_MATRIX.get(model, cls.PRICING_MATRIX["grok-4-0709"])
    
    @classmethod
    def calculate_token_cost(cls, tokens: int, cost_per_million: float) -> float:
        """Calculate cost for given number of tokens."""
        return (tokens / 1_000_000) * cost_per_million
    
    @classmethod
    def calculate_search_cost(cls, num_searches: int) -> float:
        """Calculate cost for live searches."""
        return (num_searches / 1000) * cls.LIVE_SEARCH_COST_PER_1K


class TokenCounter:
    """Main class for counting tokens and calculating costs."""
    
    def __init__(self, session_file: Optional[str] = None):
        self.session_costs = SessionCosts()
        self.session_file = session_file or "token_session.json"
        self.tokenizer = None
        self._init_tokenizer()
        self._load_session()
    
    def _init_tokenizer(self):
        """Initialize the tokenizer for accurate token counting."""
        try:
            import tiktoken
            # Use cl100k_base encoding which is compatible with Grok
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except ImportError:
            print("WARNING: tiktoken not available. Install with: pip install tiktoken")
            print("   Token counts will be estimated using character-based approximation.")
            self.tokenizer = None
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken or approximation."""
        # Input validation - ensure text is a string
        if text is None:
            return 0
        if not isinstance(text, str):
            text = str(text)
        
        # Handle empty strings
        if not text.strip():
            return 0
            
        if self.tokenizer:
            try:
                return len(self.tokenizer.encode(text))
            except Exception as e:
                print(f"Warning: Tokenizer error: {e}, falling back to approximation")
                # Fall back to approximation if tokenizer fails
                return max(1, len(text) // 4)
        else:
            # Rough approximation: ~4 characters per token
            return max(1, len(text) // 4)
    
    def count_messages_tokens(self, messages: List[Dict[str, Any]], model: str = "grok-beta") -> int:
        """Count tokens for a list of messages, including system overhead."""
        total_tokens = 0
        
        for message in messages:
            content = message.get("content", "")
            if isinstance(content, list):
                # Handle vision content with images
                for item in content:
                    if item.get("type") == "text":
                        total_tokens += self.count_tokens(item.get("text", ""))
                    elif item.get("type") == "image_url":
                        # Approximate vision token cost (varies by image size)
                        total_tokens += 765  # Base cost for vision processing
            else:
                total_tokens += self.count_tokens(content)
            
            # Add overhead for message formatting
            total_tokens += 4  # Role + message formatting overhead
        
        # Add model-specific overhead
        total_tokens += 3  # Final formatting
        
        return total_tokens
    
    def track_api_call(self, 
                      input_tokens: int,
                      output_tokens: int,
                      model: str = "grok-4-0709",
                      cached_tokens: int = 0,
                      live_searches: int = 0,
                      operation_type: str = "chat") -> TokenUsage:
        """Track a single API call and calculate its cost."""
        
        usage = TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_input_tokens=cached_tokens,
            live_searches=live_searches,
            model=model,
            operation_type=operation_type
        )
        
        # Calculate costs
        pricing = GrokPricing.get_model_pricing(model)
        
        input_cost = GrokPricing.calculate_token_cost(input_tokens, pricing["input"])
        output_cost = GrokPricing.calculate_token_cost(output_tokens, pricing["output"])
        cached_cost = GrokPricing.calculate_token_cost(cached_tokens, pricing["cached_input"])
        search_cost = GrokPricing.calculate_search_cost(live_searches)
        
        # Update session totals
        self.session_costs.total_input_cost += input_cost
        self.session_costs.total_output_cost += output_cost
        self.session_costs.total_cached_cost += cached_cost
        self.session_costs.total_search_cost += search_cost
        self.session_costs.total_cost = (
            self.session_costs.total_input_cost + 
            self.session_costs.total_output_cost + 
            self.session_costs.total_cached_cost + 
            self.session_costs.total_search_cost
        )
        
        self.session_costs.total_input_tokens += input_tokens
        self.session_costs.total_output_tokens += output_tokens
        self.session_costs.total_cached_tokens += cached_tokens
        self.session_costs.total_searches += live_searches
        
        self.session_costs.operations.append(usage)
        
        self._save_session()
        return usage
    
    def estimate_cost(self, 
                     input_text: str, 
                     expected_output_tokens: int = 500,
                     model: str = "grok-4-0709",
                     include_searches: int = 0) -> Dict[str, float]:
        """Estimate cost for an operation before making the API call."""
        
        input_tokens = self.count_tokens(input_text)
        pricing = GrokPricing.get_model_pricing(model)
        
        input_cost = GrokPricing.calculate_token_cost(input_tokens, pricing["input"])
        output_cost = GrokPricing.calculate_token_cost(expected_output_tokens, pricing["output"])
        search_cost = GrokPricing.calculate_search_cost(include_searches)
        
        total_estimated = input_cost + output_cost + search_cost
        
        return {
            "input_tokens": input_tokens,
            "estimated_output_tokens": expected_output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "search_cost": search_cost,
            "total_estimated_cost": total_estimated,
            "model": model
        }
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the current session."""
        duration = self._get_session_duration()
        
        return {
            "session_duration": duration,
            "total_cost_usd": round(self.session_costs.total_cost, 4),
            "cost_breakdown": {
                "input_tokens": {
                    "count": self.session_costs.total_input_tokens,
                    "cost": round(self.session_costs.total_input_cost, 4)
                },
                "output_tokens": {
                    "count": self.session_costs.total_output_tokens,
                    "cost": round(self.session_costs.total_output_cost, 4)
                },
                "cached_tokens": {
                    "count": self.session_costs.total_cached_tokens,
                    "cost": round(self.session_costs.total_cached_cost, 4)
                },
                "live_searches": {
                    "count": self.session_costs.total_searches,
                    "cost": round(self.session_costs.total_search_cost, 4)
                }
            },
            "operations_count": len(self.session_costs.operations),
            "start_time": self.session_costs.start_time
        }
    
    def display_cost_warning(self, estimated_cost: float, threshold: float = 1.0):
        """Display warning if estimated cost exceeds threshold."""
        if estimated_cost > threshold:
            # NOTE: These warnings should be displayed through the UI, not printed directly
            # print(f"WARNING: High cost operation: ${estimated_cost:.4f} USD")
            # print(f"   Session total will be: ${self.session_costs.total_cost + estimated_cost:.4f} USD")
            pass
    
    def display_session_costs(self):
        """Display current session costs in a user-friendly format."""
        summary = self.get_session_summary()
        
        # NOTE: This method should return formatted text, not print directly
        # The calling code should handle displaying this through the UI
        # Commenting out all print statements to prevent UI corruption
        
        # print("\nSession Cost Summary")
        # print("=" * 50)
        # print(f"Session Duration: {summary['session_duration']}")
        # print(f"Total Cost: ${summary['total_cost_usd']:.4f} USD")
        # print()
        # print("Cost Breakdown:")
        # 
        # breakdown = summary['cost_breakdown']
        # if breakdown['input_tokens']['count'] > 0:
        #     print(f"  Input Tokens: {breakdown['input_tokens']['count']:,} -> ${breakdown['input_tokens']['cost']:.4f}")
        # 
        # if breakdown['output_tokens']['count'] > 0:
        #     print(f"  Output Tokens: {breakdown['output_tokens']['count']:,} -> ${breakdown['output_tokens']['cost']:.4f}")
        # 
        # if breakdown['cached_tokens']['count'] > 0:
        #     print(f"  Cached Tokens: {breakdown['cached_tokens']['count']:,} -> ${breakdown['cached_tokens']['cost']:.4f}")
        # 
        # if breakdown['live_searches']['count'] > 0:
        #     print(f"  Live Searches: {breakdown['live_searches']['count']} -> ${breakdown['live_searches']['cost']:.4f}")
        # 
        # print(f"\nOperations: {summary['operations_count']}")
        # print("=" * 50)
        pass
    
    def _get_session_duration(self) -> str:
        """Calculate session duration as human-readable string."""
        start = datetime.fromisoformat(self.session_costs.start_time.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        duration = now - start
        
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        elif minutes > 0:
            return f"{int(minutes)}m {int(seconds)}s"
        else:
            return f"{int(seconds)}s"
    
    def _save_session(self):
        """Save session data to file."""
        try:
            session_data = asdict(self.session_costs)
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save session data: {e}")
    
    def _load_session(self):
        """Load existing session data from file."""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r') as f:
                    data = json.load(f)
                    
                # Reconstruct operations list
                operations = []
                for op_data in data.get('operations', []):
                    operations.append(TokenUsage(**op_data))
                
                data['operations'] = operations
                self.session_costs = SessionCosts(**data)
            except Exception as e:
                print(f"Warning: Could not load session data: {e}")
                # Start fresh session
                self.session_costs = SessionCosts()
    
    def reset_session(self):
        """Reset the current session and start fresh."""
        if os.path.exists(self.session_file):
            os.remove(self.session_file)
        self.session_costs = SessionCosts()
        print("Session costs reset.")


# Convenience functions for easy integration
def create_token_counter(session_file: Optional[str] = None) -> TokenCounter:
    """Create a new TokenCounter instance."""
    return TokenCounter(session_file)


def estimate_prompt_cost(prompt: str, model: str = "grok-beta") -> Dict[str, Any]:
    """Quick cost estimation for a prompt."""
    counter = TokenCounter()
    return counter.estimate_cost(prompt, model=model)


if __name__ == "__main__":
    # Example usage and testing
    print("Token Counter Test")
    print("=" * 30)
    
    counter = TokenCounter("test_session.json")
    
    # Test token counting
    test_prompt = "Hello, how are you today? This is a test prompt for token counting."
    tokens = counter.count_tokens(test_prompt)
    print(f"Test prompt: '{test_prompt}'")
    print(f"Token count: {tokens}")
    
    # Test cost estimation
    estimate = counter.estimate_cost(test_prompt, expected_output_tokens=100)
    print(f"\nCost estimate: ${estimate['total_estimated_cost']:.4f}")
    
    # Simulate an API call
    usage = counter.track_api_call(
        input_tokens=tokens,
        output_tokens=85,
        model="grok-beta",
        operation_type="test"
    )
    
    print(f"\nTracked API call:")
    print(f"Input: {usage.input_tokens} tokens")
    print(f"Output: {usage.output_tokens} tokens")
    
    # Display session summary
    counter.display_session_costs()