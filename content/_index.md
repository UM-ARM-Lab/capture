+++
title = "Particle-based Conformal Prediction for Contact-Aware Uncertainty Calibration in Stratified Configuration Spaces"
[extra]
display_title = "Particle-based Conformal Prediction for Contact-Aware Uncertainty Calibration in Stratified Configuration Spaces"
authors = [
    {name = "Luís Marques", url = "https://marquesluis.com/", contribution = true},
    {name = "Kristian Popov", url = "https://kris-popov.github.io/", contribution = true},
    {name = "Dmitry Berenson", url = "https://berenson.robotics.umich.edu/"}
]
contribution = "denotes equal contribution."
venue = {name = "15th Symposium on Conformal and Probabilistic Prediction with Applications (COPA) 2026", url = "https://copa-conference.com/"}
buttons = [
    {name = "ArXiv", url = "https://arxiv.org/abs/2608.09166"},
    {name = "PDF", url = "https://arxiv.org/pdf/2608.09166"},
    # {name = "Code", url = "https://github.com/UM-ARM-Lab/capture_code"}
]
katex = true
card = "hero_videos/center_capture_with_particles_1x1_card.png"
large_card = false
favicon = true
+++

<section class="capture-hero" aria-label="PCP and CaPTURe planning comparison">
<p class="capture-hero-caption">(Left) PCP calibrates particle uncertainty globally, making it optimistic in free-space and too conservative near contact. (Right) <strong>CaPTURe</strong> calibrates motion uncertainty conditioned on state, action, and the contact manifold, providing informative, adaptive uncertainty estimates for motion planners.</p>
<video autoplay muted loop controls playsinline preload="metadata" poster="./hero_videos/capture_vs_pcp_marble_hero_poster.jpg?v=20260816-four-peg-hero" data-capture-hero-video>
    <source src="./hero_videos/capture_vs_pcp_marble_hero.mp4?v=20260816-four-peg-hero" type="video/mp4">
</video>
<p class="capture-hero-legend" aria-live="polite" data-capture-hero-legend>
<span data-capture-hero-segment data-start="0" data-end="7.68">Blue particles show predicted future configurations, the translucent region shows the resulting uncertainty set, and the green flag marks the goal.</span>
<span data-capture-hero-segment data-start="7.68" hidden>The yellow peg is the controlled object, and the white fixture contains the insertion hole.</span>
</p>
</section>

<script>
(() => {
    const video = document.querySelector("[data-capture-hero-video]");
    const legend = document.querySelector("[data-capture-hero-legend]");
    if (!video || !legend) return;

    const segments = Array.from(legend.querySelectorAll("[data-capture-hero-segment]"));
    let activeSegment = null;

    const updateLegend = () => {
        const time = video.currentTime;
        const nextSegment = segments.find((segment) => {
            const start = Number(segment.dataset.start || 0);
            const end = segment.dataset.end ? Number(segment.dataset.end) : Infinity;
            return time >= start && time < end;
        }) || segments[segments.length - 1];

        if (!nextSegment || nextSegment === activeSegment) return;
        segments.forEach((segment) => {
            segment.hidden = segment !== nextSegment;
        });
        activeSegment = nextSegment;
    };

    video.addEventListener("loadedmetadata", updateLegend);
    video.addEventListener("timeupdate", updateLegend);
    video.addEventListener("seeked", updateLegend);
    video.addEventListener("ended", updateLegend);

    if ("IntersectionObserver" in window) {
        const observer = new IntersectionObserver(([entry]) => {
            if (entry.isIntersecting) {
                video.play().catch(() => {});
            } else {
                video.pause();
            }
        }, {threshold: 0.1});
        observer.observe(video);
    }

    updateLegend();
})();
</script>

<section class="capture-abstract" aria-label="Abstract">
<p><span class="capture-run-in-heading">Abstract</span> Reliable uncertainty representation is essential for deploying autonomous systems that interact with their environment, as robots must reason about how uncertainty arising from both <em>stochasticity</em> and <em>model mismatch</em> is impacted by contacts with obstacles (e.g., when navigating through a cluttered environment or inserting a part into an assembly). We propose <strong>Ca</strong>librated <strong>P</strong>article-sets for <strong>T</strong>rans-dimensional <strong>U</strong>ncertainty <strong>Re</strong>presentation (<strong>CaPTURe</strong>), a geometry-aware, conformal prediction-based algorithm that generates probabilistically valid prediction regions of the unknown future system configuration using particle-based models of arbitrary fidelity. While calibrated uncertainty predictions are essential for safe and efficient planning, analytical or learned motion models are often inaccurate&mdash;due to limited data, simplifying assumptions, unmodeled effects, etc.&mdash;which can lead to unsafe executions or task failure. Additionally, when a robot contacts an obstacle, the distribution of its future configurations can become <em>multimodal</em> or <em>disjoint</em>, or lie along manifolds of lower intrinsic dimension than the space of possible robot configurations. Our method uses a calibration dataset of system transitions to locally calibrate motion uncertainty estimates, constructing regions guaranteed to contain the future robot configuration at a user-set probability. Our calibration procedure captures how motion uncertainty varies between contact-rich and contactless motions, leading to sufficient coverage in both cases. We evaluate our method on two simulated planning tasks: controlling a marble around a labyrinth and performing tight-tolerance peg-in-hole insertion with a manipulator. Compared to relevant baselines, <strong>CaPTURe</strong> achieves the user-specified coverage requirement both in and out of contact and achieves up to a 30% absolute improvement in task success rate over the best baseline.</p>
</section>

