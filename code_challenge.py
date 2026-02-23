"""
BlackRoad Code Challenge Platform
Coding challenge platform with multi-language test runner and leaderboard.
"""

import json
import math
import os
import random
import subprocess
import tempfile
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    BASH = "bash"


class SubmissionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    RUNTIME_ERROR = "runtime_error"
    TIME_LIMIT = "time_limit"
    COMPILE_ERROR = "compile_error"


# ---------------------------------------------------------------------------
# Test Case & Challenge
# ---------------------------------------------------------------------------

@dataclass
class TestCase:
    """A single input/expected-output test case."""
    test_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    input_data: str = ""
    expected_output: str = ""
    is_hidden: bool = False
    weight: int = 1     # scoring weight
    description: str = ""

    def to_dict(self, reveal: bool = False) -> dict:
        d = {
            "id": self.test_id,
            "is_hidden": self.is_hidden,
            "weight": self.weight,
            "description": self.description,
        }
        if not self.is_hidden or reveal:
            d["input"] = self.input_data
            d["expected"] = self.expected_output
        return d


@dataclass
class Challenge:
    """A coding challenge."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:10])
    title: str = ""
    description: str = ""
    difficulty: Difficulty = Difficulty.MEDIUM
    examples: List[Dict[str, str]] = field(default_factory=list)   # [{"input": ..., "output": ...}]
    test_cases: List[TestCase] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    hints: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    languages: List[Language] = field(default_factory=lambda: list(Language))
    time_limit_ms: int = 2000
    memory_limit_mb: int = 128
    starter_code: Dict[str, str] = field(default_factory=dict)   # lang → code stub
    solution_code: Dict[str, str] = field(default_factory=dict)  # lang → reference solution
    points: int = 100
    created_at: float = field(default_factory=time.time)

    def to_dict(self, reveal_cases: bool = False) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "difficulty": self.difficulty.value,
            "examples": self.examples,
            "test_cases": [tc.to_dict(reveal=reveal_cases) for tc in self.test_cases if not tc.is_hidden or reveal_cases],
            "constraints": self.constraints,
            "hints": self.hints,
            "tags": self.tags,
            "languages": [l.value for l in self.languages],
            "time_limit_ms": self.time_limit_ms,
            "memory_limit_mb": self.memory_limit_mb,
            "points": self.points,
        }

    def get_public_test_cases(self) -> List[TestCase]:
        return [tc for tc in self.test_cases if not tc.is_hidden]

    def get_all_test_cases(self) -> List[TestCase]:
        return self.test_cases


# ---------------------------------------------------------------------------
# Submission
# ---------------------------------------------------------------------------

@dataclass
class TestResult:
    test_id: str
    passed: bool
    input_data: str
    expected: str
    actual: str
    error: str = ""
    time_ms: float = 0.0
    is_hidden: bool = False

    def to_dict(self) -> dict:
        return {
            "test_id": self.test_id,
            "passed": self.passed,
            "input": self.input_data if not self.is_hidden else "[hidden]",
            "expected": self.expected if not self.is_hidden else "[hidden]",
            "actual": self.actual if not self.is_hidden else ("[correct]" if self.passed else "[wrong]"),
            "error": self.error,
            "time_ms": round(self.time_ms, 2),
        }


@dataclass
class Submission:
    """A user's code submission."""
    submission_id: str = field(default_factory=lambda: str(uuid.uuid4())[:10])
    challenge_id: str = ""
    user_id: str = ""
    language: Language = Language.PYTHON
    code: str = ""
    status: SubmissionStatus = SubmissionStatus.PENDING
    test_results: List[TestResult] = field(default_factory=list)
    score: int = 0
    time_ms: float = 0.0
    submitted_at: float = field(default_factory=time.time)
    graded_at: Optional[float] = None

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.test_results if r.passed)

    @property
    def total_count(self) -> int:
        return len(self.test_results)

    @property
    def pass_rate(self) -> float:
        if not self.test_results:
            return 0.0
        return self.passed_count / self.total_count

    def to_dict(self) -> dict:
        return {
            "id": self.submission_id,
            "challenge_id": self.challenge_id,
            "user_id": self.user_id,
            "language": self.language.value,
            "status": self.status.value,
            "score": self.score,
            "passed": f"{self.passed_count}/{self.total_count}",
            "time_ms": round(self.time_ms, 2),
            "submitted_at": self.submitted_at,
            "test_results": [r.to_dict() for r in self.test_results],
        }


# ---------------------------------------------------------------------------
# Test Runner
# ---------------------------------------------------------------------------

