from crew.financial_parser import financial_analysis_tool

print("\n========== CREWAI FINANCIAL TOOL TEST ==========\n")

result = financial_analysis_tool.run(
    file_path="data/sample_financial_data.csv"
)

print(result)