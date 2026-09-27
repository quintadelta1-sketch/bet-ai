def probability_over(value, line):
    if value <= 0:
        return 0

    probability = (value / line) * 50

    if probability > 95:
        probability = 95

    return round(probability, 2)


def probability_under(value, line):
    if value <= 0:
        return 95

    probability = 100 - ((value / line) * 50)

    if probability < 5:
        probability = 5

    return round(probability, 2)


def calculate_probabilities(stats):
    probabilities = {}

    for market, values in stats.items():

        if not isinstance(values, dict):
            continue

        probabilities[market] = {}

        for side, value in values.items():

            if isinstance(value, (int, float)):
                probabilities[market][side] = {
                    "over": probability_over(value, 1),
                    "under": probability_under(value, 1)
                }

    return probabilities
