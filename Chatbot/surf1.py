'''
    This is the entry point for the CLI
'''

import argparse
from surfline import search, spotSuggestion, createForecast


def main():
    args = parseArgs()
    getForecast(args.spot, args.timeframe)


def parseArgs():
    # Parse args passed to the cli
    parser = argparse.ArgumentParser(description="Get a surf forecast! Enter when and where you want to surf.")
    parser.add_argument('timeframe', help='when do you want to go surfing - today, tomorrow, weekend or forecast')
    parser.add_argument('spot', help='where do you want to surf')

    return parser.parse_args()


def getForecast(spot, forecastType):
    searchSpots = search(spot)
    hits = searchSpots[0]["hits"]["hits"]

    if len(hits) == 1:
        # Pull out the spot id for the single hit
        spotId = hits[0]["_id"]
        duh = createForecast(spotId, forecastType)
        if duh["optimalScore"] == 0:
            return ("The surf height's " + str(duh["min"]) + "-" + str(duh["max"]) + " Ft. You shouldn't go.")
        if duh["optimalScore"] == 1:
            return ("The surf height's' " + str(duh["min"]) + "-" + str(duh["max"]) + " Ft. You should consider going.")
        if duh["optimalScore"] == 2:
            return ("The surf height's " + str(duh["min"]) + "-" + str(duh["max"]) + " Ft. You should send it. ")

    elif len(hits) > 1:
        # The user has received multiple spot suggestions, they'll need to narrow down the spot they want
        for i in hits:
            if str(i["_source"]["name"]).lower() == str(spot).lower():
                spotId = hits[0]["_id"]
                duh = createForecast(spotId, forecastType)
                if duh["optimalScore"] == 0:
                    return ("The surf height's " + str(duh["min"]) + "-" + str(duh["max"]) + " Ft. You shouldn't go.")
                if duh["optimalScore"] == 1:
                    return ("The surf height's' " + str(duh["min"]) + "-" + str(
                        duh["max"]) + " Ft. You should consider going.")
                if duh["optimalScore"] == 2:
                    return ("The surf height's " + str(duh["min"]) + "-" + str(
                        duh["max"]) + " Ft. You should send it. ")
        return str(spotSuggestion(searchSpots))

    else:
        return ("Couldn't find that spot")


if __name__ == '__main__':
    main()