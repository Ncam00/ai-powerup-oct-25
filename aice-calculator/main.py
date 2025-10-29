"""
Main script to test the calculator agent with various math problems
"""

from calculator_agent import solve_math_problem


def main():
    """Test the calculator agent with various math problems"""

    test_problems = [
        "What is 15 + 27?",
        "Calculate the square root of 144",
        "What is 23 + 4 / 2 * 3",
        "What is 5 factorial?",
        "What is 2 to the power of 8?",
        "What is 100 - 45?",
    ]

    print("Calculator Agent Test Suite")
    print("=" * 50)

    for i, problem in enumerate(test_problems, 1):
        print(f"\nTEST {i}/{len(test_problems)}")
        solve_math_problem(problem)
        print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