# Problem Setup

Consider a discrete-time stochastic system with full configuration `$\mathfrak c_t \in \mathfrak C$`, state `$s_t := (\mathfrak c_t,\dot{\mathfrak c}_t)$`, action `$a_t \in \mathcal A$`, and unknown dynamics `$s_{t+1} \sim f(s_t,a_t)$`. We plan from `$s_0$` to a goal region using an approximate particle dynamics model `$\hat f$`. The prediction input is `$X := (s_t,a_t)$`, and its target `$Y := c_{t+1} \in C$` is the task-relevant projection of the next full configuration.

Given an exchangeable calibration set `$D_{\mathrm{cal}} := \{(X_i,Y_i)\}_{i=1}^{n}$`, we seek an informative input-dependent region `$\hat{\mathcal C}(X) \subseteq C_{\mathrm{feas}}$` with user-specified coverage. We model the feasible C-space as `$C_{\mathrm{feas}} := \bigsqcup_{m\in M} S_m$` with known stratum indexer `$\mathcal T:C_{\mathrm{feas}}\to M$`, so regions may span full-dimensional free space and lower-dimensional contact manifolds without containing infeasible configurations.

# Method: CaPTURe

CaPTURe calibrates the `$k_{\mathrm{NN}}$`-th-nearest-particle score within groups defined by state, action, and candidate future stratum. At inference, it queries every candidate stratum and unions the resulting feasible per-stratum regions. For a user-specified failure rate `$\alpha \in (0,1)$`, the union satisfies
```
$$
\mathbb P\!\left(c_{t+1} \in \hat{\mathcal C}\right) \ge 1 - \alpha.
$$
```
{% figure(alt=["Offline calibration diagram"] src=["./paper_figures/offline_calibration_dark_arxiv_v1.svg?v=20260816-vector-palette-v2"] dark_src=["./paper_figures/offline_calibration_dark_arxiv_v1.svg?v=20260816-vector-palette-v2"]) %}
**Offline calibration of CaPTURe.** For each transition in `$D_{\mathrm{cal}}$`, `$\hat f$` receives the current state `$s_t := (\mathfrak c_t,\dot{\mathfrak c}_t)$` and action `$a_t$` to sample `$L$` predictive particles (black) of the future configuration `$c_{t+1}$`, which we use to compute the nonconformity score `$R_i$` (pink). The augmented subset `$\bar D_{\mathrm{cal}}^{part}$` fits a regression decision tree that partitions state, action, and future stratum index `$\mathcal T(c_{t+1})$` into groups with approximately group-constant prediction scores. The holdout subset `$\bar D_{\mathrm{cal}}^{cp}$` is passed through the `DTree`, with each example landing in a corresponding group `$j$`. SplitCP is performed independently in each group, producing threshold `$\hat q_j$`.
{% end %}

{% figure(alt=["Prediction region construction diagram"] src=["./paper_figures/diagram_region_construction_dark_arxiv_v1.svg?v=20260816-vector-palette-v2"] dark_src=["./paper_figures/diagram_region_construction_dark_arxiv_v1.svg?v=20260816-vector-palette-v2"]) %}
**Construction of stratified prediction region `$\hat{\mathcal C}$`.** Given action `$a_t$` and state `$s_t := (\mathfrak c_t,\dot{\mathfrak c}_t)$`, `$\hat f$` returns predictive particles (black). For each stratum index `$m\in M$`, the pre-fit `DTree` maps `$(s_t,a_t,m)$` to a contact-aware threshold `$\hat q_j$`. Configurations in `$S_m$` whose `$k_{\mathrm{NN}}$`-th-particle distance is at most `$\hat q_j$` form that stratum's region. Their union is `$\hat{\mathcal C}$`.
{% end %}

# Experiments

## Marble Labyrinth Control

<p class="capture-section-lede">We simulate a planar marble control environment inspired by the BRIO labyrinth toy, where the task is to navigate a tight-clearance maze while avoiding known pit locations under aleatoric disturbances and significant model mismatch. The state is <code>$s_t=[x^b,\dot x^b,y^b,\dot y^b,\alpha,\beta]^\top$</code>, with board-fixed marble coordinates and plate inclination angles, and controls are motor velocities that tilt the board. We construct prediction regions over the 2D marble position <code>$c_t = [x^b, y^b]^\top$</code>. This task is challenging since the controls only indirectly influence marble location through plate tilt, causing delayed responses, momentum accumulation, and wall-shaped uncertainty when the dynamics are inaccurately modeled. The videos below compare rollouts produced by CaPTURe and the baselines across maze sections.</p>

