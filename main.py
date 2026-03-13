from dotenv import load_dotenv
load_dotenv()

from crew import run_crew


if __name__ == "__main__":
    prompt = input("Enter a stock ticker or describe a stock (e.g. 'Tell me about Tesla'): ").strip()

    if not prompt:
        print("\nNo input provided. Please enter a ticker or describe a stock.\n")
    else:
        try:
            run_crew(prompt)
        except Exception as e:
            print(f"\nUnexpected error: {e}\n")

