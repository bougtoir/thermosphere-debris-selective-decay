"""JSSE manuscript for the GITM localized-heating study (non-target orbital-drag exposure framing).

Reuses the value collection, tables, equations, figures and docx helpers of scripts/build_physical_manuscript.py, so
every number is read from the same canonical outputs (results/, data/physical/) at build time. Citations are numbered
in square brackets in order of first appearance (JSSE guide for authors, archived in data/raw/journal/jsse/), formatted
from archived Crossref records; references added for the space-safety framing are listed in
references/JSSE_ADDED_REFERENCES.csv.

Outputs (manuscript/JSSE/): manuscript.docx (figures supplied separately), manuscript_review_inline.docx (figures
inline), tables.docx, figures.pptx, highlights.docx, cover_letter.docx, figures/Fig{n}.tif;
results/manuscript_jsse_values.csv (must equal results/manuscript_physical_values.csv) and
results/manuscript_jsse_citations.csv.
"""
from __future__ import annotations

import os
import re
import shutil
import sys

import pandas as pd
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_physical_manuscript as bpm  # noqa: E402
from build_physical_manuscript import (CAPTIONS, Doc, V, collect, eq_dv, eq_s, fill_captions,  # noqa: E402
                                       m_frac, m_r, m_sub, m_sup, new_doc, rd, runs, small, table1, table2, table3,
                                       table4)

ROOT = bpm.ROOT
OUT = os.path.join(ROOT, "manuscript/JSSE")
FIG = bpm.FIG
WORD_LIMIT = bpm.WORD_LIMIT
HL_MAX = bpm.HL_MAX

TITLE = "Non-target orbital-drag exposure from localized thermospheric heating: a coupled GITM–orbit assessment"
AUTHOR = dict(
    name="Tatsuki Onishi",
    affiliation=("Data Science and AI Innovation Research Promotion Center, Shiga University, 1-1-1 Bamba, Hikone, "
                 "Shiga 522-8522, Japan"),
    email="bougtoir@gmail.com",
    orcid="0000-0001-7261-9062",
)
REPO_URL = bpm.REPO_URL
REPO_TAG = "gitm-orbit-selectivity-v1.1"


ISO4 = {  # journal titles abbreviated per the ISSN List of Title Word Abbreviations (JSSE guide)
    "Geophysical Research Letters": "Geophys. Res. Lett.",
    "Journal of Geophysical Research: Space Physics": "J. Geophys. Res. Space Phys.",
    "Journal of Geophysical Research": "J. Geophys. Res.",
    "Journal of Atmospheric and Solar-Terrestrial Physics": "J. Atmos. Sol.-Terr. Phys.",
    "Journal of Advances in Modeling Earth Systems": "J. Adv. Model. Earth Syst.",
    "Earth and Space Science": "Earth Space Sci.",
    "Advances in Space Research": "Adv. Space Res.",
    "Space Weather": "Space Weather",
    "Frontiers in Astronomy and Space Sciences": "Front. Astron. Space Sci.",
    "Acta Astronautica": "Acta Astronaut.",
    "Journal of Space Safety Engineering": "J. Space Saf. Eng.",
    "Science": "Science",
    "Progress in Aerospace Sciences": "Prog. Aerosp. Sci.",
    "Geophysical Monograph Series": "Geophys. Monogr. Ser.",
    "AIP Conference Proceedings": "AIP Conf. Proc.",
}
NOT_JOURNAL = {"AIAA/AAS Astrodynamics Specialist Conference and Exhibit"}


class Refs(bpm.Refs):
    def __init__(self):
        super().__init__()
        add = rd("references/JSSE_ADDED_REFERENCES.csv").set_index("citation_key")
        assert not set(add.index) & set(self.tab.index)
        self.tab = pd.concat([self.tab, add])

    def entry(self, key):
        e = super().entry(key)
        r = self.tab.loc[key]
        cont = (self.cr.get(str(r.doi).lower(), {}).get("container-title") or [r.journal])[0]
        if cont in NOT_JOURNAL:
            return e
        i = e.rfind(f", {cont} ")
        assert i > 0 and cont in ISO4, (key, cont)
        return e[:i] + f", {ISO4[cont]} " + e[i + len(cont) + 3:]


def eq_share():
    """Eq. (3): aggregate non-target share of the total extra Δv of a shell."""
    def total(g):
        return (f'<m:nary><m:naryPr><m:chr m:val="∑"/><m:supHide m:val="1"/></m:naryPr>'
                f"<m:sub>{g}</m:sub><m:sup></m:sup>"
                f"<m:e>{m_sup(m_sub(m_r('Δ') + m_r('v'), m_r('i')), m_r('extra', True))}</m:e></m:nary>")
    return (m_sub(m_r("F"), m_r("N", True)) + m_r("(t)", True) + m_r(" = ", True)
            + m_frac(total(m_r("i") + m_r(" ∈ ", True) + m_r("N", True)), total(m_r("i", False))))


def data_statement(S):
    z = S["zenodo"]
    t = ("The analysis code, GITM case configurations, the heating hook and the figure- and manuscript-generation "
         f"scripts are publicly available at {REPO_URL} (release tag {REPO_TAG}; the JSSE manuscript builder is "
         "scripts/build_jsse_manuscript.py). ")
    what = (f"The processed GITM fields required to reproduce the figures, tables and principal numerical results "
            f"(about {S['proc_gb']} GB, five paired heated/control files with SHA-256 checksums) and a snapshot of "
            "the code ")
    assert z and z.get("published"), "JSSE data statement requires the published Zenodo record"
    t += what + f"are archived at Zenodo, https://doi.org/{z['doi']}. "
    return t + ("The GITM run configurations, execution records and file-level SHA-256 checksums of the raw output "
                "are documented in the repository (data/physical/run_records/ and "
                "data/physical/GITM_RUN_MANIFEST.csv). Reproducing the results from the processed fields does not "
                "require GITM; regenerating the processed fields requires rerunning GITM. "
                f"The full raw GITM output (about {S['raw_gb']} GB, including failed and test runs) is not deposited "
                "and is available from the author on reasonable request.")


