from crew.agents import researcher, analyst, writer


print("\n========== AGENT VERIFICATION ==========\n")

agents = [researcher, analyst, writer]

for agent in agents:

    print("Role:", agent.role)
    print("Goal:", agent.goal)
    print("Backstory:", agent.backstory[:100] + "...")
    print("----------------------------------------")

print("\nSUCCESS: All three agents created!")