<div class="inference-video-panel capture-video-picker" data-capture-video-picker data-video-template="./marble_videos/single/{map}_episode_{episode}_{method}.mp4">
    <div class="inference-picker-controls">
        <div class="inference-picker-group" aria-label="Marble map">
            <span class="inference-picker-label">Map</span>
            <div class="inference-picker-options" role="group">
                <button type="button" class="inference-option active" data-video-token="map" data-video-value="center" aria-pressed="true">Center</button>
                <button type="button" class="inference-option" data-video-token="map" data-video-value="center_right" aria-pressed="false">Center Right</button>
                <button type="button" class="inference-option" data-video-token="map" data-video-value="bottom_left" aria-pressed="false">Bottom Left</button>
                <button type="button" class="inference-option" data-video-token="map" data-video-value="bottom_right" aria-pressed="false">Bottom Right</button>
                <button type="button" class="inference-option" data-video-token="map" data-video-value="top_left" aria-pressed="false">Top Left</button>
                <button type="button" class="inference-option" data-video-token="map" data-video-value="top_center" aria-pressed="false">Top Center</button>
            </div>
        </div>
        <div class="inference-picker-group" aria-label="Marble episode">
            <span class="inference-picker-label">Episode</span>
            <div class="inference-picker-options" role="group">
                <button type="button" class="inference-option active" data-video-token="episode" data-video-value="00" aria-pressed="true">00</button>
                <button type="button" class="inference-option" data-video-token="episode" data-video-value="01" aria-pressed="false">01</button>
                <button type="button" class="inference-option" data-video-token="episode" data-video-value="02" aria-pressed="false">02</button>
                <button type="button" class="inference-option" data-video-token="episode" data-video-value="03" aria-pressed="false">03</button>
                <button type="button" class="inference-option" data-video-token="episode" data-video-value="04" aria-pressed="false">04</button>
                <button type="button" class="inference-option" data-video-token="episode" data-video-value="05" aria-pressed="false">05</button>
                <button type="button" class="inference-option" data-video-token="episode" data-video-value="06" aria-pressed="false">06</button>
                <button type="button" class="inference-option" data-video-token="episode" data-video-value="07" aria-pressed="false">07</button>
                <button type="button" class="inference-option" data-video-token="episode" data-video-value="08" aria-pressed="false">08</button>
                <button type="button" class="inference-option" data-video-token="episode" data-video-value="09" aria-pressed="false">09</button>
            </div>
        </div>
        <div class="inference-picker-group" aria-label="Marble method">
            <span class="inference-picker-label">Method</span>
            <div class="inference-picker-options" role="group">
                <button type="button" class="inference-option" data-video-token="method" data-video-value="particle_no_cp" aria-pressed="false">ParticleNoCP</button>
                <button type="button" class="inference-option" data-video-token="method" data-video-value="pcp" aria-pressed="false">PCP</button>
                <button type="button" class="inference-option" data-video-token="method" data-video-value="lucca" aria-pressed="false">LUCCa</button>
                <button type="button" class="inference-option" data-video-token="method" data-video-value="ablation_without_strata" aria-pressed="false">Ablation w/o stratum label (k<sub>NN</sub>=8)</button>
                <button type="button" class="inference-option" data-video-token="method" data-video-value="capture_knn1" aria-pressed="false">Ablation (k<sub>NN</sub>=1)</button>
                <button type="button" class="inference-option active" data-video-token="method" data-video-value="capture_knn8" aria-pressed="true"><strong>CaPTURe</strong> (k<sub>NN</sub>=8)</button>
            </div>
        </div>
    </div>
    <div class="inference-video-stage" data-capture-video-stage></div>
    <p class="inference-video-note" data-capture-video-note hidden>Video for this selection is not available yet.</p>
</div>

<div class="inference-video-panel capture-video-picker" data-capture-video-picker data-video-template="./marble_videos/all_runs/{map}_all_methods.mp4">
    <div class="inference-picker-controls">
        <div class="inference-picker-group" aria-label="Marble full-map rollout">
            <span class="inference-picker-label">Map</span>
            <div class="inference-picker-options" role="group">
                <button type="button" class="inference-option active" data-video-token="map" data-video-value="center" aria-pressed="true">Center</button>
                <button type="button" class="inference-option" data-video-token="map" data-video-value="center_right" aria-pressed="false">Center Right</button>
                <button type="button" class="inference-option" data-video-token="map" data-video-value="bottom_left" aria-pressed="false">Bottom Left</button>
                <button type="button" class="inference-option" data-video-token="map" data-video-value="bottom_right" aria-pressed="false">Bottom Right</button>
                <button type="button" class="inference-option" data-video-token="map" data-video-value="top_left" aria-pressed="false">Top Left</button>
                <button type="button" class="inference-option" data-video-token="map" data-video-value="top_center" aria-pressed="false">Top Center</button>
            </div>
        </div>
    </div>
    <div class="inference-video-stage" data-capture-video-stage></div>
    <p class="inference-video-note" data-capture-video-note hidden>Full-map video for this selection is not available yet.</p>
