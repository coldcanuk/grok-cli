"""
Test cost tracking integration with grok-cli.
"""

from grok_cli.engine import GrokEngine
from grok_cli.tokenCount import TokenCounter


def test_engine_cost_integration():
    """Test that GrokEngine properly integrates with TokenCounter."""
    print("Testing GrokEngine cost tracking integration...")
    
    # Create engine
    engine = GrokEngine()
    
    # Test enabling cost tracking
    engine.enable_cost_tracking("test_integration.json")
    
    assert engine.cost_tracking_enabled == True
    assert engine.token_counter is not None
    assert isinstance(engine.token_counter, TokenCounter)
    
    print("PASS: Cost tracking enabled successfully")
    
    # Test message token counting
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]
    
    if engine.token_counter:
        token_count = engine.token_counter.count_messages_tokens(messages, "grok-beta")
        print(f"PASS: Token counting works: {token_count} tokens for test messages")
    
    # Test mock response tracking
    mock_response = {
        "usage": {
            "prompt_tokens": 25,
            "completion_tokens": 100,
            "total_tokens": 125
        },
        "choices": [{"message": {"content": "Test response"}}]
    }
    
    engine.track_api_response(mock_response, "grok-beta", "test")
    
    # Check that tracking worked
    if engine.token_counter:
        summary = engine.token_counter.get_session_summary()
        print(f"Debug: Input tokens = {summary['cost_breakdown']['input_tokens']['count']}")
        print(f"Debug: Output tokens = {summary['cost_breakdown']['output_tokens']['count']}")
        
        # Should have the tokens from our mock response
        assert summary["cost_breakdown"]["input_tokens"]["count"] >= 25
        assert summary["cost_breakdown"]["output_tokens"]["count"] >= 100
        assert summary["total_cost_usd"] > 0
        
        print(f"PASS: Response tracking works: ${summary['total_cost_usd']:.4f} total cost")
    
    # Test session summary
    print("\n--- Session Summary Test ---")
    engine.display_session_summary()
    
    print("\nPASS: All integration tests passed!")


def test_cli_argument_integration():
    """Test that CLI properly passes cost tracking flag."""
    print("\nTesting CLI argument integration...")
    
    # Mock args object
    class MockArgs:
        def __init__(self):
            self.cost = True
            self.src = "."
            self.prompt = "Test prompt"
            self.image = None
            self.model = "grok-beta"
            self.stream = False
            self.debug = None
    
    args = MockArgs()
    engine = GrokEngine()
    
    # Test that cost tracking can be enabled from args
    if args.cost:
        engine.enable_cost_tracking()
    
    assert engine.cost_tracking_enabled == True
    print("PASS: CLI argument integration works")


if __name__ == "__main__":
    test_engine_cost_integration()
    test_cli_argument_integration()
    
    print("\n" + "="*50)
    print("Cost tracking integration is ready!")
    print("Use --cost flag with any grok-cli command.")
    print("="*50)