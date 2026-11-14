from crew.financial_parser import analyze_financial_data


print("\n========== FINANCIAL ANALYSIS ==========\n")

result = analyze_financial_data(
    "data/sample_financial_data.csv"
)

if result["status"] == "success":

    print("Total Companies:", result["total_companies"])

    print("\nFINANCIAL STATISTICS:")

    for column, values in result["statistics"].items():

        print(f"\n{column}")

        for metric, value in values.items():
            print(f"{metric}: {value:.2f}")

    print("\nMARKDOWN TABLE:")
    print(result["markdown_table"])

else:
    print("Analysis failed:", result["message"])