</div>

<p class="result-table-title">Aggregate planning results across six marble maze sections (180 trials per method).</p>
<div class="result-table-wrap capture-wide-table">
<table class="result-table marble-planning-table" aria-label="Aggregate planning results across six marble maze sections, 180 trials per method">
    <thead>
        <tr>
            <th>Map</th>
            <th class="metric-cell">Metric</th>
            <th class="narrow-col">ParticleNoCP</th>
            <th class="narrow-col">PCP</th>
            <th class="narrow-col">LUCCa</th>
            <th class="narrow-col">Ablation w/o stratum label<br>(<i>k</i><sub>NN</sub>=8)</th>
            <th class="narrow-col">Ablation<br>(<i>k</i><sub>NN</sub>=1)</th>
            <th class="narrow-col method-ours"><strong>CaPTURe</strong><br>(<i>k</i><sub>NN</sub>=8)</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <th rowspan="2">All six<br>maps</th>
            <th class="metric-cell">Success (%) &uarr;</th>
            <td>72.8</td><td>70.6</td><td>51.7</td><td>76.1</td><td>77.2</td><td><strong>91.1</strong></td>
        </tr>
        <tr>
            <th class="metric-cell">Steps to goal<br>(mean) &darr;</th>
            <td>13.2</td><td>13.9</td><td>28.5</td><td>14.8</td><td>16.3</td><td>15.6</td>
        </tr>
        <!-- The full per-map breakdown is reported in the paper.
        <tr>
            <th rowspan="2">Center<br>Right</th>
            <th class="metric-cell">Success (%) &uarr;</th>
            <td>83</td><td>87</td><td>57</td><td>83</td><td>90</td><td><strong>90</strong></td>
        </tr>
        <tr>
            <th class="metric-cell">Steps to goal<br>(mean &plusmn; std) &darr;</th>
            <td>13.8 &plusmn; 2.1</td><td>13.7 &plusmn; 1.6</td><td>33.2 &plusmn; 14.9</td><td>15.7 &plusmn; 2.1</td><td>19.0 &plusmn; 6.3</td><td>16.4 &plusmn; 4.3</td>
        </tr>
        <tr>
            <th rowspan="2">Bottom<br>Left</th>
            <th class="metric-cell">Success (%) &uarr;</th>
            <td>40</td><td>57</td><td>17</td><td>47</td><td>67</td><td><strong>73</strong></td>
        </tr>
        <tr>
            <th class="metric-cell">Steps to goal<br>(mean &plusmn; std) &darr;</th>
            <td>16.2 &plusmn; 3.0</td><td>16.4 &plusmn; 3.3</td><td>25.4 &plusmn; 5.0</td><td>18.5 &plusmn; 7.2</td><td>16.9 &plusmn; 3.6</td><td>23.1 &plusmn; 13.6</td>
        </tr>
        <tr>
            <th rowspan="2">Bottom<br>Right</th>
            <th class="metric-cell">Success (%) &uarr;</th>
            <td>93</td><td>100</td><td>67</td><td>97</td><td>100</td><td><strong>100</strong></td>
        </tr>
        <tr>
            <th class="metric-cell">Steps to goal<br>(mean &plusmn; std) &darr;</th>
            <td>14.5 &plusmn; 1.1</td><td>14.9 &plusmn; 1.1</td><td>60.0 &plusmn; 24.6</td><td>14.7 &plusmn; 1.1</td><td>15.2 &plusmn; 1.2</td><td>15.2 &plusmn; 2.0</td>
        </tr>
        <tr>
            <th rowspan="2">Top<br>Left</th>
            <th class="metric-cell">Success (%) &uarr;</th>
            <td>100</td><td>93</td><td>100</td><td>100</td><td>100</td><td><strong>100</strong></td>
        </tr>
        <tr>
            <th class="metric-cell">Steps to goal<br>(mean &plusmn; std) &darr;</th>
            <td>12.6 &plusmn; 1.3</td><td>12.8 &plusmn; 1.4</td><td>13.5 &plusmn; 1.2</td><td>12.5 &plusmn; 1.1</td><td>12.7 &plusmn; 0.9</td><td>12.5 &plusmn; 1.4</td>
        </tr>
        <tr>
            <th rowspan="2">Top<br>Center</th>
            <th class="metric-cell">Success (%) &uarr;</th>
            <td>67</td><td>83</td><td>70</td><td>73</td><td>100</td><td>93</td>
        </tr>
        <tr>
            <th class="metric-cell">Steps to goal<br>(mean &plusmn; std) &darr;</th>
            <td>12.3 &plusmn; 2.1</td><td>12.6 &plusmn; 2.1</td><td>17.0 &plusmn; 6.6</td><td>11.6 &plusmn; 1.7</td><td>13.7 &plusmn; 2.3</td><td>16.2 &plusmn; 4.4</td>
        </tr>
        -->
    </tbody>