class CodeRunner:
    """Executes code in a subprocess with timeout."""

    TIMEOUT_SECONDS = 5

    def run_python(self, code: str, input_data: str, timeout_ms: int = 2000) -> Tuple[str, str, float]:
        """Run Python code. Returns (stdout, stderr, elapsed_ms)."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            tmppath = f.name
        try:
            start = time.perf_counter()
            result = subprocess.run(
                ["python3", tmppath],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=min(timeout_ms / 1000.0, self.TIMEOUT_SECONDS),
            )
            elapsed = (time.perf_counter() - start) * 1000
            return result.stdout.rstrip("\n"), result.stderr, elapsed
        except subprocess.TimeoutExpired:
            return "", "TIMEOUT", timeout_ms * 1.0
        except Exception as e:
            return "", str(e), 0.0
        finally:
            os.unlink(tmppath)

    def run_javascript(self, code: str, input_data: str, timeout_ms: int = 2000) -> Tuple[str, str, float]:
        """Run JavaScript code via node."""
        wrapped = f"const lines = `{input_data}`.trim().split('\\n'); let idx=0; const readline=()=>lines[idx++]||'';\n{code}"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write(wrapped)
            tmppath = f.name
        try:
            start = time.perf_counter()
            result = subprocess.run(
                ["node", tmppath],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=min(timeout_ms / 1000.0, self.TIMEOUT_SECONDS),
            )
            elapsed = (time.perf_counter() - start) * 1000
            return result.stdout.rstrip("\n"), result.stderr, elapsed
        except subprocess.TimeoutExpired:
            return "", "TIMEOUT", timeout_ms * 1.0
        except FileNotFoundError:
            return "", "node not found", 0.0
        except Exception as e:
            return "", str(e), 0.0
        finally:
            os.unlink(tmppath)

    def run_bash(self, code: str, input_data: str, timeout_ms: int = 2000) -> Tuple[str, str, float]:
        """Run bash code."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
            f.write("#!/bin/bash\n" + code)
            tmppath = f.name
        os.chmod(tmppath, 0o755)
        try:
            start = time.perf_counter()
            result = subprocess.run(
                ["bash", tmppath],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=min(timeout_ms / 1000.0, self.TIMEOUT_SECONDS),
            )
            elapsed = (time.perf_counter() - start) * 1000
            return result.stdout.rstrip("\n"), result.stderr, elapsed
        except subprocess.TimeoutExpired:
            return "", "TIMEOUT", timeout_ms * 1.0
        except Exception as e:
            return "", str(e), 0.0
        finally:
            os.unlink(tmppath)

    def execute(self, language: Language, code: str, input_data: str, timeout_ms: int) -> Tuple[str, str, float]:
        if language == Language.PYTHON:
            return self.run_python(code, input_data, timeout_ms)
        elif language == Language.JAVASCRIPT:
            return self.run_javascript(code, input_data, timeout_ms)
        elif language == Language.BASH:
            return self.run_bash(code, input_data, timeout_ms)
        return "", "Unsupported language", 0.0


def run_tests(code: str, language: Language, test_cases: List[TestCase], timeout_ms: int = 2000) -> List[TestResult]:
    """Run code against all test cases."""
    runner = CodeRunner()
    results = []
    for tc in test_cases:
        stdout, stderr, elapsed = runner.execute(language, code, tc.input_data, timeout_ms)
        if stderr == "TIMEOUT":
            results.append(TestResult(
                test_id=tc.test_id,
                passed=False,
                input_data=tc.input_data,
                expected=tc.expected_output,
                actual="",
                error="Time limit exceeded",
                time_ms=elapsed,
                is_hidden=tc.is_hidden,
            ))
        elif stderr:
            results.append(TestResult(
                test_id=tc.test_id,
                passed=False,
                input_data=tc.input_data,
                expected=tc.expected_output,
                actual="",
                error=stderr[:200],
                time_ms=elapsed,
                is_hidden=tc.is_hidden,
            ))
        else:
            passed = stdout.strip() == tc.expected_output.strip()
            results.append(TestResult(
                test_id=tc.test_id,
                passed=passed,
                input_data=tc.input_data,
                expected=tc.expected_output,
                actual=stdout,
                time_ms=elapsed,
                is_hidden=tc.is_hidden,
            ))
    return results


# ---------------------------------------------------------------------------
# Grader
# ---------------------------------------------------------------------------