def highlights(v):
    h = [
        "Coupled GITM–orbit runs quantify drag exposure of objects outside a target set",
        f"After 12 h, target/non-target drag ratio is ~{float(v['Sc_400']):.1f} at 400 km, ~{float(v['Sc_500']):.0f} at 500 km",
        f"Non-targets get {v['sharec_400']}% of extra drag at 400 km in the synthetic orbit sample",
        f"Idealized static Gaussian patches overstate selectivity {v['gf_lo_12_400']}–{v['gf_hi_12_500']}×",
        "Extra drag is an exposure metric; collision risk and feasibility are not assessed",
    ]
    for x in h:
        assert len(x) <= HL_MAX, (len(x), x)
    return h


def body(D, v):
    S = v
    D.p(TITLE, align=WD_ALIGN_PARAGRAPH.CENTER).runs[0].bold = True
    D.p(AUTHOR["name"], align=WD_ALIGN_PARAGRAPH.CENTER)
    D.p(AUTHOR["affiliation"], align=WD_ALIGN_PARAGRAPH.CENTER)
    D.p(f"Corresponding author: {AUTHOR['name']}, {AUTHOR['affiliation']}. E-mail: {AUTHOR['email']}. "
        f"ORCID: {AUTHOR['orcid']}", align=WD_ALIGN_PARAGRAPH.CENTER)

    D.h("Abstract")
    D.p(
        "Environment-directed debris-remediation concepts would raise the thermospheric density along the paths of "
        "selected debris objects to accelerate their decay. Because such an intervention modifies a shared medium, "
        "its safety screening must quantify not only the intended drag on targets but also the extra drag received by "
        "objects outside the target set. I quantify this non-target orbital-drag exposure for an idealized intervention "
        "with a physically self-consistent model. A compact neutral heat source (100 GW for 1 h, centred at 300 km and "
        "45°N) is inserted into the Global Ionosphere–Thermosphere Model (GITM) and paired with an unheated control, "
        f"and the resulting density and wind fields drive drag on {S['n_tot']} synthetic circular orbits per shell at "
        "300, 400 and 500 km; targets are objects that pass through the source footprint while it is on. The "
        f"perturbation reaches {S['pk_p11_z300_400']}% at 400 km but spreads over most of the globe within hours. Over "
        "12 h the ratio of mean extra Δv between targets and non-targets (selectivity) is "
        f"{S['Sc_400']} at 400 km, {S['Sc_500']} at 500 km and {S['Sc_300']} at 300 km, and non-targets receive "
        f"{S['sharec_400']}% and {S['sharec_500']}% of the total extra Δv of the synthetic sample at 400 and 500 km. "
        f"Idealized static Gaussian patches matched to the GITM peak overstate selectivity by factors of "
        f"{S['gf_lo_12_400']}–{S['gf_hi_12_400']} at 400 km and {S['gf_lo_12_500']}–{S['gf_hi_12_500']} at 500 km, "
        f"and a source-centred 1000 km patch by {S['src_lo_400']}–{S['src_hi_500']}. Doubling the horizontal resolution "
        f"changes the 12 h selectivity by at most {S['S_grid_max']}% at 400 and 500 km. In two-level tests, "
        "selectivity is lower at 100 GW than at 10 GW and disappears for deposition at 150 km. Extra drag is an "
        "exposure metric, not an estimate of collision or operational risk, and no engineering feasibility is "
        "implied. Within these limits, screening of environment-directed remediation should report non-target "
        "exposure computed with a time-evolving atmosphere rather than with prescribed static density patches.")
    D.p("Keywords: space safety; debris remediation; non-target exposure; atmospheric drag; thermosphere; GITM",
        count=True)
    D.p("Abbreviations: GITM, Global Ionosphere–Thermosphere Model; MSIS, Mass Spectrometer Incoherent Scatter "
        "empirical atmosphere model (NRLMSISE-00); SME, SuperMAG electrojet index; FTA, Feature Tracking of Aurora "
        "model; MPI, Message Passing Interface; S, drag selectivity; Δv, velocity change.", count=True)

    D.h("1. Introduction")
    D.p(
        "Orbital debris is a space-safety problem because collisions among orbiting objects can sustain the growth "
        "of the debris population even without new launches [@kessler1978debrisbelt,liou2006risks,"
        "lewis2020population]. Most proposed remediation methods act on individual objects: capture and controlled "
        "deorbit, drag-augmentation devices, or momentum transfer by ground- or space-based lasers "
        "[@bonnal2013adr,shan2016adrreview,svotina2024removal,serfontein2021dragaug,rhatigan2020deorbit,"
        "schall1991laser,rubenchik2010laser]. A different and speculative family acts on the environment rather "
        "than on the object: if the neutral density along a target's path could be raised, its drag and decay "
        "rate would increase without contact. Enhanced ionospheric drag has been discussed in this spirit "
        "[@smith2020ionodrag].")
    D.p(
        "Object-directed and environment-directed interventions differ in who is affected. An object-directed "
        "method acts, by design, on the object it engages. An environment-directed method modifies a shared medium, "
        "so every object that crosses the modified region, or any region that the perturbation later reaches, "
        "receives part of the effect. Assessing remediation measures by their effect on the debris environment and "
        "on operations rather than by their intended mechanism alone [@mcknight2016remediation,usovik2023mitigation] "
        "therefore requires, for environment-directed concepts, a quantity that object-directed methods do not "
        "need: the drag exposure of objects outside the target population. Unplanned drag changes are relevant to "
        "operations because atmospheric density and drag uncertainties propagate directly into orbit prediction and "
        "estimation [@vallado2014dragassessment].")
    D.p(
        "The thermosphere is known to respond strongly and quickly to energy input. Storm-time heating raises density "
        "globally within hours [@bruinsma2006storm,sutton2009rapid,emmert2015review], and localized auroral or cusp "
        "heating produces density enhancements that can approach a factor of two near 400 km [@luhr2004cusp,"
        "crowley2010cusp,carlson2012cusp]. Physics-based models reproduce these responses and show that sudden, "
        "intense heating launches travelling atmospheric disturbances and departures from hydrostatic balance that "
        "carry the perturbation away from the source [@deng2008nonhydro,gardner2010tad]. In GITM, an idealized "
        "50 GW substorm-like input raises the local density by about 14% [@liu2015substorm]. The drag consequences "
        "of storm-time density increases are also well documented, including the loss of newly launched satellites "
        "[@oliveira2019drag,fang2022starlink,baruah2024starlink].")
    D.p(
        "What has not been quantified is how the horizontal and vertical redistribution of a localized perturbation "
        "divides the resulting extra drag between objects that did, and did not, pass through the heated region. "
        "An idealized screening approach that prescribes a static Gaussian density patch around the source assumes "
        "that the perturbation stays localized, which can inflate the apparent selectivity. A targeted literature "
        "search found no published study that evaluates selective debris decay in this way, so the static patch is "
        "used here as an idealized comparator, not as a representation of prior work. Here I compare such patches "
        "with a self-consistent general circulation model, the Global Ionosphere–Thermosphere Model (GITM) "
        "[@ridley2006gitm], couple its paired heated and control fields directly to an orbit propagator, and ask "
        "three questions: (i) how the cumulative extra drag over 12 h is divided between target and non-target "
        "objects; (ii) by how much static patches overstate the target/non-target contrast; and (iii) whether the "
        "answer survives a change of model resolution. Predictions for the physical response and for selectivity "
        "were written down and committed before any heated output existed, and are scored against the results. The "
        "thermospheric response to localized heating — the local density increase, its spreading and the "
        "associated waves — is established physics and is not claimed as new; the contribution is the quantified "
        "non-target drag exposure that this response implies for an environment-directed intervention. Extra drag "
        "is treated throughout as an exposure metric: collision probability, conjunction rates and manoeuvre burden "
        "are not computed. How such a heat source could be produced is outside the scope, and no engineering "
        "feasibility is claimed.")

    D.h("2. Methods")
    D.h("2.1. Thermosphere model and background state", 2)
    D.p(
        "GITM solves the non-hydrostatic Navier–Stokes equations for the neutral and ion species on a spherical grid "
        "with altitude as the vertical coordinate [@ridley2006gitm]. I used the public GITM source (commit "
        "c4fc315), compiled with GNU Fortran 11.4 and Open MPI 4.1.2, with 50 altitude levels starting at "
        "100 km. The background was a quiet equinox (2002-03-21) with constant drivers: F10.7 = F10.7A = 150, "
        "interplanetary magnetic field B_{z} = −2 nT, solar wind 400 km s^{−1}, and a constant SuperMAG "
        "electrojet index SME = 150 nT "
        "driving the FTA auroral model. High-latitude electrodynamics used the Weimer model [@weimer2005] "
        "and the lower boundary was set "
        "from NRLMSISE-00 [@picone2002msis]. Constant drivers ensure that heated and control runs differ only by "
        "the added heat source.")
    D.p(
        f"The coarse-grid background was spun up for {S['spin_c']} h from an MSIS initial state. Its global-mean "
        f"density at 250, 400 and 500 km was {S['V4@250']}, {S['V4@400']} and {S['V4@500']} times the NRLMSISE-00 "
        f"value for the same time, and the 400 km neutral temperature differed from MSIS by {S['V5']}; these and "
        "other acceptance criteria were set before the spin-up was inspected. One criterion failed: the minimum "
        f"neutral temperature was {S['V2b_min']} K, against a lower bound of 150 K, in a small high-latitude region "
        "near 100–107 km. I retain this failure as a limitation; it lies far below the heated layer and the orbit "
        "shells.")
    D.h("2.2. Localized heat source", 2)
    D.p(
        "A heating term was added to the GITM neutral energy equation through the model's user-perturbation hook. "
        "Its spatial shape is Gaussian in great-circle distance from the centre (σ_{h} = 1000 km) and in altitude "
        "(σ_{z} = 50 km around z_{0} = 300 km, or 20 km around 150 km), and its time profile is a 1 h cosine-tapered boxcar with "
        f"10 min ramps, which deposits {S['E_p11_z300']} J at 100 GW. The heating rate is normalised on the "
        "discrete grid with a global MPI sum of "
        "weight × cell volume, so the deposited power equals the requested P_{0} irrespective of grid or domain "
        f"decomposition; the realized power on the coarse grid was {S['Preal']} GW, and the realized horizontal width "
        f"was {S['sig_eff']} km on the coarse grid and {S['sig_eff_f']} km on the fine grid. The source is an abstract "
        "neutral energy input; no heating mechanism or hardware is implied.")
    D.h("2.3. Experiments", 2)
    D.p(
        "Each heated case was paired with a control started from the same restart file with zero source power, so "
        "that every reported perturbation is a heated-minus-control difference at identical times. On the coarse "
        "grid (10°×5°) I ran three heated cases: 100 GW and 10 GW centred at 300 km, and 100 GW centred at 150 km, "
        "each for 12 h with heating from 1 h to 2 h. The 100 GW, 300 km pair was repeated on a fine grid "
        "(5°×2.5°). The fine pair was run to 3 h and then continued from its 3 h restart files to 12 h, with the "
        "source timing corrected for the restart origin; the 3 h outputs were kept unchanged. Table 1 lists the two "
        "configurations. Energy closure — the change in total neutral internal energy over the deposited energy at "
        f"the first output after onset — was {S['cl_p11_z300']} and {S['cl_p11_z300_fine12']} for the coarse and "
        f"fine 100 GW pairs, {S['cl_p10_z300']} for 10 GW and {S['cl_p11_z150']} for 150 km deposition.")
    D.table(1, "Configuration of the coarse- and fine-grid GITM experiments.", table1(v),
            "Cells per σ_{h} and realized σ_{h} are computed from the source as evaluated on each grid. The fine grid "
            "used four MPI ranks because a decomposition-dependent sanity check in the GITM potential solver stopped "
            "the two-rank run; the executable and grid were otherwise identical.")
    D.h("2.4. Orbit coupling and selectivity", 2)
    D.p(
        f"For each of 300, 400 and 500 km, {S['n_tot']} synthetic circular orbits were generated at inclinations "
        "of 30°, 50°, 70° and 97° with random node and phase (fixed seed). Orbits were propagated with J2 secular "
        "rates at 10 s steps, and the GITM density (log-linear interpolation in space and time between 10 min "
        "outputs) and winds were sampled along each track. The cumulative extra drag velocity change of object i is")
    D.eq(eq_dv(), 1)
    D.p(
        "where subscripts p and c denote the heated and control runs, v_{rel} is the velocity relative to the "
        "co-rotating atmosphere plus the GITM wind, B = 30 kg m^{−2} is the ballistic coefficient and t is time "
        "after heating onset. An object is a target if its ground track comes within σ_{h} of the source centre "
        f"while the source is on ({S['n_t400']} of {S['n_tot']} objects at 400 km). The selectivity is")
    D.eq(eq_s(), 2)
    D.p(
        "where angle brackets denote the mean over the target (T) or non-target (N) objects of a shell. S compares "
        "the average object in each group. The aggregate non-target share")
    D.eq(eq_share(), 3)
    D.p(
        "where the sums run over the non-target objects and over all objects of a shell, is the fraction of the "
        "total extra drag of the synthetic sample that falls outside the target set. Unlike S, it depends on how many "
        "objects of the sample are targets, and therefore on the synthetic population and on the target criterion; "
        "it is a property of this sample, not of any real satellite or debris population. "
        "Replacing linear by nearest-neighbour "
        "interpolation, removing winds, changing the Earth radius used for altitude, or doubling the output interval "
        f"changed the 12 h selectivity at 400 and 500 km by at most {S['orbit_sens']}%. Sampling uncertainty of S "
        f"was estimated by resampling targets and non-targets separately with replacement ({S['n_boot']} replicates, "
        "percentile 95% intervals).")
    D.h("2.5. Static comparators", 2)
    D.p(
        "To compare the evolving GITM perturbation with a prescribed static field, the same orbits were also "
        "flown through static Gaussian patches "
        "imposed on the GITM control atmosphere. The peak-matched patch takes the amplitude, centre and e^{−1/2} "
        "area-equivalent width of the GITM perturbation at the time of its peak at each orbit altitude, and is held "
        "fixed while the GITM peak exceeds half its maximum. The source-centred patch, the simplest idealized "
        "screening form, has the same amplitude and window but is centred on the source with σ = 1000 km. Because the "
        "peak-matched fit depends on discrete choices, I also recomputed it with the centre, width and time window "
        "taken from the other grid.")
    D.h("2.6. Resolution test", 2)
    D.p(
        "For each diagnostic, the fine-grid result was compared with the coarse-grid result in two ways: on its native "
        "grid, and after conservative remapping of ρ (area-weighted 2×2 means) to the coarse grid before "
        "differencing. The remapped comparison (A) measures the change due to the model's discretization; the "
        "native-versus-remapped difference (B) measures the change due only to evaluating diagnostics on a finer "
        f"grid. The fine background was spun up for {S['spin_f']} h, against {S['spin_c']} h on the coarse grid, so "
        "A also contains any effect of the shorter spin-up. With two resolutions, these differences indicate "
        "sensitivity; they do not establish numerical convergence.")
    D.h("2.7. Frozen predictions", 2)
    D.p(
        "Before the first heated case was started, I committed quantitative predictions (PR1–PR12) to the project "
        "repository (docs/PRIOR_PREDICTIONS_FROZEN.md), derived from published "
        "simulations and observations, together with falsification rules, and a decision rule for the scientific "
        "contribution that required the direction of the GITM-versus-patch difference to be preserved across grids. "
        "Thresholds were not changed after results were available; the outcomes are scored in Section 3.6. These "
        "predictions were frozen prospectively within the project; they were not registered with an external "
        "registry.")

    D.h("3. Results")
    D.h("3.1. Physical response and redistribution", 2)
    D.p(
        f"The 100 GW source raised the 400 km density by up to {S['pk_p11_z300_400']}% and the 500 km density by up to "
        f"{S['pk_p11_z300_500']}%, with neutral temperature increases of up to {S['dT_p11_z300']} K and O/N_{{2}} "
        f"decreases of up to {S['dOn2_p11_z300']}% in the heated column. Fig. 1 shows that the perturbation, compact "
        f"at the end of heating, is carried equatorward and westward; at 3 h after onset it covers {S['pa3h']}% of the "
        "shell (participation area). By "
        f"the end of the window the residual 400 km perturbation is a few per cent and nearly global, with weak "
        "negative anomalies near the original source. The area-integrated excess at 400 km peaks just after "
        "switch-off and then decays, while the participation area and radius of gyration keep growing for about "
        f"{S['rg_tmax']} h (Fig. 2). The largest area with Δρ/ρ > 1% at 400 km was {S['af_p11_z300_400']}% of the shell, and the "
        f"global-mean density increase peaked at {S['gm_p11_z300_400']}%.")
    D.figure(1, CAPTIONS[1][0])
    D.figure(2, CAPTIONS[2][0])
    D.h("3.2. Target and non-target cumulative drag", 2)
    D.p(
        "Because targets are defined by their passage through the source while it is on, they collect most of their "
        "extra drag early, whereas non-targets keep accumulating drag from the spreading perturbation. As a result "
        f"S(t) falls monotonically after the first hour at 400 and 500 km (Fig. 3): at 400 km from {S['Sc_400_1h']} at "
        f"1 h to {S['Sc_400_3h']} at 3 h and {S['Sc_400']} at {S['t_end_h']} h after onset; at 500 km from "
        f"{S['Sc_500_1h']} to {S['Sc_500_3h']} and {S['Sc_500']}. Resampling the objects gives 95% intervals of "
        f"{S['ci_lo_400']}–{S['ci_hi_400']} at 400 km and {S['ci_lo_500']}–{S['ci_hi_500']} at 500 km for the coarse "
        "12 h values, so the orbit sample is not the limiting uncertainty; these intervals are conditional on the single "
        "simulated atmosphere and exclude model, background and forcing uncertainty. At 300 km, where the perturbation is smaller and "
        f"broad, S settles near unity ({S['Sc_300']}). By the end of the window non-targets account for "
        f"{S['sharec_400']}% of the total extra Δv of the synthetic sample at 400 km and {S['sharec_500']}% at 500 km "
        "(Eq. (3)). Table 2 summarises "
        f"the 12 h values. The target extra Δv at 400 km was {S['dv_t400']} mm s^{{−1}}, {S['dv_nat_frac']}% of the "
        f"natural drag Δv over the same window, which shortens a {S['life400']} d orbital lifetime by about "
        f"{S['dlife400']} d.")
    D.h("3.3. Comparison with idealized static patches", 2)
    D.p(
        "Idealized static patches flown along the same orbits give substantially higher selectivity (Fig. 4). Over 12 h, the peak-matched Gaussian "
        f"overstates the GITM selectivity by factors of {S['gf_lo_12_400']}–{S['gf_hi_12_400']} at 400 km and "
        f"{S['gf_lo_12_500']}–{S['gf_hi_12_500']} at 500 km, across both grids and all fit variants (Table 2). The "
        f"source-centred σ = 1000 km patch overstates it by {S['src_lo_400']}–{S['src_hi_400']} at 400 km and "
        f"{S['src_lo_500']}–{S['src_hi_500']} at 500 km. At 300 km, where the perturbation is weak and broad, the "
        "peak-matched patch is close to GITM.")
    D.table(2, "Twelve-hour drag selectivity from GITM and from static comparators, 100 GW source at 300 km.",
            table2(v),
            "S is the ratio of mean extra Δv of target and non-target objects. The range in the sixth column covers "
            "the peak-matched fit with its own centre, width and window and with each of these taken from the other "
            "grid (two variants on the coarse grid, "
            f"{S['nvar']} on the fine grid); it was evaluated at 400 and 500 km only.")
    D.p(
        f"Over the first 3 h the comparison is different. At 400 km, the GITM selectivity is indistinguishable from "
        f"that of the peak-matched patch (ratio {S['gr_lo_3_400']}–{S['gr_hi_3_400']} across grids and fit variants), and the "
        "sign of the difference depends on the fit. The sign change between grids comes from the half-maximum time "
        "window, which starts one 10 min output earlier on the fine grid; using the coarse-grid window on the fine "
        f"grid restores agreement in sign, and the GITM selectivity itself differs between grids by {S['g3h_diff']}%. At "
        "400 km, the reduction relative to a static patch therefore emerges after switch-off, while the perturbation "
        "spreads, rather than during the heating hour. At 500 km the reduction is already present at 3 h "
        f"(ratio {S['gr_lo_3_500']}–{S['gr_hi_3_500']}).")
    D.figure(3, CAPTIONS[3][0])
    D.figure(4, CAPTIONS[4][0])
    D.h("3.4. Sensitivity to model resolution", 2)
    D.p(
        f"Of {S['gs_n']} diagnostic-by-altitude comparisons that can be remapped, {S['gs_ok']} belong to diagnostics "
        f"that changed by 20% or less between grids at every altitude (largest change {S['gs_max_ok']}%), and "
        f"the diagnostic-grid effect B never exceeded {S['gs_B_max']}% "
        "(Table 3). The 12 h selectivity, the target and non-target extra Δv, the peak and integrated perturbation, "
        "the affected area and the spreading rate are all robust in this sense, and the fine-grid curves overlie "
        "the coarse-grid curves throughout the 12 h (Figs. 2–3). The participation area differs by up to "
        f"{S['pa_diff']}% in mid-window. The fine-vs-coarse change in peak Δρ/ρ at 400 km was {S['pk_fc']}% "
        "and in integrated excess "
        f"{S['int_fc']}%, so both frozen resolution criteria (PR8a: < 30%; PR8b: < 20%) were met over 3 h and 12 h. "
        "Two quantities are resolution-sensitive and are not used for any conclusion: the negative perturbation, "
        f"whose integral is {S['neg_fc']} times larger on the fine grid, and the end-of-window centroid, which is "
        "poorly defined once the perturbation is nearly global.")
    D.table(3, "Coarse- versus fine-grid sensitivity of the 100 GW, 300 km case over 12 h.", table3(v),
            "A: remapped fine minus coarse, relative to coarse (model discretization plus the shorter fine spin-up). "
            "B: native fine minus remapped fine, relative to remapped (diagnostic grid only). Δv in m s^{−1}; "
            "integrals in kg m^{−1}; radius in km; speed in m s^{−1}; latitude in degrees.")
    D.h("3.5. Power and deposition altitude", 2)
    D.p(
        "Two further coarse-grid pairs bracket the dependence on source parameters (Fig. 5). Reducing the power to "
        f"10 GW reduced the 400 km peak only to {S['ratio_pk_power']} of its 100 GW value, whereas the global-mean "
        f"density increase at 400 km fell from {S['gm_p11_z300_400']}% to {S['gm_p10_z300_400']}% and the maximum area "
        f"with Δρ/ρ > 1% from {S['af_p11_z300_400']}% to {S['af_p10_z300_400']}%. The 12 h selectivity was "
        f"correspondingly higher at 10 GW ({S['S_p10_z300_400']} at "
        f"400 km, {S['S_p10_z300_500']} at 500 km). Depositing 100 GW at 150 km produced a 400 km peak "
        f"{S['ratio_pk_z150']} times that of 300 km deposition and selectivities of {S['S_p11_z150_400']} and "
        f"{S['S_p11_z150_500']} at 400 and 500 km: lower-altitude heating raises density almost uniformly at orbit "
        "heights. These are two-level contrasts on one grid and do not define a scaling law.")
    D.figure(5, CAPTIONS[5][0])
    D.h("3.6. Scorecard of frozen predictions", 2)
    D.p(
        f"Of the {S['n_core']} prospectively frozen outcomes evaluated on the primary configuration, {S['n_conf']} were "
        f"confirmed, {S['n_fals']} falsified and {S['n_out']} fell outside the predicted range without being "
        "falsified (Table 4). The falsifications are informative. The 400 km peak response was "
        f"{S['PR1']}%, above the predicted 5–100% (PR1), so a 100 GW source does reach δ ≥ 1 (PR12). The response was "
        f"less than linear in power, with a 10 GW/100 GW peak ratio of {S['PR2']} (predicted 0.05–0.2; PR2). "
        "Deposition "
        f"at 150 km was much less effective at 400 km than predicted (ratio {S['PR7']}, PR7). The predicted ≥ 3-fold "
        "reduction of selectivity relative to the peak-matched patch (PR10) held at 500 km, was not reached at 400 km "
        f"(factor {S['PR10@400']}, outside the range but not falsified) and was falsified at 300 km "
        f"(factor {S['PR10@300']}), where the perturbation is broad and selectivity is close to unity in both "
        f"fields. The target extra Δv at 400 km ({S['PR9']}% of natural drag) slightly exceeded the predicted range "
        "(PR9). All fine-grid rows reproduce the coarse-grid outcomes.")
    D.table(4, "Outcomes of the predictions frozen before the first heated run.", table4(v),
            "Values are those of the quantity named in the scorecard file; 12 h and fine-grid rows were added after "
            "the fine-grid extension using the unchanged rules.")

    D.h("4. Discussion")
    D.h("4.1. Intended benefit versus distributed exposure", 2)
    D.p(
        "For a space-safety screening, the relevant comparison is between the drag delivered to the intended targets "
        "and the drag distributed to all other objects. In the self-consistent model, the perturbation spreads well "
        "beyond the source within a few hours of switch-off (Figs. 1–2), consistent with the wind and wave response "
        "known from auroral and cusp heating [@deng2008nonhydro,gardner2010tad,liu2015substorm], and objects that "
        "never passed the source then collect most of the extra drag of the synthetic sample. The target advantage "
        "is largest during and just after the heating hour and shrinks as drag accumulates (Fig. 3), so the window "
        "over which exposure is integrated determines the answer. At the same time the intended benefit is small: "
        f"the target drag increment at 400 km for 100 GW sustained for 1 h was {S['dv_nat_frac']}% of natural drag "
        "over 12 h, which changes the orbital lifetime by a negligible amount.")
    D.p(
        f"The power dependence points the same way. Increasing the power tenfold increased the 400 km peak only "
        f"{S['inv_pk_power']}-fold but raised the global-mean increase {S['gm_ratio']}-fold, so selectivity fell. "
        "Lowering the deposition altitude removed selectivity altogether. Within the tested range, therefore, neither "
        "more power nor deeper deposition makes the effect more selective; the most selective configuration tested "
        "is the weakest one, where the absolute effect on any object is also smallest. Selectivity as defined here "
        "also depends on the target criterion (passage through the source footprint while it is on); other target "
        "definitions would give different values of S and of the non-target share and were not tested.")
    D.h("4.2. Static patches as a modelling representation", 2)
    D.p(
        "The comparison with static Gaussian patches contrasts two modelling representations of the same forcing, "
        "not two physical outcomes. The static comparators differ from the GITM field in persistence, shape, peak "
        "location and timing at once, and no transport budget was computed, so the difference is attributed to the "
        "time-evolving GITM field as a whole rather than to atmospheric transport alone or to any single mechanism. "
        "A static patch cannot represent this evolution, so it overstates selectivity by a factor that grows with "
        "altitude and with the time over which drag is accumulated. In this experiment the overstatement over 12 h is "
        f"about {S['gf_lo_12_400']}–{S['gf_hi_12_400']}-fold at 400 km and {S['gf_lo_12_500']}–"
        f"{S['gf_hi_12_500']}-fold at 500 km relative to a patch fitted to GITM itself, and "
        f"{S['src_lo_400']}–{S['src_hi_500']}-fold relative to a source-sized patch. These factors, rather than the "
        "absolute selectivity, are the more informative result, because they compare a self-consistent and a "
        "prescribed density field under the same forcing, background and orbits.")
    D.h("4.3. What screening of environment-directed remediation should measure", 2)
    D.p(
        "The results suggest three minimum requirements for screening environment-directed remediation concepts. "
        "First, the modified atmosphere should be computed with a time-evolving, self-consistent model rather than "
        "prescribed as a static patch, because in this experiment the static representation overstated the "
        "target/non-target contrast by a factor that depended on altitude and accumulation time. Second, non-target "
        "exposure should be reported "
        "alongside the target benefit — for example S together with the non-target share — with the object population "
        "and the target definition stated, because the share depends on both. Third, exposure should be accumulated "
        "over a window that extends well beyond the forcing, because estimates made during or just after the forcing "
        "hour are much more favourable than those at 12 h (Fig. 3). These are requirements on the assessment, not "
        "conclusions about any particular concept.")
    D.h("4.4. Exposure is not hazard", 2)
    D.p(
        "Extra drag received by non-target objects is an exposure metric. It does not by itself quantify collision "
        "probability, conjunction rates, manoeuvre burden or mission safety. Converting exposure into hazard would "
        "require a realistic object catalogue with physical properties, orbit-determination and conjunction-screening "
        "workflows that propagate the density change into prediction errors [@vallado2014dragassessment], and "
        "debris-risk assessment tools of the kind used for mission analysis and compliance verification "
        "[@gulde2016risk,braun2020drama]; none of these were applied here. Conversely, a small drag increment on "
        "non-target objects is not evidence of safety, because its magnitude depends on the forcing, the synthetic "
        "population and the target definition. The aggregate non-target share is a property of the synthetic sample "
        "— its object count, inclinations and target criterion — and must not be read as a fraction of real "
        "satellites, of the debris population or of operational risk.")
    D.h("4.5. Limitations", 2)
    D.p(
        "Several limitations bound these conclusions. Only one physical model was used; TIE-GCM [@richmond1992tiegcm,"
        "qian2014tiegcm] and WACCM-X [@liu2018waccmx] could not be run in this environment, so model-structural "
        "uncertainty is not sampled. The background is one quiet equinox state with constant drivers. Only two "
        f"horizontal resolutions were compared, the fine-grid background was spun up for {S['spin_f']} h against "
        f"{S['spin_c']} h on the coarse grid, and no transport budget was computed to separate physical from "
        "numerical diffusion; the agreement between grids is evidence of robustness to resolution, not of "
        "convergence. The source is an idealized neutral energy input of fixed shape and duration at a very large "
        "power. The orbit population is synthetic and circular, uses a single ballistic coefficient and a single "
        "target definition, and power and deposition altitude were each sampled at two levels on the coarse grid "
        "only. Finally, the GITM response was checked against an empirical background and published model results, "
        "not against observations of an equivalent artificial perturbation, which do not exist. These limitations "
        "constrain the generality of the numbers; they do not change the direction of the contrast between the "
        "self-consistent and the static representations, which held on both grids.")

    D.h("5. Conclusions")
    D.p(
        "A compact 100 GW, 1 h neutral heat source in GITM produces a large local density increase that spreads over "
        "most of the globe within hours. Coupled to synthetic orbits, it gives 12 h target/non-target drag "
        f"selectivities of about {float(S['Sc_400']):.1f} at 400 km, {float(S['Sc_500']):.0f} at 500 km and "
        f"{float(S['Sc_300']):.0f} at 300 km, and most of the extra drag of the synthetic sample falls on non-target "
        f"objects. Idealized static Gaussian patches overstate this selectivity by factors of {S['gf_lo_12_400']}–"
        f"{S['gf_hi_12_400']} at 400 km and {S['gf_lo_12_500']}–{S['gf_hi_12_500']} at 500 km when fitted to the "
        f"model, and by {S['src_lo_400']}–{S['src_hi_500']} when sized to the source. Doubling the horizontal "
        f"resolution changed the 12 h selectivity at 400 and 500 km by at most {S['S_grid_max']}%, which indicates "
        "robustness to resolution but not formal convergence. For space-safety screening, an environment-directed "
        "remediation concept should therefore be assessed with a self-consistent, time-evolving atmosphere and with "
        "its non-target drag exposure reported alongside the intended benefit; translating that exposure into "
        "collision or operational risk requires further, separate analysis.")

    D.h("Declaration of competing interest")
    D.p("The author declares no known competing financial interests or personal relationships that could have "
        "appeared to influence the work reported in this paper.")
    D.h("Funding")
    D.p("This research did not receive any specific grant from funding agencies in the public, commercial, or "
        "not-for-profit sectors.")
    D.h("CRediT authorship contribution statement")
    D.p(f"{AUTHOR['name']}: Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, "
        "Writing – original draft, Writing – review and editing, Visualization.")
    D.h("Data availability")
    D.p(data_statement(S))
    D.h("Declaration of generative AI and AI-assisted technologies in the manuscript preparation process")
    D.p("During the preparation of this work the author used an AI software assistant (Devin, Cognition AI) to "
        "implement and run the simulation and analysis code, to retrieve and check bibliographic records, and to "
        "draft and revise text. After using this tool, the author reviewed, verified and edited the code, results, "
        "references and text as needed and takes full responsibility for the content of the published article.")

    D.h("References")
    for n, _, e in D.refs.listing():
        runs(D.d.add_paragraph(), f"[{n}] {e}")
        D.words += len(e.split()) + 1


