from typing import List, Dict, Set, Tuple
from .codeforces_api import cf_api
import random


# Map difficulty to Codeforces divisions
# Difficulty 1 = Div 4, 2 = Div 3, 3 = Div 2, 4 = Div 1
DIFFICULTY_TO_DIVISION = {
    1: 4,
    2: 3,
    3: 2,
    4: 1
}

PROBLEM_INDICES = ['A', 'B', 'C', 'D', 'E', 'F']
POINTS_MAP = {
    'A': 100,
    'B': 200,
    'C': 300,
    'D': 400,
    'E': 500,
    'F': 600
}


async def get_unsolved_problems(
    handle1: str,
    handle2: str,
    difficulty: int
) -> List[Dict]:
    """
    Select 6 problems (A-F) from the target division that neither user has solved.
    Returns list of problem dicts with problem_index, problem_code, problem_url, points, division
    """
    division = DIFFICULTY_TO_DIVISION.get(difficulty, 3)
    
    # Get solved problems for both users
    solved1 = await cf_api.get_user_solved_problems(handle1)
    solved2 = await cf_api.get_user_solved_problems(handle2)
    solved_both = solved1.union(solved2)
    
    # Get all problems
    problems_data = await cf_api.get_problems()
    problems = problems_data.get("problems", [])
    problem_statistics = problems_data.get("problemStatistics", [])
    
    # Get contest list to build a cache of contest divisions
    print(f"Fetching contest list to determine divisions...")
    contests = await cf_api.get_contest_list()
    contest_division_map = {}
    
    # Build a map of contest_id -> division
    for contest in contests:
        contest_id = contest.get("id")
        if contest_id:
            name = contest.get("name", "").lower()
            # Check for Div. 1, Div. 2, Div. 3, Div. 4 patterns
            if "div. 1" in name or "div1" in name or "(div1)" in name:
                contest_division_map[contest_id] = 1
            elif "div. 2" in name or "div2" in name or "(div2)" in name:
                contest_division_map[contest_id] = 2
            elif "div. 3" in name or "div3" in name or "(div3)" in name:
                contest_division_map[contest_id] = 3
            elif "div. 4" in name or "div4" in name or "(div4)" in name:
                contest_division_map[contest_id] = 4
            # Educational rounds are typically Div 2
            elif "educational" in name:
                contest_division_map[contest_id] = 2
    
    print(f"Found divisions for {len(contest_division_map)} contests")
    
    # Create a map of problem code to problem info
    problem_map = {}
    for i, problem in enumerate(problems):
        contest_id = problem.get("contestId")
        index = problem.get("index")
        if contest_id and index:
            code = f"{contest_id}{index}"
            problem_map[code] = {
                "problem": problem,
                "statistics": problem_statistics[i] if i < len(problem_statistics) else {},
                "contest_id": contest_id
            }
    
    # Filter problems by actual contest division and index
    # Use per-index rating ranges as a secondary filter for better quality
    
    # Div 4 rating ranges per index (as fallback/quality filter)
    div4_ranges = {
        'A': (800, 900),
        'B': (900, 1100),
        'C': (1100, 1300),
        'D': (1300, 1500),
        'E': (1500, 1700),
        'F': (1700, 1900)
    }
    
    # Div 3 rating ranges per index
    div3_ranges = {
        'A': (800, 1000),
        'B': (1000, 1200),
        'C': (1200, 1400),
        'D': (1400, 1600),
        'E': (1600, 1800),
        'F': (1800, 2000)
    }
    
    # Div 2 rating ranges per index
    div2_ranges = {
        'A': (800, 1200),
        'B': (1200, 1500),
        'C': (1500, 1800),
        'D': (1800, 2100),
        'E': (2100, 2400),
        'F': (2400, 2700)
    }
    
    # Div 1 rating ranges per index
    div1_ranges = {
        'A': (1500, 1800),
        'B': (1800, 2100),
        'C': (2100, 2400),
        'D': (2400, 2700),
        'E': (2700, 3000),
        'F': (3000, 3500)
    }
    
    division_ranges = {
        4: div4_ranges,
        3: div3_ranges,
        2: div2_ranges,
        1: div1_ranges
    }
    
    rating_ranges = division_ranges.get(division, div3_ranges)
    
    # Group problems by index and filter by actual contest division
    problems_by_index = {idx: [] for idx in PROBLEM_INDICES}
    
    for code, data in problem_map.items():
        if code in solved_both:
            continue
        
        problem = data["problem"]
        contest_id = data["contest_id"]
        index = problem.get("index")
        rating = problem.get("rating")
        
        # Skip if index not in our list
        if index not in PROBLEM_INDICES:
            continue
        
        # PRIMARY FILTER: Check actual contest division
        contest_division = contest_division_map.get(contest_id)
        
        # Only include if contest division matches target division
        if contest_division != division:
            continue
        
        # SECONDARY FILTER: Use rating range as quality filter (optional but helps)
        # This ensures we get problems of appropriate difficulty for the index
        min_rating, max_rating = rating_ranges.get(index, (800, 2000))
        
        # If rating is available, prefer problems within the expected range
        # But don't exclude if rating is missing (some problems don't have ratings)
        if rating and (rating < min_rating or rating > max_rating):
            # Still include but with lower priority (we'll sort later)
            pass
        
        problems_by_index[index].append({
            "contest_id": contest_id,
            "index": index,
            "code": code,
            "rating": rating or 0,
            "name": problem.get("name", ""),
            "tags": problem.get("tags", []),
            "in_rating_range": rating and min_rating <= rating <= max_rating if rating else True
        })
    
    # Select one problem per index
    selected_problems = []
    for idx in PROBLEM_INDICES:
        candidates = problems_by_index.get(idx, [])
        if candidates:
            # Prefer problems within rating range, then randomly select
            in_range = [c for c in candidates if c.get("in_rating_range", True)]
            if in_range:
                selected = random.choice(in_range)
            else:
                # If none in range, use any from the division
                selected = random.choice(candidates)
            
            contest_id = selected["contest_id"]
            index = selected["index"]
            selected_problems.append({
                "problem_index": index,
                "problem_code": selected["code"],
                "problem_url": f"https://codeforces.com/problemset/problem/{contest_id}/{index}",
                "points": POINTS_MAP[index],
                "division": division,
                "contest_id": contest_id
            })
        else:
            # Fallback: if no problems found from exact division, try to find from any division
            # but still matching the index (should rarely happen)
            print(f"Warning: No problems found for {idx} in division {division}, trying fallback...")
            fallback_candidates = []
            for code, data in problem_map.items():
                if code in solved_both:
                    continue
                problem = data["problem"]
                contest_id = data["contest_id"]
                if problem.get("index") == idx:
                    # Try to get contest division
                    contest_div = contest_division_map.get(contest_id)
                    # Prefer problems from the target division, but accept any if needed
                    fallback_candidates.append({
                        "contest_id": contest_id,
                        "index": idx,
                        "code": code,
                        "rating": problem.get("rating") or 0,
                        "contest_division": contest_div
                    })
            
            if fallback_candidates:
                # Prefer problems from target division, then by rating
                fallback_candidates.sort(key=lambda x: (
                    0 if x["contest_division"] == division else 1,
                    abs(x["rating"] - (rating_ranges.get(idx, (1000, 1500))[0] + rating_ranges.get(idx, (1000, 1500))[1]) / 2)
                ))
                selected = fallback_candidates[0]
                print(f"  Using fallback: {selected['code']} from division {selected['contest_division']}")
                selected_problems.append({
                    "problem_index": selected["index"],
                    "problem_code": selected["code"],
                    "problem_url": f"https://codeforces.com/problemset/problem/{selected['contest_id']}/{selected['index']}",
                    "points": POINTS_MAP[selected["index"]],
                    "division": division,
                    "contest_id": selected["contest_id"]
                })
            else:
                print(f"  Error: No fallback problem found for {idx}")
    
    return selected_problems[:6]