def grade_submission(submission: Submission, challenge: Challenge) -> Submission:
    """Grade a submission against all test cases."""
    if not submission.test_results:
        return submission

    submission.graded_at = time.time()
    passed = sum(r.passed for r in submission.test_results)
    total = len(submission.test_results)

    # Weighted score
    total_weight = sum(tc.weight for tc in challenge.test_cases)
    earned_weight = sum(
        tc.weight for tc, r in zip(challenge.test_cases, submission.test_results)
        if r.passed
    )
    score_ratio = earned_weight / total_weight if total_weight > 0 else 0
    submission.score = int(challenge.points * score_ratio)

    # Determine status
    if any(r.error == "Time limit exceeded" for r in submission.test_results):
        submission.status = SubmissionStatus.TIME_LIMIT
    elif any(r.error and "TIMEOUT" not in r.error for r in submission.test_results):
        submission.status = SubmissionStatus.RUNTIME_ERROR
    elif passed == total:
        submission.status = SubmissionStatus.ACCEPTED
    else:
        submission.status = SubmissionStatus.WRONG_ANSWER

    return submission


# ---------------------------------------------------------------------------
# Challenge Platform
# ---------------------------------------------------------------------------

class CodeChallengePlatform:
    """Main coding challenge platform."""

    def __init__(self):
        self._challenges: Dict[str, Challenge] = {}
        self._submissions: Dict[str, Submission] = {}
        self._runner = CodeRunner()

    # ------------------------------------------------------------------
    # Challenge management
    # ------------------------------------------------------------------

    def add_challenge(self, challenge: Challenge) -> Challenge:
        self._challenges[challenge.id] = challenge
        return challenge

    def get_challenge(self, challenge_id: str) -> Optional[Challenge]:
        return self._challenges.get(challenge_id)

    def list_challenges(
        self,
        difficulty: Optional[Difficulty] = None,
        tags: Optional[List[str]] = None,
        language: Optional[Language] = None,
    ) -> List[Challenge]:
        ch = list(self._challenges.values())
        if difficulty:
            ch = [c for c in ch if c.difficulty == difficulty]
        if tags:
            ch = [c for c in ch if any(t in c.tags for t in tags)]
        if language:
            ch = [c for c in ch if language in c.languages]
        return sorted(ch, key=lambda c: c.difficulty.value)

    # ------------------------------------------------------------------
    # Submission flow
    # ------------------------------------------------------------------

    def submit_solution(
        self,
        challenge_id: str,
        user_id: str,
        language: Language,
        code: str,
    ) -> Submission:
        """Submit code, run tests, grade, return submission."""
        submission = Submission(
            challenge_id=challenge_id,
            user_id=user_id,
            language=language,
            code=code,
            status=SubmissionStatus.RUNNING,
        )

        challenge = self.get_challenge(challenge_id)
        if not challenge:
            submission.status = SubmissionStatus.COMPILE_ERROR
            self._submissions[submission.submission_id] = submission
            return submission

        # Run tests
        test_cases = challenge.get_all_test_cases()
        start = time.perf_counter()
        results = run_tests(code, language, test_cases, challenge.time_limit_ms)
        submission.time_ms = (time.perf_counter() - start) * 1000
        submission.test_results = results

        # Grade
        grade_submission(submission, challenge)
        self._submissions[submission.submission_id] = submission
        return submission

    def get_submission(self, submission_id: str) -> Optional[Submission]:
        return self._submissions.get(submission_id)

    def get_user_submissions(self, user_id: str, challenge_id: Optional[str] = None) -> List[Submission]:
        subs = [s for s in self._submissions.values() if s.user_id == user_id]
        if challenge_id:
            subs = [s for s in subs if s.challenge_id == challenge_id]
        return sorted(subs, key=lambda s: s.submitted_at, reverse=True)

    def get_best_submission(self, user_id: str, challenge_id: str) -> Optional[Submission]:
        subs = [s for s in self.get_user_submissions(user_id, challenge_id)
                if s.status == SubmissionStatus.ACCEPTED]
        if not subs:
            subs = self.get_user_submissions(user_id, challenge_id)
        if not subs:
            return None
        return max(subs, key=lambda s: s.score)

    # ------------------------------------------------------------------
    # Leaderboard
    # ------------------------------------------------------------------

    def get_leaderboard(self, challenge_id: str, limit: int = 10) -> List[dict]:
        best_by_user: Dict[str, Submission] = {}
        for sub in self._submissions.values():
            if sub.challenge_id != challenge_id:
                continue
            uid = sub.user_id
            if uid not in best_by_user or sub.score > best_by_user[uid].score:
                best_by_user[uid] = sub
        ranked = sorted(best_by_user.values(), key=lambda s: (-s.score, s.time_ms))
        return [
            {
                "rank": i + 1,
                "user_id": sub.user_id,
                "score": sub.score,
                "status": sub.status.value,
                "language": sub.language.value,
                "time_ms": round(sub.time_ms, 2),
                "pass_rate": f"{sub.passed_count}/{sub.total_count}",
            }
            for i, sub in enumerate(ranked[:limit])
        ]

    def get_global_leaderboard(self, limit: int = 10) -> List[dict]:
        """Aggregate scores across all challenges."""
        user_scores: Dict[str, int] = {}
        user_solved: Dict[str, int] = {}
        for sub in self._submissions.values():
            uid = sub.user_id
            if sub.status == SubmissionStatus.ACCEPTED:
                user_scores[uid] = user_scores.get(uid, 0) + sub.score
                user_solved[uid] = user_solved.get(uid, 0) + 1
        ranked = sorted(user_scores.items(), key=lambda x: -x[1])
        return [
            {"rank": i + 1, "user_id": uid, "total_score": score, "solved": user_solved.get(uid, 0)}
            for i, (uid, score) in enumerate(ranked[:limit])
        ]

    # ------------------------------------------------------------------
    # Explanation
    # ------------------------------------------------------------------

    def generate_explanation(self, challenge_id: str) -> str:
        """Generate a step-by-step explanation for a challenge."""
        challenge = self.get_challenge(challenge_id)
        if not challenge:
            return "Challenge not found."
        lines = [
            f"## {challenge.title}",
            f"**Difficulty:** {challenge.difficulty.value}",
            f"**Points:** {challenge.points}",
            "",
            "### Problem",
            challenge.description,
            "",
        ]
        if challenge.constraints:
            lines += ["### Constraints"] + [f"- {c}" for c in challenge.constraints] + [""]
        if challenge.examples:
            lines.append("### Examples")
            for i, ex in enumerate(challenge.examples, 1):
                lines.append(f"**Example {i}:**")
                lines.append(f"- Input: `{ex.get('input', '')}`")
                lines.append(f"- Output: `{ex.get('output', '')}`")
                if "explanation" in ex:
                    lines.append(f"- Explanation: {ex['explanation']}")
            lines.append("")
        if challenge.hints:
            lines += ["### Hints"] + [f"{i+1}. {h}" for i, h in enumerate(challenge.hints)] + [""]
        lines += ["### Approach", "1. Read and parse the input carefully.",
                  "2. Identify edge cases from the constraints.",
                  "3. Consider time and space complexity.",
                  "4. Test with provided examples before submitting."]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def platform_stats(self) -> dict:
        total = len(self._submissions)
        accepted = sum(1 for s in self._submissions.values() if s.status == SubmissionStatus.ACCEPTED)
        return {
            "challenges": len(self._challenges),
            "submissions": total,
            "accepted": accepted,
            "acceptance_rate": round(accepted / total * 100, 1) if total else 0,
            "users": len(set(s.user_id for s in self._submissions.values())),
        }


