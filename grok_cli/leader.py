"""
Leader-Follower orchestration for strategic planning and execution
"""

import json
import os
import time
from typing import Dict, Any, List
from datetime import datetime

from .utils import get_api_key, build_vision_content


class LeaderFollowerOrchestrator:
    """Orchestrates leader-follower workflow with strategic planning."""
    
    def __init__(self, engine, src_path: str):
        self.engine = engine
        self.src_path = src_path
        self.temp_work_dir = os.path.join(src_path, "tempWork")
        self.follow_me_path = os.path.join(self.temp_work_dir, "followMe.md")
        
        # Ensure tempWork directory exists
        os.makedirs(self.temp_work_dir, exist_ok=True)
    
    def execute_leader_follower_workflow(self, objective: str, args):
        """Execute the complete leader-follower workflow."""
        print("🔍 Phase 1: Leader Analysis & Strategic Planning...")
        
        # Step 1: Leader creates strategic plan
        strategic_plan = self._create_strategic_plan(objective, args)
        
        # Step 2: Save plan to followMe.md
        self._save_follow_me_plan(strategic_plan)
        
        print(f"📋 Strategic plan saved to: {self.follow_me_path}")
        print("\n⚡ Phase 2: Follower Execution...")
        
        # Step 3: Follower executes the plan
        self._execute_follower_workflow(objective, strategic_plan, args)
        
        print("\n✅ Leader-Follower workflow completed!")
    
    def _create_strategic_plan(self, objective: str, args) -> str:
        """Use grok-3-mini (leader) to create strategic plan."""
        
        # Build leader system prompt for strategic planning
        leader_system_prompt = self._build_leader_system_prompt()
        
        # Build leader planning prompt
        planning_prompt = self._build_planning_prompt(objective)
        
        # Configure leader with grok-3-mini
        key, brave_key = get_api_key(args)
        
        messages = [
            {"role": "system", "content": leader_system_prompt},
            {"role": "user", "content": planning_prompt}
        ]
        
        # Override model to use grok-3-mini for leader
        original_model = args.model if hasattr(args, 'model') else self.engine.config.get("model", "grok-4")
        leader_args = type('Args', (), {**vars(args), 'model': 'grok-3-mini'})()
        
        print("🧠 Leader (grok-3-mini) analyzing objective and creating strategic plan...")
        
        # Use engine to get strategic plan from leader
        response_content = ""
        
        # Temporarily capture the response
        original_run_chat_loop = self.engine.run_chat_loop
        captured_response = []
        
        def capture_response(args, key, brave_key, messages):
            # Call original method but capture output
            result = original_run_chat_loop(args, key, brave_key, messages)
            return result
        
        # Get strategic plan from leader
        strategic_plan = self._call_leader_model(leader_args, key, brave_key, messages)
        
        return strategic_plan
    
    def _call_leader_model(self, args, key: str, brave_key: str, messages: List[Dict]) -> str:
        """Call the leader model and capture response."""
        try:
            # Use engine's api_call method for cost tracking
            response = self.engine.api_call(key, messages, "grok-3-mini", False)
            result = response.json()
            
            # Track the response for cost calculation
            self.engine.track_api_response(result, "grok-3-mini", "leader_planning")
            
            return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error calling leader model: {e}")
            return self._create_fallback_plan()
    
    def _build_leader_system_prompt(self) -> str:
        """Build system prompt for the leader (strategic planner)."""
        return """You are a Strategic Planning Leader using grok-3-mini. Your role is to analyze objectives and create comprehensive execution plans for a follower agent.

CRITICAL INSTRUCTIONS:
- Create plans optimized for AI agents, not humans
- Be extremely detailed and systematic
- Think systemically about error boundaries and dependencies
- Consider the broader system context

Your output MUST follow this exact structure:

# STRATEGIC EXECUTION PLAN

## SYSTEMIC ANALYSIS
### Error Boundaries
- [Identify potential failure points and dependencies]
### System Context
- [Analyze if this is isolated or part of larger system]
### Risk Assessment
- [Evaluate technical and implementation risks]

## PHASE 1: INVESTIGATION
**Objective**: Gather all data needed to accomplish the objective
### Milestones:
1. [Major milestone 1]
2. [Major milestone 2]
### ToDo Tasks:
- [ ] [Specific investigation task 1]
- [ ] [Specific investigation task 2]
- [ ] [Continue with detailed tasks...]

## PHASE 2: HEAVY LIFTING
**Objective**: Core implementation work, coding, testing, refactoring
### Milestones:
1. [Major milestone 1]
2. [Major milestone 2]
### ToDo Tasks:
- [ ] [Specific implementation task 1]
- [ ] [Specific implementation task 2]
- [ ] [Continue with detailed tasks...]

## PHASE 3: POLISH & FINALIZATION
**Objective**: Testing, tweaking, polishing for final push
### Milestones:
1. [Major milestone 1]
2. [Major milestone 2]
### ToDo Tasks:
- [ ] [Specific polishing task 1]
- [ ] [Specific polishing task 2]
- [ ] [Continue with detailed tasks...]

## EXECUTION NOTES
- [Additional implementation guidance]
- [Special considerations]
- [Success criteria]

Make your plan meticulous and comprehensive."""
    
    def _build_planning_prompt(self, objective: str) -> str:
        """Build the planning prompt for the leader."""
        
        # Get project context for better planning
        project_context = self.engine.project_context or "No project context available"
        
        return f"""OBJECTIVE: {objective}

PROJECT CONTEXT:
{project_context}

SOURCE DIRECTORY: {self.src_path}

Please analyze this objective and create a comprehensive strategic execution plan. Consider:

1. SYSTEMIC ANALYSIS:
   - What are the error boundaries?
   - Is this an isolated task or part of a larger system?
   - What dependencies exist?
   - What could go wrong?

2. THREE-PHASE BREAKDOWN:
   - Phase 1 (Investigation): What information do we need?
   - Phase 2 (Heavy Lifting): What is the core work?
   - Phase 3 (Polish): How do we ensure quality and completion?

3. DETAILED PLANNING:
   - Break each phase into specific milestones
   - Create meticulous ToDo task lists
   - Consider technical implementation details
   - Plan for testing and validation

Create a plan that a follower AI agent can execute systematically."""
    
    def _save_follow_me_plan(self, strategic_plan: str):
        """Save the strategic plan to followMe.md."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        header = f"""# followMe.md
