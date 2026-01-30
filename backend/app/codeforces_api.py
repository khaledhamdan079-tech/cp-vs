import httpx
from typing import List, Dict, Optional
from .config import settings
import asyncio


class CodeforcesAPI:
    def __init__(self):
        self.base_url = settings.codeforces_api_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def _make_request(self, method: str, params: Optional[Dict] = None) -> Dict:
        """Make a request to Codeforces API with rate limiting"""
        url = f"{self.base_url}/{method}"
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if data["status"] == "OK":
                return data["result"]
            else:
                raise Exception(f"Codeforces API error: {data.get('comment', 'Unknown error')}")
        except httpx.HTTPError as e:
            raise Exception(f"HTTP error calling Codeforces API: {str(e)}")
        except Exception as e:
            raise Exception(f"Error calling Codeforces API: {str(e)}")

    async def get_user_submissions(self, handle: str) -> List[Dict]:
        """Get all submissions for a user"""
        params = {"handle": handle, "from": 1, "count": 10000}
        return await self._make_request("user.status", params)

    async def get_user_solved_problems(self, handle: str) -> set:
        """Get set of solved problem codes (e.g., {'1234A', '567B'})"""
        try:
            submissions = await self.get_user_submissions(handle)
            solved = set()
            for submission in submissions:
                if submission.get("verdict") == "OK":
                    problem = submission.get("problem", {})
                    contest_id = problem.get("contestId")
                    index = problem.get("index")
                    if contest_id and index:
                        solved.add(f"{contest_id}{index}")
            return solved
        except Exception as e:
            print(f"Error getting solved problems for {handle}: {e}")
            return set()

    async def get_problems(self) -> List[Dict]:
        """Get all problems from Codeforces"""
        return await self._make_request("problemset.problems")

    async def get_contest_list(self) -> List[Dict]:
        """Get list of all contests from Codeforces"""
        return await self._make_request("contest.list")

    async def get_contest_division(self, contest_id: int) -> Optional[int]:
        """
        Get the division of a contest by checking its name.
        Returns 1, 2, 3, 4, or None if division cannot be determined.
        """
        try:
            contests = await self.get_contest_list()
            for contest in contests:
                if contest.get("id") == contest_id:
                    name = contest.get("name", "").lower()
                    # Check for Div. 1, Div. 2, Div. 3, Div. 4 patterns
                    if "div. 1" in name or "div1" in name:
                        return 1
                    elif "div. 2" in name or "div2" in name:
                        return 2
                    elif "div. 3" in name or "div3" in name:
                        return 3
                    elif "div. 4" in name or "div4" in name:
                        return 4
                    # Educational rounds are typically Div 2
                    elif "educational" in name:
                        return 2
                    # If no division specified, return None
                    return None
            return None
        except Exception as e:
            print(f"Error getting contest division for {contest_id}: {e}")
            return None

    async def get_contest_problems(self, contest_id: int) -> List[Dict]:
        """Get problems from a specific contest"""
        params = {"contestId": contest_id}
        try:
            return await self._make_request("contest.standings", params)
        except Exception:
            return []

    async def get_user_info(self, handles: List[str]) -> List[Dict]:
        """Get user info for one or more handles"""
        params = {"handles": ";".join(handles)}
        return await self._make_request("user.info", params)

    async def validate_handle(self, handle: str) -> bool:
        """Validate if a Codeforces handle exists"""
        try:
            params = {"handles": handle}
            result = await self._make_request("user.info", params)
            # If we get a result and it's a list with at least one user, handle is valid
            return isinstance(result, list) and len(result) > 0
        except Exception as e:
            # If API returns error (e.g., handle not found), return False
            print(f"Error validating handle {handle}: {e}")
            return False

    async def check_submission(self, handle: str, problem_code: str, since: int) -> Optional[Dict]:
        """Check if user has solved a specific problem since a given timestamp"""
        try:
            submissions = await self.get_user_submissions(handle)
            for submission in submissions:
                if submission.get("creationTimeSeconds", 0) < since:
                    break
                if submission.get("verdict") == "OK":
                    problem = submission.get("problem", {})
                    contest_id = problem.get("contestId")
                    index = problem.get("index")
                    if contest_id and index:
                        code = f"{contest_id}{index}"
                        if code == problem_code:
                            return submission
            return None
        except Exception as e:
            print(f"Error checking submission for {handle}: {e}")
            return None

    async def close(self):
        await self.client.aclose()


# Global instance
cf_api = CodeforcesAPI()