# ---------------------------------------------------------------------------
# Sample challenges
# ---------------------------------------------------------------------------

def make_two_sum_challenge() -> Challenge:
    """Two Sum challenge."""
    ch = Challenge(
        title="Two Sum",
        description=(
            "Given an array of integers `nums` and an integer `target`, return the indices "
            "of the two numbers such that they add up to `target`.\n\n"
            "Input: first line is N, second line is N space-separated integers, third line is target.\n"
            "Output: two space-separated indices (0-based), smaller index first."
        ),
        difficulty=Difficulty.EASY,
        constraints=["2 ≤ N ≤ 10^4", "-10^9 ≤ nums[i] ≤ 10^9", "Exactly one solution exists"],
        hints=["Use a hash map to store seen values.", "O(n) solution exists."],
        tags=["array", "hash-map"],
        points=100,
        examples=[{"input": "4\n2 7 11 15\n9", "output": "0 1", "explanation": "nums[0]+nums[1]=9"}],
    )
    ch.test_cases = [
        TestCase(input_data="4\n2 7 11 15\n9", expected_output="0 1"),
        TestCase(input_data="3\n3 2 4\n6", expected_output="1 2"),
        TestCase(input_data="2\n3 3\n6", expected_output="0 1"),
        TestCase(input_data="5\n1 5 3 7 2\n8", expected_output="1 3", is_hidden=True),
        TestCase(input_data="6\n-1 -2 -3 -4 -5 -6\n-7", expected_output="1 4", is_hidden=True),
    ]
    ch.starter_code[Language.PYTHON] = (
        "n = int(input())\nnums = list(map(int, input().split()))\ntarget = int(input())\n"
        "# Your solution here\n"
    )
    ch.solution_code[Language.PYTHON] = (
        "n = int(input())\nnums = list(map(int, input().split()))\ntarget = int(input())\n"
        "seen = {}\n"
        "for i, v in enumerate(nums):\n"
        "    complement = target - v\n"
        "    if complement in seen:\n"
        "        a, b = sorted([seen[complement], i])\n"
        "        print(a, b)\n"
        "        break\n"
        "    seen[v] = i\n"
    )
    return ch


