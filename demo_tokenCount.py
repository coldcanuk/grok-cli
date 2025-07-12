"""
Demonstration of TokenCounter functionality for Grok CLI.
"""

from grok_cli.tokenCount import TokenCounter, estimate_prompt_cost


def demo_basic_usage():
    """Demonstrate basic TokenCounter usage."""
    print("=" * 60)
    print("TokenCounter Demo - Basic Usage")
    print("=" * 60)
    
    # Create a token counter
    counter = TokenCounter("demo_session.json")
    
    # Test prompts of varying complexity
    prompts = [
        "Hello, world!",
        "Can you help me write a Python function to calculate fibonacci numbers?",
        "I need you to analyze this codebase, identify potential performance bottlenecks, create optimization recommendations, and implement the top 3 improvements with comprehensive testing.",
    ]
    
    print("\n1. Token Counting Examples:")
    for i, prompt in enumerate(prompts, 1):
        tokens = counter.count_tokens(prompt)
        print(f"   Prompt {i}: {tokens} tokens")
        print(f"   Text: '{prompt[:50]}{'...' if len(prompt) > 50 else ''}'")
        print()
    
    print("2. Cost Estimation Examples:")
    for i, prompt in enumerate(prompts, 1):
        estimate = counter.estimate_cost(prompt, expected_output_tokens=200, model="grok-beta")
        print(f"   Prompt {i} (grok-beta): ${estimate['total_estimated_cost']:.4f}")
        
        estimate_4 = counter.estimate_cost(prompt, expected_output_tokens=200, model="grok-4")
        print(f"   Prompt {i} (grok-4):    ${estimate_4['total_estimated_cost']:.4f}")
        print()


def demo_session_tracking():
    """Demonstrate session tracking functionality."""
    print("=" * 60)
    print("TokenCounter Demo - Session Tracking")
    print("=" * 60)
    
    counter = TokenCounter("demo_session.json")
    counter.reset_session()  # Start fresh for demo
    
    print("\n1. Simulating API calls...")
    
    # Simulate a series of API calls
    calls = [
        {"input": 50, "output": 100, "model": "grok-beta", "op": "simple_question"},
        {"input": 200, "output": 500, "model": "grok-4", "op": "code_generation"},
        {"input": 100, "output": 300, "model": "grok-beta", "cached": 25, "op": "follow_up"},
        {"input": 500, "output": 1200, "model": "grok-4", "searches": 2, "op": "research_task"},
    ]
    
    for i, call in enumerate(calls, 1):
        usage = counter.track_api_call(
            input_tokens=call["input"],
            output_tokens=call["output"],
            model=call["model"],
            cached_tokens=call.get("cached", 0),
            live_searches=call.get("searches", 0),
            operation_type=call["op"]
        )
        print(f"   Call {i} ({call['op']}): ${counter.session_costs.total_cost:.4f} total")
    
    print("\n2. Session Summary:")
    counter.display_session_costs()


def demo_model_comparison():
    """Demonstrate cost comparison across different models."""
    print("=" * 60)
    print("TokenCounter Demo - Model Comparison")
    print("=" * 60)
    
    test_prompt = "Create a comprehensive REST API with authentication, database integration, and comprehensive testing."
    expected_output = 2000  # tokens
    
    models = ["grok-beta", "grok-4", "grok-4-0709", "grok-3-mini"]
    
    print(f"\nCost comparison for complex task:")
    print(f"Prompt: '{test_prompt}'")
    print(f"Expected output: {expected_output} tokens\n")
    
    for model in models:
        estimate = estimate_prompt_cost(test_prompt, model)
        print(f"{model:<15}: ${estimate['total_estimated_cost']:.4f}")
        print(f"{'':15}  Input: {estimate['input_tokens']} tokens (${estimate['input_cost']:.4f})")
        print(f"{'':15}  Output: {estimate['estimated_output_tokens']} tokens (${estimate['output_cost']:.4f})")
        print()


def demo_leader_follower_costs():
    """Demonstrate cost tracking for leader-follower mode."""
    print("=" * 60)
    print("TokenCounter Demo - Leader-Follower Mode")
    print("=" * 60)
    
    counter = TokenCounter("leader_follower_demo.json")
    counter.reset_session()
    
    objective = "Implement a complete user authentication system with JWT tokens, password hashing, role-based access control, and comprehensive security testing."
    
    print(f"\nObjective: {objective}")
    print("\nSimulating Leader-Follower workflow:\n")
    
    # Leader phase (strategic planning)
    leader_input = counter.count_tokens(f"Create strategic plan for: {objective}")
    leader_output = 800  # Strategic plan is detailed
    
    usage_leader = counter.track_api_call(
        input_tokens=leader_input,
        output_tokens=leader_output,
        model="grok-3-mini",
        operation_type="leader_planning"
    )
    
    print(f"1. Leader Phase (grok-3-mini):")
    print(f"   Strategic planning: ${counter.session_costs.total_cost:.4f}")
    
    # Follower phase (execution)
    # Multiple API calls as follower executes the plan
    follower_calls = [
        {"input": 400, "output": 1200, "op": "phase1_investigation"},
        {"input": 600, "output": 2000, "op": "phase2_implementation"},
        {"input": 300, "output": 800, "op": "phase2_testing"},
        {"input": 200, "output": 600, "op": "phase3_polishing"},
    ]
    
    print(f"\n2. Follower Phase (grok-4-0709):")
    for call in follower_calls:
        counter.track_api_call(
            input_tokens=call["input"],
            output_tokens=call["output"],
            model="grok-4-0709",
            operation_type=call["op"]
        )
        print(f"   {call['op']}: ${counter.session_costs.total_cost:.4f} total")
    
    print(f"\n3. Complete Workflow Summary:")
    counter.display_session_costs()
    
    # Cost breakdown
    leader_cost = usage_leader.input_tokens * 1.00/1_000_000 + usage_leader.output_tokens * 3.00/1_000_000
    follower_cost = counter.session_costs.total_cost - leader_cost
    
    print(f"\nCost Analysis:")
    print(f"Leader (strategic planning): ${leader_cost:.4f}")
    print(f"Follower (execution):        ${follower_cost:.4f}")
    print(f"Cost efficiency: {(leader_cost/(leader_cost+follower_cost)*100):.1f}% planning, {(follower_cost/(leader_cost+follower_cost)*100):.1f}% execution")


def run_all_demos():
    """Run all demonstration functions."""
    print("TokenCounter - Comprehensive Demonstration")
    print("Showing real-world usage scenarios for Grok CLI\n")
    
    demo_basic_usage()
    print("\n" + "="*20 + " NEXT DEMO " + "="*20 + "\n")
    
    demo_session_tracking()
    print("\n" + "="*20 + " NEXT DEMO " + "="*20 + "\n")
    
    demo_model_comparison()
    print("\n" + "="*20 + " NEXT DEMO " + "="*20 + "\n")
    
    demo_leader_follower_costs()
    
    print("\n" + "=" * 60)
    print("Demo Complete! TokenCounter is ready for integration.")
    print("=" * 60)


if __name__ == "__main__":
    run_all_demos()