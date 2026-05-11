+++
title = "Local Conformal Calibration of Dynamics Uncertainty from Semantic Images"
[extra]
display_title = "Local Conformal Calibration of Dynamics Uncertainty from Semantic Images "
authors = [
    {name = "Luís Marques", url = "https://marquesluis.com/"},
    {name = "Dmitry Berenson", url = "https://berenson.robotics.umich.edu/"}
]
venue = {name = "17th International Workshop on the Algorithmic Foundations of Robotics (WAFR) 2026", url = "https://algorithmic-robotics.org/"}
buttons = [
    # {name = "ArXiv", url = ""},
    # {name = "PDF", url = ""},
    # {name = "Code", url = "https://github.com/UM-ARM-Lab/ocular_code"}
]
katex = true
large_card = true
favicon = true
+++

<!-- <div class="abstract-with-figure"> -->

<!-- <div class="text-column"> -->

We introduce **O**bservation-aware **C**onformal **U**ncertainty **L**ocal-C**a**lib**r**ation (**OCULAR**), a conformal prediction-based algorithm that uses perceptual information to provide uncertainty quantification guarantees for unseen test-time environments. While previous conformal approaches lack the ability to discriminate between state-action space regions leading to higher or lower model mismatch, and require environment-specific data, our method uses data collected from visually similar environments to provably calibrate a given linear Gaussian dynamics model of arbitrary fidelity. The prediction regions generated from **OCULAR** are guaranteed to contain the future system states with, at least, a user-set likelihood, despite both aleatoric and epistemic uncertainty—i.e., uncertainty arising from both stochastic disturbances and lack of data. Our guarantees are non-asymptotic and distribution-free, not requiring strong assumptions about the unknown real system dynamics. Our calibration procedure enables distinguishing between observation-velocity-action inputs leading to higher and lower next-state-uncertainty, which is helpful for probabilistically-safe planning. We numerically validate our algorithm on a double-integrator system subject to random perturbations and significant model mismatch, using both a simplified sensor and a more realistic simulated camera. Our approach appropriately quantifies uncertainty both when in-distribution and out-of-distribution, being comparatively volume-efficient to baselines requiring environment-specific data. 

<!-- </div> -->

More comming soon! Stay tuned.