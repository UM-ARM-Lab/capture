+++
title = "Particle-based Conformal Prediction for Contact-Aware Uncertainty Calibration in Stratified Configuration Spaces"
[extra]
display_title = "Particle-based Conformal Prediction for Contact-Aware Uncertainty Calibration in Stratified Configuration Spaces"
authors = [
    {name = "Luís Marques", url = "https://marquesluis.com/", contribution = true},
    {name = "Kristian Popov", url = "https://www.linkedin.com/in/kristian-c-popov/", contribution = true},
    {name = "Dmitry Berenson", url = "https://berenson.robotics.umich.edu/"}
]
contribution = "denotes equal contribution."
venue = {name = "Under Review"}
buttons = [
    # {name = "ArXiv", url = ""},
    # {name = "PDF", url = ""},
    # {name = "Code", url = "https://github.com/UM-ARM-Lab/capture_code"}
]
katex = true
card = "hero_videos/center_capture_with_particles_1x1_card.png"
large_card = false
favicon = true
+++

<!--
<div class="capture-hero-video-grid capture-hero-video-single" aria-label="CaPTURe demonstration video">
    <div class="capture-hero-video-slot">
        Replace this placeholder with the final combined demo clip, e.g. static/hero_videos/capture_overview.mp4.
        <div class="capture-hero-placeholder">Combined marble + manipulator video</div>
        <span class="capture-hero-label">CaPTURe demos</span>
    </div>
</div>
-->

<section class="capture-abstract" aria-label="Abstract">
<p><span class="capture-run-in-heading">Abstract</span> Reliable uncertainty representation is essential for deploying autonomous systems that interact with their environment, as robots must reason about how uncertainty arising from both <em>stochasticity</em> and <em>model mismatch</em> is impacted by contacts with obstacles (e.g., when navigating through a cluttered environment or inserting a part into an assembly). We propose <strong>Ca</strong>librated <strong>P</strong>article-sets for <strong>T</strong>rans-dimensional <strong>U</strong>ncertainty <strong>Re</strong>presentation (<strong>CaPTURe</strong>), a geometry-aware, conformal prediction-based algorithm that generates probabilistically-valid prediction regions of the unknown future system configuration using particle-based models of arbitrary fidelity. While calibrated uncertainty predictions are essential for safe and efficient planning, analytical or learned motion models are often inaccurate - due to limited data, simplifying assumptions, unmodeled effects, etc. - which can lead to unsafe executions or task failure. Additionally, when a robot contacts an obstacle, the distribution of its future configurations can become <em>multi-modal</em>, <em>disjoint</em>, and can lie along manifolds of lower intrinsic dimension than the space of possible robot configurations. Our method uses a calibration dataset of system transitions to locally calibrate motion uncertainty estimates, constructing regions guaranteed to contain the future robot configuration at a user-set likelihood. Our calibration procedure captures how motion uncertainty varies between contact-rich and contactless motions, leading to sufficient coverage in both cases. We evaluate our method on two simulated planning tasks: controlling a marble around a labyrinth and tight-tolerance peg-in-hole insertion by a manipulator in simulation. Compared to relevant baselines, <strong>CaPTURe</strong> achieves the user-specified coverage requirement, when both in and out of contact, and leads to executions that are up to 37% more successful.</p>
</section>

# Problem Setup

Consider a discrete-time stochastic system with configuration `$\mathfrak c_t \in \mathfrak C$`, state `$s_t := (\mathfrak c_t,\dot{\mathfrak c}_t)$`, action `$u_t \in \mathcal U$`, and *unknown* dynamics `$s_{t+1} \sim f(s_t,u_t)$`. We consider the problem of moving this robot, safely and efficiently, from an initial state `$s_0$` to a goal region in a known environment using an approximate particle-based dynamics model `$\hat f$` of arbitrary fidelity. During planning, we can use the current state and 
action `$X := (s_t,u_t) = (\mathfrak c_t,\dot{\mathfrak c}_t,u_t)$` to predict the future configuration `$Y := c_{t+1}$`. Yet, `$\hat f$`'s predictions can be unreliable due to aleatoric disturbances, epistemic model mismatch, and contact-induced changes in feasible motion. To support uncertainty-aware planning and control under contact, we construct calibrated prediction regions over `$C \subseteq \mathfrak C$` a task-relevant subset of the configuration space --- `$c_t \subseteq \mathfrak c_t$` denotes the corresponding task-relevant robot configurations. 

Given a finite exchangeable calibration set `$D_{\mathrm{cal}} := \{(X_i,Y_i)\}_{i=1}^{n}$`, our aim is to construct an input-dependent prediction region `$\hat{\mathcal C} \subseteq C$` that is calibrated, informative for planning, and constrained to feasible configurations -- `$\hat{\mathcal C}(X) \cap \mathcal C_{\mathrm{infeasible}} = \emptyset$`. We model `$C$` as a finite stratified space `$C := \bigsqcup_{m\in M} S_m$` with known stratum indexer `$\mathcal T:C \to \{1,\ldots,|M|\}$`, allowing feasible configurations to include free-space regions as well as lower-dimensional contact manifolds, such as wall-contact edges and corner contacts.

