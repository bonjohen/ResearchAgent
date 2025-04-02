"""
Tests for the base agent module.
"""

import asyncio
import pytest
# No mocks needed for these tests

from src.agents.base import BaseAgent, AgentRegistry, AgentPipeline, ParallelAgents

# Create a concrete implementation of BaseAgent for testing
# Use a naming convention that doesn't start with 'Test' to prevent pytest from collecting it
class ConcreteAgent(BaseAgent):
    """Test implementation of BaseAgent."""

    def __init__(self, name, description="", delay=0, error=False):
        super().__init__(name, description)
        self.delay = delay
        self.error = error

    async def process(self, input_data):
        if self.delay > 0:
            await asyncio.sleep(self.delay)

        if self.error:
            raise ValueError("Test error")

        return f"{self.name} processed: {input_data}"

class TestBaseAgent:
    """Tests for the BaseAgent class."""

    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test agent initialization."""
        agent = ConcreteAgent("test_agent", "Test agent description")

        assert agent.name == "test_agent"
        assert agent.description == "Test agent description"

    @pytest.mark.asyncio
    async def test_agent_process(self):
        """Test agent processing."""
        agent = ConcreteAgent("test_agent")
        result = await agent.process("test_input")

        assert result == "test_agent processed: test_input"

    @pytest.mark.asyncio
    async def test_agent_run(self):
        """Test agent run method."""
        agent = ConcreteAgent("test_agent")
        result = await agent.run("test_input")

        assert result == "test_agent processed: test_input"

    @pytest.mark.asyncio
    async def test_agent_run_with_error(self):
        """Test agent run method with error."""
        agent = ConcreteAgent("test_agent", error=True)

        with pytest.raises(ValueError, match="Test error"):
            await agent.run("test_input")

class TestAgentRegistry:
    """Tests for the AgentRegistry class."""

    def setup_method(self):
        """Set up the test environment."""
        # Clear the registry before each test
        AgentRegistry._agents = {}

    def test_register_and_get_agent(self):
        """Test registering and retrieving an agent."""
        agent = ConcreteAgent("test_agent")
        AgentRegistry.register(agent)

        retrieved_agent = AgentRegistry.get("test_agent")
        assert retrieved_agent is agent

    def test_get_nonexistent_agent(self):
        """Test retrieving a non-existent agent."""
        retrieved_agent = AgentRegistry.get("nonexistent_agent")
        assert retrieved_agent is None

    def test_list_agents(self):
        """Test listing all registered agents."""
        agent1 = ConcreteAgent("agent1")
        agent2 = ConcreteAgent("agent2")

        AgentRegistry.register(agent1)
        AgentRegistry.register(agent2)

        agent_list = AgentRegistry.list_agents()
        assert set(agent_list) == {"agent1", "agent2"}

class TestAgentPipeline:
    """Tests for the AgentPipeline class."""

    @pytest.mark.asyncio
    async def test_pipeline_execution(self):
        """Test executing a pipeline of agents."""
        agent1 = ConcreteAgent("agent1")
        agent2 = ConcreteAgent("agent2")

        pipeline = AgentPipeline([agent1, agent2])
        result = await pipeline.run("initial_input")

        # The output of agent1 becomes the input to agent2
        expected = "agent2 processed: agent1 processed: initial_input"
        assert result == expected

    @pytest.mark.asyncio
    async def test_empty_pipeline(self):
        """Test executing an empty pipeline."""
        pipeline = AgentPipeline([])
        result = await pipeline.run("initial_input")

        # With no agents, the input should be returned unchanged
        assert result == "initial_input"

    @pytest.mark.asyncio
    async def test_pipeline_with_error(self):
        """Test pipeline execution with an error."""
        agent1 = ConcreteAgent("agent1")
        agent2 = ConcreteAgent("agent2", error=True)
        agent3 = ConcreteAgent("agent3")  # This agent should not be called

        pipeline = AgentPipeline([agent1, agent2, agent3])

        with pytest.raises(ValueError, match="Test error"):
            await pipeline.run("initial_input")

class TestParallelAgents:
    """Tests for the ParallelAgents class."""

    @pytest.mark.asyncio
    async def test_parallel_execution(self):
        """Test executing agents in parallel."""
        agent1 = ConcreteAgent("agent1")
        agent2 = ConcreteAgent("agent2")

        parallel = ParallelAgents([agent1, agent2])
        results = await parallel.run("test_input")

        assert results[0] == "agent1 processed: test_input"
        assert results[1] == "agent2 processed: test_input"

    @pytest.mark.asyncio
    async def test_parallel_with_delays(self):
        """Test parallel execution with delays."""
        # Create agents with different delays
        agent1 = ConcreteAgent("agent1", delay=0.1)
        agent2 = ConcreteAgent("agent2", delay=0.2)

        parallel = ParallelAgents([agent1, agent2])

        # Measure the time it takes to run both agents
        import time
        start_time = time.time()
        results = await parallel.run("test_input")
        elapsed_time = time.time() - start_time

        # The elapsed time should be close to the longest delay (0.2s)
        # but not the sum of delays (0.3s)
        assert elapsed_time < 0.3
        assert results[0] == "agent1 processed: test_input"
        assert results[1] == "agent2 processed: test_input"

    @pytest.mark.asyncio
    async def test_parallel_with_errors(self):
        """Test parallel execution with errors."""
        agent1 = ConcreteAgent("agent1")
        agent2 = ConcreteAgent("agent2", error=True)

        parallel = ParallelAgents([agent1, agent2])
        results = await parallel.run("test_input")

        assert results[0] == "agent1 processed: test_input"
        assert isinstance(results[1], ValueError)
        assert str(results[1]) == "Test error"