</table>
</div>

<p class="table-note">Success means reaching the goal without falling into a pit. Aggregate percentages use all 180 executions per method; mean steps use successful trials only. An episode times out at step 100.</p>

## Manipulator Peg Insertion

<p class="capture-section-lede">We further evaluate CaPTURe on a tight-tolerance peg insertion task adapted from the <a href="https://research.nvidia.com/publication/2022-05_factory-fast-contact-robotic-assembly">Factory</a> simulation suite in Isaac Sim. We control a Franka Panda (7 DoF manipulator) to insert a cylindrical peg into a low-clearance hole under both stochastic disturbances and significant model mismatch. To facilitate contact-aware planning, we restrict end-effector motion to lie along the hole's plane, reducing possible peg poses from <code>$SE(3)$</code> to <code>$SE(2)$</code> and making the configuration of interest <code>$c_t = [x,z,\theta]$</code>.</p>

<p>The videos below show CaPTURe peg-insertion rollouts across several initial peg poses.</p>

<div class="inference-video-panel capture-video-picker peg-video-picker" data-capture-video-picker data-video-template="./peg_videos/w50_odin/{method}/{state}/inference_trace_combined_replay.mp4?v=20260814-05x">
    <div class="inference-picker-controls">
        <div class="inference-picker-group" aria-label="Manipulator initial condition">
            <span class="inference-picker-label">Initial peg pose</span>
            <div class="inference-picker-options" role="group">
                <button type="button" class="inference-option" data-video-token="state" data-video-value="state_000" data-pose-note="x₀ = 0 cm, z₀ = 4 cm, θ₀ = -12°" aria-pressed="false">00</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="state_001" data-pose-note="x₀ = -1.5 cm, z₀ = 5 cm, θ₀ = -4°" aria-pressed="false">01</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="state_002" data-pose-note="x₀ = 1.5 cm, z₀ = 3.33 cm, θ₀ = 4°" aria-pressed="false">02</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="state_003" data-pose-note="x₀ = -2.25 cm, z₀ = 4.33 cm, θ₀ = 12°" aria-pressed="false">03</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="state_004" data-pose-note="x₀ = 0.75 cm, z₀ = 5.33 cm, θ₀ = -18.4°" aria-pressed="false">04</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="state_005" data-pose-note="x₀ = -0.75 cm, z₀ = 3.67 cm, θ₀ = -10.4°" aria-pressed="false">05</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="state_006" data-pose-note="x₀ = 2.25 cm, z₀ = 4.67 cm, θ₀ = -2.4°" aria-pressed="false">06</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="state_007" data-pose-note="x₀ = -2.62 cm, z₀ = 5.67 cm, θ₀ = 5.6°" aria-pressed="false">07</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="state_008" data-pose-note="x₀ = 0.375 cm, z₀ = 3.11 cm, θ₀ = 13.6°" aria-pressed="false">08</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="state_009" data-pose-note="x₀ = -1.12 cm, z₀ = 4.11 cm, θ₀ = -16.8°" aria-pressed="false">09</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="state_010" data-pose-note="x₀ = 1.88 cm, z₀ = 5.11 cm, θ₀ = -8.8°" aria-pressed="false">10</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="state_011" data-pose-note="x₀ = -1.88 cm, z₀ = 3.44 cm, θ₀ = -0.8°" aria-pressed="false">11</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="state_012" data-pose-note="x₀ = 1.12 cm, z₀ = 4.44 cm, θ₀ = 7.2°" aria-pressed="false">12</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="state_013" data-pose-note="x₀ = -0.375 cm, z₀ = 5.44 cm, θ₀ = 15.2°" aria-pressed="false">13</button>
                <button type="button" class="inference-option active" data-video-token="state" data-video-value="state_014" data-pose-note="x₀ = 2.62 cm, z₀ = 3.78 cm, θ₀ = -15.2°" aria-pressed="true">14</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="state_015" data-pose-note="x₀ = -2.81 cm, z₀ = 4.78 cm, θ₀ = -7.2°" aria-pressed="false">15</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="state_016" data-pose-note="x₀ = 0.188 cm, z₀ = 5.78 cm, θ₀ = 0.8°" aria-pressed="false">16</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="state_017" data-pose-note="x₀ = -1.31 cm, z₀ = 3.22 cm, θ₀ = 8.8°" aria-pressed="false">17</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="state_018" data-pose-note="x₀ = 1.69 cm, z₀ = 4.22 cm, θ₀ = 16.8°" aria-pressed="false">18</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="state_019" data-pose-note="x₀ = -2.06 cm, z₀ = 5.22 cm, θ₀ = -13.6°" aria-pressed="false">19</button>
            </div>
        </div>
        <div class="inference-picker-group" aria-label="Manipulator method">
            <span class="inference-picker-label">Method</span>
            <div class="inference-picker-options" role="group">
                <button type="button" class="inference-option" data-video-token="method" data-video-value="particle_nocp" aria-pressed="false">ParticleNoCP</button>
                <button type="button" class="inference-option" data-video-token="method" data-video-value="pcp" aria-pressed="false">PCP</button>
                <button type="button" class="inference-option" data-video-token="method" data-video-value="lucca" aria-pressed="false">LUCCa</button>
                <button type="button" class="inference-option" data-video-token="method" data-video-value="kth_nn_locart_k4" aria-pressed="false">Ablation w/o stratum label (k<sub>NN</sub>=4)</button>
                <button type="button" class="inference-option" data-video-token="method" data-video-value="min_stratcp_factory_shaved_bounds2" aria-pressed="false">Ablation (k<sub>NN</sub>=1)</button>
                <button type="button" class="inference-option active" data-video-token="method" data-video-value="kth_nn_stratcp_k4_factory_shaved_bounds2_friction01_leaf200_depth8" aria-pressed="true"><strong>CaPTURe</strong> (k<sub>NN</sub>=4)</button>
            </div>
        </div>
    </div>
    <div class="inference-video-stage" data-capture-video-stage></div>
    <p class="inference-video-note" data-capture-video-note hidden>Video for this selection is not available yet.</p>
