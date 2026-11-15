from types import SimpleNamespace

from monitoring.execution_tracker import (
    agent_metrics,
    get_agent_id,
    get_agent_name,
    get_task_id,
    get_task_name,
    expected_specialist,
    reset_tracking,
    routing_history,
    task_metrics,
)


def test_tracker_maps_current_crewai_event_objects():
    task = SimpleNamespace(
        id="task-123",
        name="Analyze financial data",
        agent=SimpleNamespace(id="agent-456", role="Financial Data Analyst")
    )
    event = SimpleNamespace(task=task, agent=None)

    assert get_task_id(event) == "task-123"
    assert get_task_name(event) == "Analyze financial data"
    assert get_agent_id(event) == "agent-456"
    assert get_agent_name(event) == "Financial Data Analyst"


def test_reset_tracking_clears_only_in_memory_metrics():
    agent_metrics.append({"agent": "test"})
    task_metrics.append({"task": "test"})
    routing_history.append({"event": "test"})

    reset_tracking()

    assert agent_metrics == []
    assert task_metrics == []
    assert routing_history == []


def test_task_description_maps_to_assigned_specialist():
    cases = {
        "Delegate this task to the Market Research Specialist.": "Senior Market Research Specialist",
        "Delegate this task to the Financial Data Analyst.": "Senior Financial Data Analyst",
        "Delegate this task to the Professional Report Writer.": "Professional Market Research Report Writer",
    }
    for task_description, specialist in cases.items():
        assert expected_specialist(task_description) == specialist


def test_reset_tracking_associates_provider_events_with_current_run():
    import monitoring.execution_tracker as tracker

    reset_tracking(run_id="run-123")
    assert tracker.current_run_id == "run-123"
    reset_tracking()
    assert tracker.current_run_id is None
