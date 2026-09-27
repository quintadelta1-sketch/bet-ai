def probability_over(value, line):
    if line <= 0:
        return 0

    probability = (value / line) * 50

    if probability > 95:
        probability = 95

    return round(probability, 2)


def probability_under(value, line):
    if line <= 0:
        return 0

    probability = 100 - ((value / line) * 50)

    if probability < 5:
        probability = 5

    return round(probability, 2)


def calculate_probabilities(stats, lines=None):

    if lines is None:
        lines = {
            "goals": 2.5,
            "corners": 9.5,
            "shots": 20.5,
            "shots_on_target": 7.5,
            "tackles": 25.5,
            "cards": 4.5,
            "fouls": 24.5
        }

    probabilities = {}

    for market, values in stats.items():

        if market not in lines:
            continue

        line = lines[market]

        total = values["home"] + values["away"]

        probabilities[market] = {
            "line": line,
            "total_expected": round(total, 2),
            "over": probability_over(total, line),
            "under": probability_under(total, line)
        }

    return probabilities
