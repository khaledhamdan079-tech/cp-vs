"""
Elo rating system implementation for CP VS contests.
"""


def calculate_elo_rating(rating1: int, rating2: int, score1: float, score2: float, k_factor: int = 32) -> tuple:
    """
    Calculate new ratings using Elo system.
    
    Args:
        rating1: Current rating of user 1
        rating2: Current rating of user 2
        score1: Score for user 1 (1.0 for win, 0.5 for draw, 0.0 for loss)
        score2: Score for user 2 (1.0 for win, 0.5 for draw, 0.0 for loss)
        k_factor: K-factor for rating changes (default 32)
    
    Returns:
        Tuple of (new_rating1, new_rating2, rating_change1, rating_change2)
    """
    # Calculate expected scores
    expected1 = 1 / (1 + 10 ** ((rating2 - rating1) / 400))
    expected2 = 1 / (1 + 10 ** ((rating1 - rating2) / 400))
    
    # Calculate new ratings
    new_rating1 = rating1 + k_factor * (score1 - expected1)
    new_rating2 = rating2 + k_factor * (score2 - expected2)
    
    # Round to integers
    new_rating1 = int(round(new_rating1))
    new_rating2 = int(round(new_rating2))
    
    # Calculate rating changes
    rating_change1 = new_rating1 - rating1
    rating_change2 = new_rating2 - rating2
    
    return (new_rating1, new_rating2, rating_change1, rating_change2)


def determine_contest_scores(points1: int, points2: int) -> tuple:
    """
    Determine Elo scores based on contest points.
    
    Args:
        points1: Total points scored by user 1
        points2: Total points scored by user 2
    
    Returns:
        Tuple of (score1, score2) for Elo calculation
        - (1.0, 0.0) if user1 wins
        - (0.0, 1.0) if user2 wins
        - (0.5, 0.5) if draw
    """
    if points1 > points2:
        return (1.0, 0.0)
    elif points2 > points1:
        return (0.0, 1.0)
    else:
        return (0.5, 0.5)
