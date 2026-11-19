"""Gate 1B: build references/PRIOR_KNOWLEDGE_VERIFIED.csv.

Bibliographic fields come only from the retained Crossref records in
data/physical/raw/crossref/ (verified=crossref). Content fields are my reading
of the Crossref abstract (evidence_level=abstract) or of the title only
(evidence_level=title_only); no full texts were available offline, so
quantitative results are given only where the abstract states them.
"""
import csv
import json
import os

D = "data/physical/raw/crossref"
F = ["citation_key", "authors", "year", "title", "journal", "doi", "verified", "evidence_level",
     "research_domain", "model_used", "physical_process", "principal_result", "quantitative_result",
     "limitations", "relevance_to_current_study"]
A = [  # doi, key, domain, model, process, principal, quantitative, limitations, relevance, evidence
    ("10.1029/92GL00401", "richmond1992tiegcm", "B", "TIE-GCM", "coupled T-I electrodynamics",
     "Introduces NCAR TIE-GCM with self-consistent dynamo", "", "model description", "surveyed model", "abstract"),
    ("10.1002/9781118704417.ch7", "qian2014tiegcm", "B", "TIE-GCM", "model description",
     "Reference description of TIE-GCM", "", "", "surveyed model", "title_only"),
    ("10.1029/2025JA034219", "wu2025tiegcm3", "B", "TIE-GCM 3.0", "model description",
     "Higher resolution, raised upper boundary", "", "", "surveyed model (current version)", "abstract"),
    ("10.1016/j.jastp.2006.01.008", "ridley2006gitm", "B", "GITM", "non-hydrostatic I-T model",
     "Describes GITM", "", "", "selected model", "title_only"),
    ("10.1002/2017MS001232", "liu2018waccmx", "B", "WACCM-X 2.0", "whole-atmosphere model",
     "Self-consistent electrodynamics, O+ transport in WACCM-X", "", "", "surveyed model", "abstract"),
    ("10.1029/2002JA009430", "picone2002msis", "B", "NRLMSISE-00", "empirical climatology",
     "Empirical density/temperature model", "", "cannot respond to imposed heating", "empirical control", "abstract"),
    ("10.1029/2020EA001321", "emmert2021msis2", "B", "NRLMSIS 2.0", "empirical climatology",
     "Reformulated MSIS", "", "as above", "empirical control", "abstract"),
    ("10.2514/6.2008-6438", "bowman2008jb2008", "B", "JB2008", "empirical density", "Empirical density model", "",
     "as above", "empirical control", "title_only"),
    ("10.1029/2007GL032182", "deng2008nonhydro", "A", "GITM", "non-hydrostatic response to sudden heating",
     "Sudden intense high-latitude Joule heating breaks hydrostatic balance; disturbance transported away",
     "vertical pressure-gradient force locally up to 25% larger than gravity", "high-latitude Joule heating only",
     "establishes that localized strong heating needs a non-hydrostatic solver; prior for PR5", "abstract"),
    ("10.1002/2014JA020962", "liu2015substorm", "A/E", "GITM", "density response to idealized substorms",
     "Mass-density response to idealized substorm energy input; local-time dependence; slight nonlinearity",
     "50 GW HP peak with Bz=-2 nT -> max density perturbation ~14% about 50 min after onset (nightside auroral zone)",
     "auroral forcing (HP, IMF), not a compact prescribed source; no orbit coupling",
     "closest physical predecessor; prior for PR1-PR3", "abstract"),
    ("10.1029/2008JA013667", "sutton2009rapid", "A", "CHAMP observations", "response time to Joule heating",
     "Thermosphere responds faster than empirical-model lags",
     "response times 3-4 h at low latitudes, <2 h at mid/high latitudes (400 km)", "storm forcing, observational",
     "prior for PR3/PR5", "abstract"),
    ("10.1029/2008GL036916", "deng2009efield", "A", "TIE-GCM", "electric-field variability and Joule heating",
     "Field variability raises Joule heating >100% and changes Tn and density",
     "at 400 km ~120 K polar-average temperature increase", "high-latitude forcing", "energy-input sensitivity", "abstract"),  # noqa: E501
    ("10.1029/2005JA011284", "bruinsma2006storm", "A/C", "CHAMP, GRACE", "storm density response",
     "Global storm-time density increase, latitudinal asymmetry",
     "density increases of 300-800% at 400-500 km; ~4 h delay at equator", "single severe storm",
     "scale of natural density anomalies (cited by baseline)", "abstract"),
    ("10.1029/2009JA015129", "gardner2010tad", "A", "high-resolution global T-I model", "TAD generation",
     "Pulsating storms excite multiple TADs propagating poleward and equatorward", "", "storm forcing",
     "transport of localized energy; prior for PR5", "abstract"),
    ("10.1029/97JA00941", "bauske1997tad", "A", "ionospheric model + TAD description", "TAD effect on ionosphere",
     "TAD winds raise the F2 layer", "", "prescribed TAD", "secondary", "abstract"),
    ("10.1029/ja079i025p03879", "perkins1974artificial", "A/D", "theory", "artificial TIDs",
     "Artificial production of TIDs and large-scale motion (title)", "", "full text not available",
     "early artificial-perturbation concept", "title_only"),
    ("10.1016/j.asr.2015.05.038", "emmert2015review", "A/C", "review", "thermospheric mass density",
     "Review of mass density observations, models and uncertainties", "", "", "background (cited by baseline)", "title_only"),  # noqa: E501
    ("10.1029/2004JA010884", "weimer2005", "B", "Weimer 2005", "high-latitude potential driver",
     "Empirical potential/FAC model used to drive GITM here", "", "", "model driver", "abstract"),
    ("10.1029/2003GL019314", "luhr2004cusp", "A", "CHAMP observations", "localized cusp density enhancement",
     "Localized cusp density enhancements associated with small-scale FACs",
     "air density enhancements of almost a factor of two in the cusp (25 Sep 2000)", "natural forcing",
     "natural localized density anomalies of order delta~1 exist; prior for PR12", "abstract"),
    ("10.1029/2009GL042143", "crowley2010cusp", "A", "TIMEGCM + AMIE", "cusp density enhancement",
     "First detailed model explanation of a CHAMP cusp density enhancement", "", "single event",
     "physics model reproduces localized anomaly", "abstract"),
    ("10.1029/2012GL053034", "carlson2012cusp", "A", "first-principles analysis", "cusp input-response",
     "Explains up-to-doubling of air density and drag near 400 km from cusp energy impulses",
     "up to doubling of density/drag near 400 km", "", "natural localized delta~1 at 400 km", "abstract"),
    ("10.1029/2008GL035972", "clemmons2008streak", "A", "Streak observations", "cusp density",
     "Cusp density depleted at lower altitude relative to surroundings (altitude effect)", "",
     "single mission", "sign changes with altitude; prior for PR4", "abstract"),
    ("10.1029/2012GL053519", "zhang2012soft", "A", "CMIT", "soft precipitation heating",
     "Soft electron precipitation raises Joule heating per unit mass and F-region density", "", "",
     "deposition altitude matters; prior for PR7", "abstract"),
    ("10.1029/2009JA014754", "lei2010wind", "A", "TIMED/CHAMP + model", "winds/temperature in storm density response",
     "SigmaO/N2 depleted at high latitude, enhanced at low latitude; structures differ from density", "", "",
     "composition response; prior for PR4", "abstract"),
    ("10.1029/2010JA016164", "lei2011recovery", "A", "observations/model", "storm recovery",
     "Rapid recovery of density after October 2003 storms (title)", "", "full text not available",
     "persistence prior for PR6", "title_only"),
    ("10.1029/2019SW002287", "oliveira2019drag", "C/E", "CHAMP, GRACE + JB2008", "storm-time orbital drag",
     "Superposed-epoch orbital drag effects of storms vs JB2008 background", "", "observational",
     "established storm->drag->decay link", "abstract"),
    ("10.1029/2022SW003193", "fang2022starlink", "C/E", "NOAA SWPC models (incl. WAM-IPE)", "storm density and satellite loss",  # noqa: E501
     "Starlink loss of 38/49 satellites attributed to storm-enhanced density", "38 of 49 satellites lost", "",
     "established coupled chain energy->density->drag->reentry for natural storms", "abstract"),
    ("10.1029/2023SW003716", "baruah2024starlink", "C/E", "MHD modelling", "moderate storms and VLEO loss",
     "Moderate storms adversely affected Starlink satellites", "", "", "as above", "abstract"),
    ("10.3389/fspas.2024.1522139", "oliveira2025starlink", "C/E", "TLE analysis", "storm-accelerated reentry",
     "Qualitative analysis of a storm-accelerated Starlink reentry", "", "qualitative", "as above", "abstract"),
    ("10.1029/2020SW002664", "li2021pod", "C", "POD data", "storm-time orbital decay",
     "Orbital decay from POD energy-decay during storms", "", "", "established measurement of storm decay", "abstract"),
    ("10.2514/6.2008-6442", "vallado2008drag", "C", "review", "drag/density modelling",
     "Critical assessment of drag and density modelling (title)", "", "", "orbit-prediction uncertainty", "title_only"),
    ("10.1016/j.actaastro.2021.05.038", "serfontein2021dragaug", "D", "review", "drag augmentation systems",
     "Review of drag augmentation for debris mitigation (title)", "", "", "passive drag augmentation predecessor", "title_only"),  # noqa: E501
    ("10.1016/j.jsse.2020.07.026", "rhatigan2020deorbit", "D", "review", "drag-enhancing deorbit devices",
     "Review of drag-enhancing deorbit devices (title)", "", "", "as above", "title_only"),
    ("10.1016/0094-5765(91)90184-7", "schall1991laser", "D", "concept", "laser debris removal",
     "Orbital debris removal by laser radiation (title)", "", "", "non-contact removal predecessor", "title_only"),
    ("10.1063/1.3507120", "rubenchik2010laser", "D", "concept", "laser debris removal",
     "Laser systems for orbital debris removal (title)", "", "", "as above", "title_only"),
    ("10.1016/j.actaastro.2020.07.007", "smith2020ionodrag", "D", "concept", "ionospheric (plasma) drag deorbit",
     "Ionospheric drag for accelerated deorbit (title)", "", "", "environment-mediated drag predecessor", "title_only"),
    ("10.1016/j.jastp.2004.04.008", "wang2004cmit", "A", "CMIT", "coupled M-I-T response", "Initial CMIT results (title)",  # noqa: E501
     "", "", "secondary", "title_only"),
    ("10.1029/2011SW000724", "fedrizzi2012joule", "A/C", "CTIPe + observations", "Joule heating index from density",
     "Physics-based modelling links Joule heating to density for drag", "", "", "energy->density->drag link", "abstract"),  # noqa: E501
]


def main():
    rows = []
    for doi, key, dom, mod, proc, pr, q, lim, rel, ev in A:
        p = os.path.join(D, doi.lower().replace("/", "_") + ".json")
        if not os.path.exists(p):
            p = os.path.join(D, doi.replace("/", "_") + ".json")
        m = json.load(open(p))["message"]
        au = "; ".join(f"{a.get('family', '')}, {a.get('given', '')}".strip(", ") for a in m.get("author", []))
        rows.append(dict(citation_key=key, authors=au, year=m["issued"]["date-parts"][0][0], title=m["title"][0],
                         journal=(m.get("container-title") or [""])[0], doi=m["DOI"], verified="crossref",
                         evidence_level=ev, research_domain=dom, model_used=mod, physical_process=proc,
                         principal_result=pr, quantitative_result=q, limitations=lim,
                         relevance_to_current_study=rel))
    with open("references/PRIOR_KNOWLEDGE_VERIFIED.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=F)
        w.writeheader()
        w.writerows(rows)
    print(len(rows))


if __name__ == "__main__":
    main()
