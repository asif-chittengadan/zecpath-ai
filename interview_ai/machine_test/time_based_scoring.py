class TimeBasedScoring:
    def __init__(self, bonus_rate=0.0, penalty_rate=0.0):
        for name, value in {
            "bonus_rate": bonus_rate,
            "penalty_rate": penalty_rate,
        }.items():
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not 0 <= value <= 1
            ):
                raise ValueError(f"{name} must be between 0 and 1")

        self.bonus_rate = bonus_rate
        self.penalty_rate = penalty_rate

    def calculate(self, base_score, time_limit_minutes, time_taken_minutes):
        for name, value in {
            "base_score": base_score,
            "time_limit_minutes": time_limit_minutes,
            "time_taken_minutes": time_taken_minutes,
        }.items():
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or value < 0
            ):
                raise ValueError(f"{name} must be non-negative")

        if base_score > 100:
            raise ValueError("base_score cannot exceed 100")

        if time_limit_minutes <= 0:
            raise ValueError("time_limit_minutes must be positive")

        if time_taken_minutes == 0:
            raise ValueError("time_taken_minutes must be positive")

        if time_taken_minutes <= time_limit_minutes:
            remaining_ratio = (
                time_limit_minutes - time_taken_minutes
            ) / time_limit_minutes

            bonus = (
                base_score * self.bonus_rate * remaining_ratio
            )
            penalty = 0
        else:
            overtime_ratio = (
                time_taken_minutes - time_limit_minutes
            ) / time_limit_minutes

            bonus = 0
            penalty = (
                base_score
                * self.penalty_rate
                * min(overtime_ratio, 1.0)
            )

        final_score = max(
            0,
            min(100, base_score + bonus - penalty),
        )

        return {
            "base_score": round(base_score, 2),
            "time_limit_minutes": time_limit_minutes,
            "time_taken_minutes": time_taken_minutes,
            "time_bonus": round(bonus, 2),
            "time_penalty": round(penalty, 2),
            "final_score": round(final_score, 2),
        }