</div>

<p>The synchronized comparison below shows the physical execution for all six methods from the same initial peg pose.</p>

<div class="inference-video-panel capture-video-picker peg-video-picker" data-capture-video-picker data-video-template="./peg_videos/w50_odin_all_methods/state_{state}_all_methods_physical.mp4?v=20260815-compact-labels">
    <div class="inference-picker-controls">
        <div class="inference-picker-group" aria-label="Manipulator comparison initial condition">
            <span class="inference-picker-label">Initial peg pose</span>
            <div class="inference-picker-options" role="group">
                <button type="button" class="inference-option" data-video-token="state" data-video-value="000" data-pose-note="x₀ = 0 cm, z₀ = 4 cm, θ₀ = -12°" aria-pressed="false">00</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="001" data-pose-note="x₀ = -1.5 cm, z₀ = 5 cm, θ₀ = -4°" aria-pressed="false">01</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="002" data-pose-note="x₀ = 1.5 cm, z₀ = 3.33 cm, θ₀ = 4°" aria-pressed="false">02</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="003" data-pose-note="x₀ = -2.25 cm, z₀ = 4.33 cm, θ₀ = 12°" aria-pressed="false">03</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="004" data-pose-note="x₀ = 0.75 cm, z₀ = 5.33 cm, θ₀ = -18.4°" aria-pressed="false">04</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="005" data-pose-note="x₀ = -0.75 cm, z₀ = 3.67 cm, θ₀ = -10.4°" aria-pressed="false">05</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="006" data-pose-note="x₀ = 2.25 cm, z₀ = 4.67 cm, θ₀ = -2.4°" aria-pressed="false">06</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="007" data-pose-note="x₀ = -2.62 cm, z₀ = 5.67 cm, θ₀ = 5.6°" aria-pressed="false">07</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="008" data-pose-note="x₀ = 0.375 cm, z₀ = 3.11 cm, θ₀ = 13.6°" aria-pressed="false">08</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="009" data-pose-note="x₀ = -1.12 cm, z₀ = 4.11 cm, θ₀ = -16.8°" aria-pressed="false">09</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="010" data-pose-note="x₀ = 1.88 cm, z₀ = 5.11 cm, θ₀ = -8.8°" aria-pressed="false">10</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="011" data-pose-note="x₀ = -1.88 cm, z₀ = 3.44 cm, θ₀ = -0.8°" aria-pressed="false">11</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="012" data-pose-note="x₀ = 1.12 cm, z₀ = 4.44 cm, θ₀ = 7.2°" aria-pressed="false">12</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="013" data-pose-note="x₀ = -0.375 cm, z₀ = 5.44 cm, θ₀ = 15.2°" aria-pressed="false">13</button>
                <button type="button" class="inference-option active" data-video-token="state" data-video-value="014" data-pose-note="x₀ = 2.62 cm, z₀ = 3.78 cm, θ₀ = -15.2°" aria-pressed="true">14</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="015" data-pose-note="x₀ = -2.81 cm, z₀ = 4.78 cm, θ₀ = -7.2°" aria-pressed="false">15</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="016" data-pose-note="x₀ = 0.188 cm, z₀ = 5.78 cm, θ₀ = 0.8°" aria-pressed="false">16</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="017" data-pose-note="x₀ = -1.31 cm, z₀ = 3.22 cm, θ₀ = 8.8°" aria-pressed="false">17</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="018" data-pose-note="x₀ = 1.69 cm, z₀ = 4.22 cm, θ₀ = 16.8°" aria-pressed="false">18</button>
                <button type="button" class="inference-option" data-video-token="state" data-video-value="019" data-pose-note="x₀ = -2.06 cm, z₀ = 5.22 cm, θ₀ = -13.6°" aria-pressed="false">19</button>
            </div>
        </div>
    </div>
    <div class="inference-video-stage" data-capture-video-stage></div>
    <p class="inference-video-note" data-capture-video-note hidden>Video for this selection is not available yet.</p>