# ---------------------------------------------------------------- outputs
def horizontal_rules_only(doc):
    """JSSE guide: avoid vertical rules and shading in tables; keep top, bottom and inside horizontal rules."""
    for t in doc.tables:
        pr = t._tbl.tblPr
        for old in pr.findall(qn("w:tblBorders")):
            pr.remove(old)
        b = OxmlElement("w:tblBorders")
        for side, val in (("top", "single"), ("left", "nil"), ("bottom", "single"), ("right", "nil"),
                          ("insideH", "single"), ("insideV", "nil")):
            e = OxmlElement(f"w:{side}")
            e.set(qn("w:val"), val)
            if val == "single":
                e.set(qn("w:sz"), "4")
                e.set(qn("w:space"), "0")
                e.set(qn("w:color"), "000000")
            b.append(e)
        pr.append(b)
    return doc


class JDoc(Doc):
    """Doc that also records each table (number, caption, data, note) for the standalone tables file."""
    def __init__(self, refs, inline_figs):
        super().__init__(refs, inline_figs)
        self.tables = []

    def table(self, n, caption, df, note=None):
        self.tables.append((n, self.refs.render(caption), df, self.refs.render(note) if note else None))
        return super().table(n, caption, df, note)


def tables_doc(D):
    """Standalone editable tables with the same captions and notes as the manuscript."""
    d = new_doc()
    for n, cap, df, note in D.tables:
        small(runs(d.add_paragraph(), f"Table {n}. {cap}", bold=True))
        t = d.add_table(rows=1, cols=len(df.columns))
        t.style = "Table Grid"
        for i, c in enumerate(df.columns):
            runs(t.rows[0].cells[i].paragraphs[0], str(c), size=9, bold=True)
        for _, r in df.iterrows():
            cells = t.add_row().cells
            for i, c in enumerate(df.columns):
                runs(cells[i].paragraphs[0], str(r[c]), size=9)
        if note:
            small(runs(d.add_paragraph(), note))
        d.add_paragraph()
    horizontal_rules_only(d).save(os.path.join(OUT, "tables.docx"))


