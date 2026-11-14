import json
import time
from pathlib import Path
from threading import Lock

from crewai.events import BaseEventListener
from crewai.events.event_types import (
    AgentExecutionStartedEvent,
    AgentExecutionCompletedEvent,
    AgentExecutionErrorEvent,
    TaskStartedEvent,
    TaskCompletedEvent,
    TaskFailedEvent,
    CrewKickoffCompletedEvent,
    CrewKickoffFailedEvent,
)

BASE_DIR = Path(__file__).resolve().parent.parent
BENCHMARK_FILE = BASE_DIR / "benchmarks" / "benchmarks.json"

lock = Lock()

agent_starts = {}
task_starts = {}
task_agents = {}

agent_metrics = []
task_metrics = []
routing_history = []


def get_agent_name(event, source=None):

        # Get actual agent directly from CrewAI event
    agent = getattr(event, "agent", None)
    agent_role = getattr(agent, "role", None)
    if agent_role:
        return str(agent_role)

    # 1. Check event metadata
    role = getattr(event, "agent_role", None)
    if role:
        return str(role)

    # 2. Check the associated task
    task = getattr(event, "task", None)

    if task is not None:
        agent = getattr(task, "agent", None)

        if agent is not None:
            role = getattr(agent, "role", None)
            if role:
                return str(role)

    # 3. Check event source
    if source is not None:

        role = getattr(source, "role", None)
        if role:
            return str(role)

        agent = getattr(source, "agent", None)

        if agent is not None:
            role = getattr(agent, "role", None)
            if role:
                return str(role)

    # 4. Use task-to-agent mapping
    task_id = getattr(event, "task_id", None)

    if task_id and task_id in task_agents:
        return task_agents[task_id]

    return "Unknown"


class ExecutionTracker(BaseEventListener):

    def setup_listeners(self, event_bus):

        @event_bus.on(AgentExecutionStartedEvent)
        def agent_started(source, event):

            key = event.event_id
            agent_name = get_agent_name(event, source)

            with lock:

                agent_starts[key] = {
                    "agent": agent_name,
                    "agent_id": event.agent_id,
                    "task_id": event.task_id,
                    "start": time.perf_counter()
                }

        @event_bus.on(AgentExecutionCompletedEvent)
        def agent_completed(source, event):

            with lock:

                key = event.started_event_id

                if key not in agent_starts:

                    key = next(
                        (
                            k for k, v in reversed(
                                list(agent_starts.items())
                            )
                            if (
                                event.agent_id is not None
                                and v["agent_id"] == event.agent_id
                            )
                            and (
                                event.task_id is None
                                or v["task_id"] == event.task_id
                            )
                        ),
                        None
                    )

                if key is None:
                    return

                started = agent_starts.pop(key)

                agent_name = get_agent_name(event, source)

                if agent_name == "Unknown":
                    agent_name = started["agent"]

                agent_metrics.append({
                    "agent": agent_name,
                    "agent_id": event.agent_id or started["agent_id"],
                    "task_id": event.task_id or started["task_id"],
                    "task_name": event.task_name,
                    "duration_seconds": round(
                        time.perf_counter() - started["start"], 2
                    ),
                    "status": "COMPLETED"
                })

                routing_history.append({
                    "event": "agent_execution_completed",
                    "agent": agent_name,
                    "task_id": event.task_id or started["task_id"]
                })

        @event_bus.on(AgentExecutionErrorEvent)
        def agent_failed(source, event):

            agent_name = get_agent_name(event, source)

            with lock:

                agent_metrics.append({
                    "agent": agent_name,
                    "task_id": event.task_id,
                    "status": "FAILED"
                })

        @event_bus.on(TaskStartedEvent)
        def task_started(source, event):

            key = event.event_id
            agent_name = get_agent_name(event, source)

            with lock:

                if event.task_id and agent_name != "Unknown":
                    task_agents[event.task_id] = agent_name

                task_starts[key] = {
                    "start": time.perf_counter(),
                    "task_name": event.task_name or "Unknown Task",
                    "agent": agent_name,
                    "task_id": event.task_id
                }

                routing_history.append({
                    "event": "task_assignment_observed",
                    "task": event.task_name or "Unknown Task",
                    "agent": agent_name,
                    "agent_id": event.agent_id,
                    "task_id": event.task_id
                })

                print(
                    f"[TRACKER] Task started: "
                    f"{event.task_name or 'Unknown Task'}"
                )

        @event_bus.on(TaskCompletedEvent)
        def task_completed(source, event):

            with lock:

                key = event.started_event_id

                if key not in task_starts:

                    key = next(
                        (
                            k for k, v in reversed(
                                list(task_starts.items())
                            )
                            if (
                                event.task_id is not None
                                and v["task_id"] == event.task_id
                            )
                        ),
                        None
                    )

                if key is None:
                    return

                started = task_starts.pop(key)

                agent_name = get_agent_name(event, source)

                if agent_name == "Unknown":
                    agent_name = started["agent"]

                duration = round(
                    time.perf_counter() - started["start"], 2
                )

                task_metrics.append({
                    "task": event.task_name or started["task_name"],
                    "agent": agent_name,
                    "duration_seconds": duration,
                    "status": "COMPLETED"
                })

                print(
                    f"[TRACKER] Task completed: "
                    f"{started['task_name']} "
                    f"({duration} seconds)"
                )

        @event_bus.on(TaskFailedEvent)
        def task_failed(source, event):

            agent_name = get_agent_name(event, source)

            with lock:

                task_metrics.append({
                    "task": event.task_name or "Unknown Task",
                    "agent": agent_name,
                    "status": "FAILED"
                })

        @event_bus.on(CrewKickoffCompletedEvent)
        def crew_completed(source, event):

            save_benchmarks("SUCCESS")

        @event_bus.on(CrewKickoffFailedEvent)
        def crew_failed(source, event):

            save_benchmarks("FAILED")


def save_benchmarks(status):

    with lock:

        if BENCHMARK_FILE.exists():

            data = json.loads(
                BENCHMARK_FILE.read_text(encoding="utf-8")
            )

        else:
            data = {}

        data["agent_execution_metrics"] = list(agent_metrics)

        data["task_execution_metrics"] = list(task_metrics)

        data.setdefault("manager", {})

        data["manager"]["observed_task_assignments"] = list(
            routing_history
        )

        data.setdefault("execution", {})

        data["execution"]["crew_event_status"] = status

        BENCHMARK_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        BENCHMARK_FILE.write_text(
            json.dumps(data, indent=4),
            encoding="utf-8"
        )

        print("\nExecution tracking benchmarks saved.")


execution_tracker = ExecutionTracker()