# Method: CaPTURe

Given a user-specified acceptable failure-rate `$\alpha \in (0,1)$`, CaPTURe constructs a state-action-stratum dependent prediction region `$\hat{\mathcal C} \subseteq C$`, such that
```
$$
\mathbb P\!\left(c_{t+1} \in \hat{\mathcal C}\right) \ge 1 - \alpha.
$$
```
The resulting prediction region `$\hat{\mathcal C} = \bigcup_{S_m \in \mathcal S} \hat{\mathcal C}_{S_m}(s_t,u_t,S_m) \subseteq C$` is a union of regions built over the robot's configuration strata.

{% figure(alt=["Offline calibration diagram"] src=["./paper_figures/offline_calibration_dark.png"] dark_src=["./paper_figures/offline_calibration_dark.png"]) %}
**Offline calibration of CaPTURe.** For each transition in `$D_{\mathrm{cal}}$`, `$\hat f$` receives the current full-system state `$s_t := (\mathfrak{c}_t,\dot{\mathfrak{c}}_t)$` and action `$u_t$` to sample `$L$` predictive particles (black) of the future target configuration `$c_{t+1}$` which we use to compute the nonconformity score `$R_i$` (blue). A subset of transition-scores `$D_{\mathrm{cal}}^{part}$` is used to fit a regression decision-tree that separates the input space -- state, velocity and future strata `$S(c_{t+1})$` -- into groups with approximately group-constant prediction score. The holdout subset `$D_{\mathrm{cal}}^{cp}$` is then passed through the `DTree` with each example landing in a leaf node and hence corresponding group `$k$`. SplitCP is performed independently for each group, resulting in a per-partition conformal threshold `$\hat q_k$`.
{% end %}

{% figure(alt=["Prediction region construction diagram"] src=["./paper_figures/diagram_region_construction_dark.png"] dark_src=["./paper_figures/diagram_region_construction_dark.png"]) %}
**Construction of stratified prediction region `$\hat{\mathcal C}$`.** Given an action `$u_t$` and current full-system state `$s_t := (\mathfrak{c}_t,\dot{\mathfrak{c}}_t)$` the predictive model `$\hat f$` returns predictive particles (black) representing possible future target configurations. For each candidate future stratum `$(S_m)$` in C-space, we query the pre-fit `DTree` with `$(s_t,u_t,S_m)$` to get a contact-aware uncertainty threshold `$\hat q_k$`. For each stratum, we evaluate which configurations in `$S_m$` have score `$\le \hat q_k$`, where the score is the `$k$`-th distance between a candidate configuration in `$S_m$` and the particles. Finally, we compose the full prediction region `$\hat{\mathcal C}(s_t,u_t,\mathcal S)$` as the union of the per-stratum regions over candidate future strata `$S_m \in \mathcal S$`.
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
                <button type="button" class="inference-option" data-video-token="method" data-video-value="ablation_without_strata" aria-pressed="false">Ablation: no strata label (k<sub>NN</sub>=8)</button>
                <button type="button" class="inference-option" data-video-token="method" data-video-value="capture_knn1" aria-pressed="false"><strong>CaPTURe</strong> (ours, k<sub>NN</sub>=1)</button>
                <button type="button" class="inference-option active" data-video-token="method" data-video-value="capture_knn8" aria-pressed="true"><strong>CaPTURe</strong> (ours, k<sub>NN</sub>=8)</button>
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

## Manipulator Peg Insertion

<p class="capture-section-lede">We further evaluate CaPTURe on a tight-tolerance peg insertion task adapted from the <a href="https://research.nvidia.com/publication/2022-05_factory-fast-contact-robotic-assembly">Factory</a> simulation suite in Isaac Sim. We control a Franka Panda (7 DoF manipulator) to insert a cylindrical peg into a low-clearance hole under both stochastic disturbances and significant model mismatch. To facilitate contact-aware planning, we restrict end-effector motion to lie along the hole's plane, reducing possible peg poses from <code>$SE(3)$</code> to <code>$SE(2)$</code> and making the configuration of interest <code>$c_t = [x,z,\theta]$</code>. The videos below compare single-episode and all-method rollouts across initial peg poses.</p>