def build(inline, v):
    refs = Refs()
    D = JDoc(refs, inline)
    body(D, v)
    if not inline:
        D.h("Figure captions")
        for n in sorted(CAPTIONS):
            small(D.p(f"Fig. {n}. {CAPTIONS[n][1]}", count=False))
    assert D.fig_seen == sorted(D.fig_seen) == list(range(1, len(CAPTIONS) + 1)), D.fig_seen
    assert D.tab_seen == [1, 2, 3, 4], D.tab_seen
    horizontal_rules_only(D.d)
    return D


def figures_pptx():
    """Editable PPTX, one figure per slide, scaled to fit inside the slide margins (wide figures fit by width)."""
    from PIL import Image
    from pptx import Presentation
    from pptx.util import Inches as PInches
    from pptx.util import Pt as PPt
    prs = Presentation()
    prs.slide_width, prs.slide_height = PInches(13.333), PInches(7.5)
    max_w, max_h = 12.5, 5.6
    for n in sorted(CAPTIONS):
        png = os.path.join(FIG, CAPTIONS[n][0] + ".png")
        w_px, h_px = Image.open(png).size
        w = min(max_w, max_h * w_px / h_px)
        h = w * h_px / w_px
        s = prs.slides.add_slide(prs.slide_layouts[6])
        s.shapes.add_picture(png, PInches((13.333 - w) / 2), PInches(0.3), width=PInches(w), height=PInches(h))
        tb = s.shapes.add_textbox(PInches(0.4), PInches(0.4 + h), PInches(12.5), PInches(7.1 - h)).text_frame
        tb.word_wrap = True
        tb.text = f"Fig. {n}. " + re.sub(r"[\^_]\{([^}]*)\}", r"\1", CAPTIONS[n][1])
        for par in tb.paragraphs:
            for r in par.runs:
                r.font.size = PPt(11)
    prs.save(os.path.join(OUT, "figures.pptx"))