def make_fizzbuzz_challenge() -> Challenge:
    """FizzBuzz challenge."""
    ch = Challenge(
        title="FizzBuzz",
        description=(
            "Print numbers from 1 to N. For multiples of 3, print 'Fizz'. "
            "For multiples of 5, print 'Buzz'. For multiples of both, print 'FizzBuzz'."
        ),
        difficulty=Difficulty.EASY,
        constraints=["1 ≤ N ≤ 10^5"],
        tags=["math", "beginner"],
        points=50,
        examples=[{"input": "5", "output": "1\n2\nFizz\n4\nBuzz"}],
    )
    ch.test_cases = [
        TestCase(input_data="5",  expected_output="1\n2\nFizz\n4\nBuzz"),
        TestCase(input_data="15", expected_output="\n".join(
            "FizzBuzz" if i % 15 == 0 else "Fizz" if i % 3 == 0 else "Buzz" if i % 5 == 0 else str(i)
            for i in range(1, 16)
        )),
        TestCase(input_data="1",  expected_output="1", is_hidden=True),
    ]
    ch.starter_code[Language.PYTHON] = "n = int(input())\n# Your solution here\n"
    ch.solution_code[Language.PYTHON] = (
        "n = int(input())\n"
        "for i in range(1, n+1):\n"
        "    if i % 15 == 0: print('FizzBuzz')\n"
        "    elif i % 3 == 0: print('Fizz')\n"
        "    elif i % 5 == 0: print('Buzz')\n"
        "    else: print(i)\n"
    )
    return ch


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo():
    print("=== BlackRoad Code Challenge Platform Demo ===")
    platform = CodeChallengePlatform()

    # Add challenges
    fb = make_fizzbuzz_challenge()
    ts = make_two_sum_challenge()
    platform.add_challenge(fb)
    platform.add_challenge(ts)
    print(f"\nChallenges loaded: {len(platform._challenges)}")

    # List
    for ch in platform.list_challenges():
        print(f"  [{ch.difficulty.value}] {ch.title} — {len(ch.test_cases)} test cases, {ch.points}pts")

    # Run correct FizzBuzz
    print(f"\n[Submit correct FizzBuzz]")
    sub1 = platform.submit_solution(
        fb.id, "user_alice", Language.PYTHON,
        fb.solution_code[Language.PYTHON],
    )
    print(f"  Status: {sub1.status.value}, Score: {sub1.score}/{fb.points}, Tests: {sub1.passed_count}/{sub1.total_count}")

    # Run wrong FizzBuzz
    print(f"\n[Submit wrong FizzBuzz]")
    wrong_code = "n = int(input())\nfor i in range(1, n+1):\n    print(i)\n"
    sub2 = platform.submit_solution(fb.id, "user_bob", Language.PYTHON, wrong_code)
    print(f"  Status: {sub2.status.value}, Score: {sub2.score}/{fb.points}")
    for r in sub2.test_results[:2]:
        print(f"    {r.to_dict()}")

    # TwoSum
    print(f"\n[Submit TwoSum solution]")
    sub3 = platform.submit_solution(
        ts.id, "user_alice", Language.PYTHON,
        ts.solution_code[Language.PYTHON],
    )
    print(f"  Status: {sub3.status.value}, Score: {sub3.score}/{ts.points}, Tests: {sub3.passed_count}/{sub3.total_count}")

    # Leaderboard
    print(f"\n[FizzBuzz Leaderboard]")
    for entry in platform.get_leaderboard(fb.id):
        print(f"  #{entry['rank']} {entry['user_id']}: {entry['score']}pts ({entry['status']})")

    # Global leaderboard
    print(f"\n[Global Leaderboard]")
    for entry in platform.get_global_leaderboard():
        print(f"  #{entry['rank']} {entry['user_id']}: {entry['total_score']}pts, {entry['solved']} solved")

    # Explanation
    print(f"\n[TwoSum Explanation]")
    print(platform.generate_explanation(ts.id))

    # Stats
    print(f"\nPlatform stats: {platform.platform_stats()}")


if __name__ == "__main__":
    demo()
