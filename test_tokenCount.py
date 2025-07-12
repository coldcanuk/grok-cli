"""
Comprehensive test suite for TokenCounter functionality.
"""

import os
import json
import tempfile
from grok_cli.tokenCount import TokenCounter, GrokPricing, TokenUsage, SessionCosts


def test_basic_token_counting():
    """Test basic token counting functionality."""
    print("Testing basic token counting...")
    
    counter = TokenCounter()
    
    # Test simple text
    simple_text = "Hello world"
    tokens = counter.count_tokens(simple_text)
    print(f"  '{simple_text}' -> {tokens} tokens")
    assert tokens > 0, "Token count should be positive"
    
    # Test longer text
    long_text = "This is a much longer text that should result in more tokens being counted by the tokenizer."
    long_tokens = counter.count_tokens(long_text)
    print(f"  Long text -> {long_tokens} tokens")
    assert long_tokens > tokens, "Longer text should have more tokens"
    
    print("PASSED: Basic token counting tests")


def test_pricing_calculations():
    """Test pricing calculation accuracy."""
    print("\nTesting pricing calculations...")
    
    # Test grok-beta pricing
    beta_pricing = GrokPricing.get_model_pricing("grok-beta")
    assert beta_pricing["input"] == 5.00, "Beta input pricing should be $5/1M"
    assert beta_pricing["output"] == 15.00, "Beta output pricing should be $15/1M"
    
    # Test grok-4 pricing
    grok4_pricing = GrokPricing.get_model_pricing("grok-4")
    assert grok4_pricing["input"] == 3.00, "Grok-4 input pricing should be $3/1M"
    assert grok4_pricing["cached_input"] == 0.75, "Grok-4 cached pricing should be $0.75/1M"
    
    # Test cost calculations
    cost_1m = GrokPricing.calculate_token_cost(1_000_000, 5.00)
    assert cost_1m == 5.00, "1M tokens at $5/1M should cost $5"
    
    cost_100k = GrokPricing.calculate_token_cost(100_000, 15.00)
    assert cost_100k == 1.50, "100K tokens at $15/1M should cost $1.50"
    
    # Test search pricing
    search_cost = GrokPricing.calculate_search_cost(1000)
    assert search_cost == 25.00, "1000 searches should cost $25"
    
    print("PASSED: Pricing calculation tests passed")


def test_session_tracking():
    """Test session tracking functionality."""
    print("\nTesting session tracking...")
    
    # Use temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        counter = TokenCounter(temp_file)
        
        # Track first API call
        usage1 = counter.track_api_call(
            input_tokens=100,
            output_tokens=200,
            model="grok-beta",
            operation_type="test1"
        )
        
        assert counter.session_costs.total_input_tokens == 100
        assert counter.session_costs.total_output_tokens == 200
        
        # Track second API call
        usage2 = counter.track_api_call(
            input_tokens=50,
            output_tokens=150,
            model="grok-4",
            cached_tokens=25,
            operation_type="test2"
        )
        
        assert counter.session_costs.total_input_tokens == 150
        assert counter.session_costs.total_output_tokens == 350
        assert counter.session_costs.total_cached_tokens == 25
        
        # Check that costs are calculated correctly
        assert counter.session_costs.total_cost > 0
        assert len(counter.session_costs.operations) == 2
        
        # Test session persistence
        counter2 = TokenCounter(temp_file)
        assert counter2.session_costs.total_input_tokens == 150
        assert counter2.session_costs.total_output_tokens == 350
        assert len(counter2.session_costs.operations) == 2
        
        print("PASSED: Session tracking tests passed")
        
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_cost_estimation():
    """Test cost estimation functionality."""
    print("\nTesting cost estimation...")
    
    counter = TokenCounter()
    
    test_prompt = "This is a test prompt for cost estimation."
    estimate = counter.estimate_cost(
        input_text=test_prompt,
        expected_output_tokens=100,
        model="grok-beta"
    )
    
    assert "input_tokens" in estimate
    assert "total_estimated_cost" in estimate
    assert estimate["input_tokens"] > 0
    assert estimate["total_estimated_cost"] > 0
    assert estimate["model"] == "grok-beta"
    
    print(f"  Estimate for test prompt: ${estimate['total_estimated_cost']:.4f}")
    print("PASSED: Cost estimation tests passed")


def test_message_token_counting():
    """Test token counting for message arrays."""
    print("\nTesting message token counting...")
    
    counter = TokenCounter()
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you!"}
    ]
    
    token_count = counter.count_messages_tokens(messages)
    assert token_count > 0, "Message token count should be positive"
    
    # Test with vision content
    vision_messages = [
        {"role": "user", "content": [
            {"type": "text", "text": "What's in this image?"},
            {"type": "image_url", "image_url": {"url": "http://example.com/image.jpg"}}
        ]}
    ]
    
    vision_tokens = counter.count_messages_tokens(vision_messages)
    assert vision_tokens > token_count, "Vision messages should have more tokens"
    
    print(f"  Regular messages: {token_count} tokens")
    print(f"  Vision messages: {vision_tokens} tokens")
    print("PASSED: Message token counting tests passed")


def test_session_summary():
    """Test session summary functionality."""
    print("\nTesting session summary...")
    
    counter = TokenCounter()
    
    # Add some operations
    counter.track_api_call(100, 200, "grok-beta", operation_type="chat")
    counter.track_api_call(50, 100, "grok-4", cached_tokens=25, live_searches=2)
    
    summary = counter.get_session_summary()
    
    assert "total_cost_usd" in summary
    assert "cost_breakdown" in summary
    assert "session_duration" in summary
    assert summary["operations_count"] == 2
    
    # Test cost breakdown structure
    breakdown = summary["cost_breakdown"]
    assert "input_tokens" in breakdown
    assert "output_tokens" in breakdown
    assert breakdown["input_tokens"]["count"] == 150
    assert breakdown["output_tokens"]["count"] == 300
    
    print(f"  Total cost: ${summary['total_cost_usd']:.4f}")
    print(f"  Operations: {summary['operations_count']}")
    print("PASSED: Session summary tests passed")


def test_different_models():
    """Test functionality with different Grok models."""
    print("\nTesting different model support...")
    
    counter = TokenCounter()
    
    models_to_test = ["grok-beta", "grok-4", "grok-4-0709", "grok-3-mini"]
    
    for model in models_to_test:
        pricing = GrokPricing.get_model_pricing(model)
        assert "input" in pricing
        assert "output" in pricing
        assert pricing["input"] > 0
        assert pricing["output"] > 0
        
        # Test cost estimation for each model
        estimate = counter.estimate_cost("Test prompt", model=model)
        assert estimate["model"] == model
        assert estimate["total_estimated_cost"] > 0
        
        print(f"  {model}: ${estimate['total_estimated_cost']:.4f}")
    
    print("PASSED: Different model tests passed")


def run_all_tests():
    """Run all test functions."""
    print("=" * 60)
    print("TokenCounter Comprehensive Test Suite")
    print("=" * 60)
    
    try:
        test_basic_token_counting()
        test_pricing_calculations()
        test_session_tracking()
        test_cost_estimation()
        test_message_token_counting()
        test_session_summary()
        test_different_models()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED SUCCESSFULLY!")
        print("TokenCounter is ready for integration.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)