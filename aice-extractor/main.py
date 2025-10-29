"""
Main script to test job posting extraction with sample data
"""

from job_extractor import extract_job_posting
from sample_data import JOB_POSTING_1, JOB_POSTING_2, JOB_POSTING_3
import json


def main():
    """Test the job extractor with all sample data"""

    sample_jobs = [
        ("Sample 1 - Full Stack Developer", JOB_POSTING_1),
        ("Sample 2 - Data Scientist", JOB_POSTING_2),
        ("Sample 3 - Marketing Coordinator", JOB_POSTING_3),
    ]

    for title, job_text in sample_jobs:
        print(f"\n{title}")
        print("=" * 50)
        # print("Original text:")
        # print(job_text.strip())

        print("\nExtracted structured data:")
        print("-" * 30)

        try:
            job_posting = extract_job_posting(job_text)
            print(json.dumps(job_posting.model_dump(), indent=2))
        except Exception as e:
            print(f"Error extracting job posting: {e}")

        print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
