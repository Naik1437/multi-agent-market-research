from crew.crew import market_research_crew
from crewai import Process


def test_crew_uses_hierarchical_process():
    """Verify that the crew uses hierarchical execution."""

    assert market_research_crew.process == Process.hierarchical


def test_crew_has_three_agents():
    """Verify that all three specialist agents are configured."""

    assert len(market_research_crew.agents) == 3


def test_crew_has_three_tasks():
    """Verify that all three tasks are configured."""

    assert len(market_research_crew.tasks) == 3


def test_crew_has_manager_llm():
    """Verify that the hierarchical crew has a manager LLM."""

    assert market_research_crew.manager_llm is not None