<div class="inference-video-panel capture-video-picker" data-capture-video-picker data-video-template="./manipulator_videos/single/{initial_condition}_episode_{episode}_{method}.mp4">
    <div class="inference-picker-controls">
        <div class="inference-picker-group" aria-label="Manipulator initial condition">
            <span class="inference-picker-label">Initial peg pose</span>
            <div class="inference-picker-options" role="group">
                <button type="button" class="inference-option active" data-video-token="initial_condition" data-video-value="c01" aria-pressed="true"><code>$c_{0,1}$</code></button>
                <button type="button" class="inference-option" data-video-token="initial_condition" data-video-value="c02" aria-pressed="false"><code>$c_{0,2}$</code></button>
                <button type="button" class="inference-option" data-video-token="initial_condition" data-video-value="c03" aria-pressed="false"><code>$c_{0,3}$</code></button>
                <button type="button" class="inference-option" data-video-token="initial_condition" data-video-value="random" aria-pressed="false">Random</button>
            </div>
        </div>
        <div class="inference-picker-group" aria-label="Manipulator episode">
            <span class="inference-picker-label">Episode</span>
            <div class="inference-picker-options" role="group">
                <button type="button" class="inference-option active" data-video-token="episode" data-video-value="00" aria-pressed="true">00</button>
                <button type="button" class="inference-option" data-video-token="episode" data-video-value="01" aria-pressed="false">01</button>
                <button type="button" class="inference-option" data-video-token="episode" data-video-value="02" aria-pressed="false">02</button>
                <button type="button" class="inference-option" data-video-token="episode" data-video-value="03" aria-pressed="false">03</button>
                <button type="button" class="inference-option" data-video-token="episode" data-video-value="04" aria-pressed="false">04</button>
            </div>
        </div>
        <div class="inference-picker-group" aria-label="Manipulator method">
            <span class="inference-picker-label">Method</span>
            <div class="inference-picker-options" role="group">
                <button type="button" class="inference-option" data-video-token="method" data-video-value="particle_no_cp" aria-pressed="false">ParticleNoCP</button>
                <button type="button" class="inference-option" data-video-token="method" data-video-value="pcp" aria-pressed="false">PCP</button>
                <button type="button" class="inference-option" data-video-token="method" data-video-value="lucca" aria-pressed="false">LUCCa</button>
                <button type="button" class="inference-option" data-video-token="method" data-video-value="ablation_without_strata" aria-pressed="false">Ablation: no strata label (k<sub>NN</sub>=4)</button>
                <button type="button" class="inference-option" data-video-token="method" data-video-value="capture_knn1" aria-pressed="false"><strong>CaPTURe</strong> (ours, k<sub>NN</sub>=1)</button>
                <button type="button" class="inference-option active" data-video-token="method" data-video-value="capture_knn4" aria-pressed="true"><strong>CaPTURe</strong> (ours, k<sub>NN</sub>=4)</button>
            </div>
        </div>
    </div>
    <div class="inference-video-stage" data-capture-video-stage></div>
    <p class="inference-video-note" data-capture-video-note hidden>Video for this selection is not available yet.</p>
</div>

<div class="inference-video-panel capture-video-picker" data-capture-video-picker data-video-template="./manipulator_videos/all_runs/{initial_condition}_all_methods.mp4">
    <div class="inference-picker-controls">
        <div class="inference-picker-group" aria-label="Manipulator full initial-condition rollout">
            <span class="inference-picker-label">Initial peg pose</span>
            <div class="inference-picker-options" role="group">
                <button type="button" class="inference-option active" data-video-token="initial_condition" data-video-value="c01" aria-pressed="true"><code>$c_{0,1}$</code></button>
                <button type="button" class="inference-option" data-video-token="initial_condition" data-video-value="c02" aria-pressed="false"><code>$c_{0,2}$</code></button>
                <button type="button" class="inference-option" data-video-token="initial_condition" data-video-value="c03" aria-pressed="false"><code>$c_{0,3}$</code></button>
                <button type="button" class="inference-option" data-video-token="initial_condition" data-video-value="random" aria-pressed="false">Random</button>
            </div>
        </div>
    </div>
    <div class="inference-video-stage" data-capture-video-stage></div>
    <p class="inference-video-note" data-capture-video-note hidden>Full initial-condition video for this selection is not available yet.</p>
</div>

<script>
(() => {
    const setupPicker = (picker) => {
        const buttons = [...picker.querySelectorAll("[data-video-src], [data-video-token]")];
        const stage = picker.querySelector("[data-capture-video-stage]");
        const note = picker.querySelector("[data-capture-video-note]");
        if (!buttons.length || !stage || !note) return;

        let activeVideo = null;
        let activeSrc = "";
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
            const playPromise = video.play();
            if (playPromise !== undefined) {
                playPromise.catch(() => {});
            }
        };

        const createVideo = (src) => {
            if (videoCache.has(src)) return videoCache.get(src);

            const video = document.createElement("video");
            video.className = "inference-comparison-video";
            video.autoplay = true;
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
            button.addEventListener("click", () => selectVideo(button));
        });

        const initialButton = buttons.find((button) => button.classList.contains("active")) || buttons[0];
        if (initialButton) {
            selectVideo(initialButton);
        }
    };

    document.querySelectorAll("[data-capture-video-picker]").forEach(setupPicker);
})();
</script>
