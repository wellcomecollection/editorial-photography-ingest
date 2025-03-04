import sys
import os
import json
from concurrent.futures import ThreadPoolExecutor

from tqdm import tqdm

from .mediagraph import Mediagraph


def main(shoot_collections, api_token, org_number):
    m = Mediagraph(api_token, org_number)
    def delete_collection(pair):
        return m.delete_collection(pair[0], pair[1]['collection'], pair[1]['assets'])
    return {
        shoot: {"success": success, "results": results}
        for shoot, success, results
        in tqdm(
            ThreadPoolExecutor(max_workers=5).map(delete_collection,shoot_collections.items()),
            total=len(shoot_collections)
        )
    }

if __name__ == "__main__":
    results = main(json.load(sys.stdin), os.getenv("MEDIAGRAPH_TOKEN"), os.getenv("MEDIAGRAPH_ORG"))
    bad_results = {k:v for k,v in results.items() if not v['success']}

    good_results = {k:v for k,v in results.items() if v['success']}
    print(json.dumps(good_results, indent=2))
    if bad_results:
        print(bad_results, file=sys.stderr)
        raise Exception("some shoots could not be deleted")
