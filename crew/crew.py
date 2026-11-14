from crewai import Crew, Process

from config.llm_config import llm

from crew.agents import (
    researcher,
    analyst,
    writer
)

from crew.tasks import (
    research_task,
    analysis_task,
    writing_task
)


# ==========================================
# HIERARCHICAL MARKET RESEARCH CREW
# ==========================================

market_research_crew = Crew(

    agents=[
        researcher,
        analyst,
        writer
    ],

    tasks=[
        research_task,
        analysis_task,
        writing_task
    ],

    process=Process.hierarchical,

    # Automatically create the manager using Gemini
    manager_llm=llm,

    verbose=True,

    # Save execution logs
    output_log_file="benchmarks/execution.log"
)


print("Hierarchical Market Research Crew configured successfully!")