</div>

<p class="result-table-title">Peg-insertion planning over 50 feasible Halton initial configurations.</p>
<div class="result-table-wrap capture-compact-table">
<table class="result-table peg-planning-table" aria-label="Peg-insertion planning results over 50 feasible Halton initial configurations">
    <thead>
        <tr>
            <th class="metric-cell">Metric</th>
            <th class="narrow-col">ParticleNoCP</th>
            <th class="narrow-col">PCP</th>
            <th class="narrow-col">LUCCa</th>
            <th class="narrow-col">Ablation w/o stratum label<br>(<i>k</i><sub>NN</sub>=4)</th>
            <th class="narrow-col">Ablation<br>(<i>k</i><sub>NN</sub>=1)</th>
            <th class="narrow-col method-ours"><strong>CaPTURe</strong><br>(<i>k</i><sub>NN</sub>=4)</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <th class="metric-cell">Success (%) &uarr;</th>
            <td>14</td>
            <td>48</td>
            <td>48</td>
            <td>48</td>
            <td>20</td>
            <td><strong>78</strong></td>
        </tr>
        <tr>
            <th class="metric-cell">Steps to insertion<br>(mean &plusmn; std) &darr;</th>
            <td>39.9 &plusmn; 13.3</td>
            <td>38.4 &plusmn; 13.9</td>
            <td>41.5 &plusmn; 16.6</td>
            <td>43.1 &plusmn; 15.9</td>
            <td>36.2 &plusmn; 16.4</td>
            <td><strong>28.7 &plusmn; 8.9</strong></td>
        </tr>
    </tbody>
</table>
</div>

<p class="table-note">Success denotes full insertion within 75 controller steps (5.0 simulated seconds). Steps are reported over successful episodes only.</p>