*Strategic Execution Plan*
*Generated: {timestamp}*
*Leader: grok-3-mini | Follower: grok-4-0709*

---

"""
        
        full_content = header + strategic_plan
        
        with open(self.follow_me_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
    
    def _execute_follower_workflow(self, objective: str, strategic_plan: str, args):
        """Execute the follower workflow using grok-4-0709."""
        
        # Build follower system prompt
        follower_system_prompt = self._build_follower_system_prompt()
        
        # Build follower execution prompt
        execution_prompt = self._build_execution_prompt(objective, strategic_plan)
        
        # Configure follower with grok-4-0709
        key, brave_key = get_api_key(args)
        
        messages = [
            {"role": "system", "content": follower_system_prompt},
            {"role": "user", "content": execution_prompt}
        ]
        
        # Override model to use grok-4-0709 for follower
        follower_args = type('Args', (), {**vars(args), 'model': 'grok-4-0709'})()
        
        print("🚀 Follower (grok-4-0709) executing strategic plan...")
        
        # Execute with follower
        self.engine.run_chat_loop(follower_args, key, brave_key, messages)
    
    def _build_follower_system_prompt(self) -> str:
        """Build system prompt for the follower (executor)."""
        enhanced_system_prompt = self.engine.get_enhanced_system_prompt()
        
        follower_addition = """

LEADER-FOLLOWER MODE ACTIVATED:
You are the FOLLOWER agent (grok-4-0709) executing a strategic plan created by the LEADER (grok-3-mini).

EXECUTION PRINCIPLES:
- Follow the strategic plan systematically
- Execute each phase in order: Investigation → Heavy Lifting → Polish
- Complete all milestones and todo tasks methodically
- Validate your work at each step
- Adapt the plan intelligently if needed, but stay true to the strategic direction
- Use all available tools to accomplish the objectives
- Report progress as you complete each phase and milestone

Your goal is to transform the strategic plan into successful execution."""
        
        return enhanced_system_prompt + follower_addition
    
    def _build_execution_prompt(self, objective: str, strategic_plan: str) -> str:
        """Build execution prompt for the follower."""
        return f"""EXECUTION MISSION:

ORIGINAL OBJECTIVE: {objective}

STRATEGIC PLAN FROM LEADER:
{strategic_plan}

INSTRUCTIONS:
1. Read and understand the complete strategic plan above
2. Execute the plan systematically, phase by phase
3. Follow the milestones and todo tasks precisely
4. Use all available tools to accomplish the work
5. Validate and test your work thoroughly
6. Report completion of each major milestone

Begin execution of Phase 1 (Investigation) now. Work through each phase methodically until the objective is fully accomplished."""
    
    def _create_fallback_plan(self) -> str:
        """Create a fallback plan if leader model fails."""
        return """# FALLBACK STRATEGIC EXECUTION PLAN

## SYSTEMIC ANALYSIS
### Error Boundaries
- Leader model unavailable - executing with fallback plan
### System Context
- Operating with limited strategic analysis
### Risk Assessment
- Proceeding with general-purpose execution approach

## PHASE 1: INVESTIGATION
**Objective**: Understand the requirements and current state
### Milestones:
1. Analyze current codebase structure
2. Identify implementation requirements
### ToDo Tasks:
- [ ] Examine existing code patterns
- [ ] Identify files that need modification
- [ ] Understand dependencies and constraints

## PHASE 2: HEAVY LIFTING
**Objective**: Implement the core functionality
### Milestones:
1. Implement core features
2. Test basic functionality
### ToDo Tasks:
- [ ] Create or modify necessary files
- [ ] Implement required functionality
- [ ] Perform basic testing

## PHASE 3: POLISH & FINALIZATION
**Objective**: Ensure quality and completeness
### Milestones:
1. Validate implementation
2. Complete final testing
### ToDo Tasks:
- [ ] Run comprehensive tests
- [ ] Verify all requirements met
- [ ] Clean up and document

## EXECUTION NOTES
- This is a fallback plan - adapt based on specific requirements
- Focus on understanding the objective first
- Implement incrementally and test frequently"""