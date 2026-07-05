import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.eval.evaluator import run_evaluation


def main():
    print("=" * 60)
    print("  VLM Document Extraction — Evaluation")
    print("=" * 60)
    print()

    result = run_evaluation()

    print(f"  Exact match:     {'YES' if result.exact_match else 'NO'}")
    print(f"  Field accuracy:  {result.field_accuracy * 100:.1f}%")
    print(f"  Latency:         {result.latency_ms:.1f}ms")
    print()

    if result.missing_fields:
        print(f"  Missing fields:  {', '.join(result.missing_fields)}")
    if result.extra_fields:
        print(f"  Extra fields:    {', '.join(result.extra_fields)}")
    if result.mismatched_fields:
        print(f"  Mismatched:")
        for field, vals in result.mismatched_fields.items():
            print(f"    {field}: expected='{vals['expected']}' got='{vals['got']}'")

    if result.exact_match:
        print()
        print("  All fields match ground truth!")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
