from concurrent.futures import ThreadPoolExecutor
import sys
import os
import json
from .mediagraph import Mediagraph

def main(shoot_numbers, api_token, org_number):
    m = Mediagraph(api_token, org_number)
    return {shoot:data for shoot, data in ThreadPoolExecutor(max_workers=10).map(m.get_shoot_data, stripped_lines(shoot_numbers))}


def stripped_lines(lines):
    return (line.strip() for line in lines)

if __name__ == "__main__":
    results = main(sys.stdin.readlines(), os.getenv("MEDIAGRAPH_TOKEN"), os.getenv("MEDIAGRAPH_ORG"))
    good_results = {k:v for k,v in results.items() if isinstance(v, dict)}
    print(json.dumps(good_results, indent=2))
    if good_results != results:
        print({k:v for k,v in results.items() if isinstance(v, Exception)} ,file=sys.stderr)
        raise Exception("some shoots were not right")
