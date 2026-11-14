from crew.agents import researcher, analyst, writer


def test_three_agents_are_configured():
    """Verify that all three specialist agents exist."""

    agents = [researcher, analyst, writer]

    assert len(agents) == 3

    for agent in agents:
        assert agent.role
        assert agent.goal
        assert agent.backstory


def test_agents_have_distinct_roles():
    """Verify that each specialist has a distinct role."""

    agents = [researcher, analyst, writer]

    roles = [agent.role for agent in agents]

    assert len(set(roles)) == 3


def test_researcher_and_analyst_have_tools():
    """Verify that research and financial agents have tools."""

    assert researcher.tools
    assert analyst.tools