<script>
(() => {
    const setupPicker = (picker) => {
        const buttons = [...picker.querySelectorAll("[data-video-src], [data-video-token]")];
        const stage = picker.querySelector("[data-capture-video-stage]");
        const note = picker.querySelector("[data-capture-video-note]");
        const poseNote = picker.querySelector("[data-capture-pose-note]");
        if (!buttons.length || !stage || !note) return;

        let activeVideo = null;
        let activeSrc = "";
        let stageIsVisible = false;
        const videoCache = new Map();

        const setActiveButton = (selectedButton) => {
            const token = selectedButton.dataset.videoToken;
            const groupButtons = token ? buttons.filter((button) => button.dataset.videoToken === token) : buttons;

            groupButtons.forEach((button) => {
                const isActive = button === selectedButton;
                button.classList.toggle("active", isActive);
                button.setAttribute("aria-pressed", String(isActive));
            });
        };

        const updatePoseNote = () => {
            if (!poseNote) return;

            const selectedPose = picker.querySelector("[data-pose-note].active");
            const poseText = selectedPose?.dataset.poseNote ?? "";
            poseNote.textContent = poseText;
            poseNote.hidden = !poseText;
        };

        const getSelectedTokens = () => {
            const tokens = {};
            picker.querySelectorAll("[data-video-token]").forEach((button) => {
                const token = button.dataset.videoToken;
                if (!token) return;

                if (button.classList.contains("active") || tokens[token] === undefined) {
                    tokens[token] = button.dataset.videoValue ?? "";
                }
            });
            return tokens;
        };

        const getSelectedSrc = () => {
            const template = picker.dataset.videoTemplate;
            if (!template) {
                const activeButton = buttons.find((button) => button.classList.contains("active")) || buttons[0];
                return activeButton?.dataset.videoSrc ?? "";
            }

            const tokens = getSelectedTokens();
            return template.replace(/\{([a-zA-Z0-9_]+)\}/g, (_, key) => tokens[key] ?? "");
        };

        const hideActiveVideo = () => {
            if (!activeVideo) return;
            activeVideo.pause();
            activeVideo.classList.remove("active");
            activeVideo.setAttribute("aria-hidden", "true");
            activeVideo = null;
            activeSrc = "";
        };

        const updatePlayback = () => {
            if (!activeVideo) return;

            if (!stageIsVisible) {
                activeVideo.pause();
                return;
            }

            const playPromise = activeVideo.play();
            if (playPromise !== undefined) {
                playPromise.catch(() => {});
            }
        };

        const showVideo = (video, src) => {
            if (activeVideo && activeVideo !== video) {
                activeVideo.pause();
                activeVideo.classList.remove("active");
                activeVideo.setAttribute("aria-hidden", "true");
            }
            video.classList.add("active");
            video.removeAttribute("aria-hidden");
            activeVideo = video;
            activeSrc = src;
            note.hidden = true;
            updatePlayback();
        };

        const createVideo = (src) => {
            if (videoCache.has(src)) return videoCache.get(src);

            const video = document.createElement("video");
            video.className = "inference-comparison-video";
            video.controls = true;
            video.loop = true;
            video.muted = true;
            video.playsInline = true;
            video.preload = "metadata";
            video.src = src;
            video.setAttribute("aria-hidden", "true");
            video.addEventListener("canplay", () => {
                if (activeSrc === src || !activeSrc) {
                    showVideo(video, src);
                }
            });
            video.addEventListener("error", () => {
                if (activeSrc === src || !activeSrc) {
                    hideActiveVideo();
                    note.hidden = false;
                }
            });
            stage.appendChild(video);
            videoCache.set(src, video);
            return video;
        };

        const selectVideo = (button) => {
            setActiveButton(button);
            updatePoseNote();
            const src = getSelectedSrc();
            if (!src) return;

            note.hidden = true;
            activeSrc = src;
            const video = createVideo(src);
            if (video.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA) {
                showVideo(video, src);
            } else {
                video.load();
            }
        };

        buttons.forEach((button) => {
            button.addEventListener("click", () => {
                hasLoadedVideo = true;
                selectVideo(button);
            });
        });

        let hasLoadedVideo = false;
        const loadInitialVideo = () => {
            if (hasLoadedVideo) return;

            hasLoadedVideo = true;
            const initialButton = buttons.find((button) => button.classList.contains("active")) || buttons[0];
            if (initialButton) {
                selectVideo(initialButton);
            }
        };

        if ("IntersectionObserver" in window) {
            const visibilityObserver = new IntersectionObserver(([entry]) => {
                stageIsVisible = entry.isIntersecting;
                updatePlayback();
            }, {threshold: 0.1});
            visibilityObserver.observe(stage);

            const preloadObserver = new IntersectionObserver((entries) => {
                if (!entries.some((entry) => entry.isIntersecting)) return;

                preloadObserver.disconnect();
                loadInitialVideo();
            }, {rootMargin: "120px 0px"});
            preloadObserver.observe(picker);
        } else {
            stageIsVisible = true;
            loadInitialVideo();
        }
    };

    document.querySelectorAll("[data-capture-video-picker]").forEach(setupPicker);
})();
</script>

<p class="acknowledgment">This work was supported in part by the Office of Naval Research Grant N00014-24-1-2036 and NSF grants IIS-2113401 and IIS-2220876.</p>

# BibTeX <small><small>(cite this!)</small></small>

<div class="bibtex-copy-container">
    <button id="bibtex-copy-button" type="button" aria-label="Copy BibTeX to clipboard">
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
            <path d="M16 1H4a2 2 0 0 0-2 2v12h2V3h12V1zm3 4H8a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2zm0 16H8V7h11v14z"/>
        </svg>
        <span>Copy to clipboard</span>
    </button>
    <pre id="bibtex-content"><code>@misc{marques2026particlebasedconformalpredictioncontactaware,
      title={Particle-Based Conformal Prediction for Contact-Aware Uncertainty Calibration in Stratified Configuration Spaces},
      author={Luís Marques and Kristian Popov and Dmitry Berenson},
      year={2026},
      eprint={2608.09166},
      archivePrefix={arXiv},
      primaryClass={cs.RO},
      url={https://arxiv.org/abs/2608.09166},
}</code></pre>
</div>

<script>
(() => {
    const copyButton = document.getElementById("bibtex-copy-button");
    const bibtexContent = document.getElementById("bibtex-content");
    if (!copyButton || !bibtexContent) return;

    const defaultText = "Copy to clipboard";
    const setButtonLabel = (label) => {
        const textSpan = copyButton.querySelector("span");
        if (textSpan) textSpan.textContent = label;
    };

    copyButton.addEventListener("click", () => {
        const bibtexText = bibtexContent.textContent ?? "";
        if (!navigator.clipboard || !navigator.clipboard.writeText) {
            setButtonLabel("Clipboard not available");
            setTimeout(() => setButtonLabel(defaultText), 3000);
            return;
        }

        navigator.clipboard.writeText(bibtexText).then(() => {
            setButtonLabel("Copied!");
            setTimeout(() => setButtonLabel(defaultText), 3000);
        }).catch(() => {
            setButtonLabel("Copy failed");
            setTimeout(() => setButtonLabel(defaultText), 3000);
        });
    });
})();
</script>
