"""Gate 5: targeted Crossref searches; raw JSON retained under data/physical/raw/crossref_search/."""
import datetime as dt
import hashlib
import json
import os
import time
import urllib.parse
import urllib.request

OUT = "data/physical/raw/crossref_search"
QUERIES = {
    "localized_heating_response": "thermosphere response localized heating neutral density simulation",
    "gitm_joule_heating_density": "GITM Joule heating thermospheric density response",
    "tad_gravity_waves": "traveling atmospheric disturbances thermosphere heating model",
    "storm_density_perturbation": "storm-time thermospheric density perturbation satellite drag model",
    "tiegcm_heating_experiment": "TIE-GCM simulation thermosphere heating density response experiment",
    "non_hydrostatic_heating": "non-hydrostatic thermosphere response sudden heating",
    "differential_drag": "differential drag satellite control thermosphere density",
    "debris_remediation_drag": "space debris removal atmospheric drag enhancement",
    "artificial_heating_neutral": "ionospheric heating experiment neutral atmosphere density effect",
    "drag_density_uncertainty": "satellite drag thermospheric density model uncertainty orbit prediction",
}


def main():
    os.makedirs(OUT, exist_ok=True)
    ledger = []
    for key, q in QUERIES.items():
        url = "https://api.crossref.org/works?" + urllib.parse.urlencode(
            {"query": q, "rows": 40, "select": "DOI,title,author,issued,container-title,type,is-referenced-by-count"})
        UA = "thermosphere-debris-selective-decay (mailto:bougtoir@gmail.com)"
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        raw = urllib.request.urlopen(req, timeout=60).read()
        path = os.path.join(OUT, f"{key}.json")
        if not os.path.exists(path):
            open(path, "wb").write(raw)
        n = len(json.loads(raw)["message"]["items"])
        ledger.append(dict(query_key=key, query=q, url=url, retrieved_utc=dt.datetime.utcnow().isoformat() + "Z",
                           path=path, bytes=os.path.getsize(path),
                           sha256=hashlib.sha256(open(path, "rb").read()).hexdigest(),
                           items=n, note="first page only (rows=40); relevance-ranked, not exhaustive"))
        time.sleep(1)
    json.dump(ledger, open(os.path.join(OUT, "ledger.json"), "w"), indent=1)
    print(len(ledger))


if __name__ == "__main__":
    main()
