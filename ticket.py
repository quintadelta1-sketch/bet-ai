def generate_ticket(results, minimum_probability=60):
    selections = []

    for result in results:
        if result["home_probability"] >= minimum_probability:
            selections.append({
                "game": f'{result["home"]} x {result["away"]}',
                "selection": f'Vitória {result["home"]}',
                "probability": result["home_probability"]
            })

        elif result["away_probability"] >= minimum_probability:
            selections.append({
                "game": f'{result["home"]} x {result["away"]}',
                "selection": f'Vitória {result["away"]}',
                "probability": result["away_probability"]
            })

    return selections