def cover_letter(v, words):
    d = new_doc()
    d.styles["Normal"].font.name = "Times New Roman"
    paras = (
        f"{AUTHOR['name']}",
        f"{AUTHOR['affiliation']}",
        f"E-mail: {AUTHOR['email']}; ORCID: {AUTHOR['orcid']}",
        "Dear Editor,",
        f"I am submitting the enclosed Research Article, \"{TITLE}\", for consideration in the Journal of Space "
        "Safety Engineering.",
        "Several speculative debris-remediation concepts would act on the environment rather than on the debris "
        "object, for example by raising the thermospheric density along a target's path so that its drag increases. "
        "Such an intervention modifies a shared medium. Its safety screening therefore needs a quantity that "
        "object-directed removal does not: how much extra drag reaches objects outside the target population. My "
        "manuscript quantifies this non-target orbital-drag exposure for an idealized intervention and shows that "
        "the answer depends strongly on how the modified atmosphere is represented.",
        "I couple a physically self-consistent thermosphere model (GITM) directly to an orbit propagator and compare "
        "the cumulative extra drag of target and non-target objects with that implied by idealized static density "
        "patches flown along the same synthetic orbits. Over 12 h, the target/non-target drag ratio is about "
        f"{float(v['Sc_400']):.1f} at 400 km and {float(v['Sc_500']):.0f} at 500 km and close to one at 300 km, and "
        f"non-targets receive {v['sharec_400']}% and {v['sharec_500']}% of the extra drag of the synthetic sample at "
        "400 and 500 km. Static patches fitted to the GITM perturbation overstate the target/non-target contrast by "
        f"{v['gf_lo_12_400']}–{v['gf_hi_12_400']}-fold at 400 km and {v['gf_lo_12_500']}–{v['gf_hi_12_500']}-fold at "
        f"500 km, and a source-sized patch by {v['src_lo_400']}–{v['src_hi_500']}-fold. The 12 h selectivity changes "
        f"by at most {v['S_grid_max']}% when the horizontal resolution is doubled.",
        "I believe the work fits the journal's scope on space safety research and related environmental issues. It "
        "turns an atmospheric-physics result into a screening requirement: environment-directed remediation concepts "
        "should be assessed with a time-evolving atmosphere and should report non-target exposure, with the "
        "population and target definition stated, alongside the intended benefit. I am careful not to overstate "
        "this. Extra drag is treated as an exposure metric, not as collision probability, conjunction risk, "
        "manoeuvre burden or operational hazard, and the study claims no engineering feasibility.",
        "The study uses one model, one quiet-time background and two grid resolutions; it does not establish "
        "numerical convergence, multi-model agreement or observational validation, and the power and deposition "
        "dependences rest on two-level contrasts. My predictions were frozen before the heated runs and are scored "
        "in the paper, including those that failed. The code and processed model fields are publicly archived "
        "with checksums.",
        f"The manuscript has about {words} words including references, five figures and four tables. It has not "
        "been published and is not under consideration elsewhere. I declare no competing interests. The use of an "
        "AI software assistant is declared in the manuscript.",
        "Sincerely,", AUTHOR["name"])
    for t in paras:
        d.add_paragraph(t)
    d.save(os.path.join(OUT, "cover_letter.docx"))


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(os.path.join(OUT, "figures"), exist_ok=True)
    v = collect()
    fill_captions(v)
    t3 = CAPTIONS[3][1]
    old = "the non-target share of the total extra Δv (bottom)"
    assert old in t3
    CAPTIONS[3] = (CAPTIONS[3][0], t3.replace(old, "the non-target share of the total extra Δv of the synthetic "
                                                   "sample (bottom; Eq. (3))"))
    D = build(False, v)
    D.d.save(os.path.join(OUT, "manuscript.docx"))
    words = D.words
    assert words <= WORD_LIMIT, words
    build(True, v).d.save(os.path.join(OUT, "manuscript_review_inline.docx"))
    assert [t[0] for t in D.tables] == [1, 2, 3, 4]
    tables_doc(D)
    figures_pptx()
    hl = new_doc()
    hl.add_heading("Highlights", 1)
    for x in highlights(v):
        hl.add_paragraph(x, style="List Bullet")
    hl.save(os.path.join(OUT, "highlights.docx"))
    cover_letter(v, words)
    for n in sorted(CAPTIONS):
        shutil.copyfile(os.path.join(FIG, CAPTIONS[n][0] + ".tif"), os.path.join(OUT, "figures", f"Fig{n}.tif"))
    vals = pd.DataFrame(V.rows)
    vals.to_csv(os.path.join(ROOT, "results/manuscript_jsse_values.csv"), index=False)
    pd.DataFrame([dict(number=n, citation_key=k, reference=e) for n, k, e in D.refs.listing()]).to_csv(
        os.path.join(ROOT, "results/manuscript_jsse_citations.csv"), index=False)
    print(f"words (incl. refs, 300/figure-table): {words}; references: {len(D.refs.order)}; values: {len(V.rows)}")


if __name__ == "__main__":
    main()
