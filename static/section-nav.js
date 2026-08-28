(() => {
    const drawPrompts = Array.from(document.querySelectorAll("[data-cspace-draw-prompt]"));
    if (drawPrompts.length) {
        drawPrompts.forEach((prompt) => prompt.classList.add("is-awaiting-draw"));
        const explorerFrame = document.querySelector(".cspace-explorer-frame iframe");
        const visibilityTarget = explorerFrame?.closest(".cspace-explorer-frame") ?? drawPrompts[0];
        let explorerReady = false;
        let explorerIsVisible = false;
        let promptsStarted = false;
        const maybeDrawArrow = () => {
            if (!explorerReady || !explorerIsVisible || promptsStarted) return;
            promptsStarted = true;
            const clickPrompt = drawPrompts.find((prompt) =>
                prompt.classList.contains("cspace-explorer-click-prompt"),
            );
            drawPrompts
                .filter((prompt) => prompt !== clickPrompt)
                .forEach((prompt) => prompt.classList.add("is-drawn"));
            window.setTimeout(() => clickPrompt?.classList.add("is-drawn"), 1050);
        };
        window.addEventListener("message", (event) => {
            if (event.source !== explorerFrame?.contentWindow) return;
            if (event.data?.type !== "capture-cspace-explorer-ready") return;
            explorerReady = true;
            maybeDrawArrow();
        });
        const targetRect = visibilityTarget.getBoundingClientRect();
        const visibleHeight = Math.max(
            0,
            Math.min(targetRect.bottom, window.innerHeight) - Math.max(targetRect.top, 0),
        );
        const requiredVisibility = Math.min(
            0.95,
            Math.max(0.6, (window.innerHeight - 32) / targetRect.height),
        );
        explorerIsVisible = visibleHeight / targetRect.height >= requiredVisibility;
        if (explorerIsVisible || !("IntersectionObserver" in window)) {
            maybeDrawArrow();
        } else {
            const drawObserver = new IntersectionObserver(
                ([entry]) => {
                    if (entry.intersectionRatio < requiredVisibility) return;
                    explorerIsVisible = true;
                    maybeDrawArrow();
                    drawObserver.disconnect();
                },
                {threshold: requiredVisibility},
            );
            drawObserver.observe(visibilityTarget);
        }
    }

    const nav = document.querySelector("[data-capture-section-nav]");
    if (!nav) return;

    const entries = Array.from(nav.querySelectorAll("[data-capture-section-link]"))
        .map((link) => {
            const section = document.getElementById(link.dataset.sectionId);
            return section ? {link, section} : null;
        })
        .filter(Boolean);
    if (!entries.length) return;

    const hero = document.querySelector(".capture-hero");
    let scheduled = false;

    for (const entry of entries) {
        const scrollTargetId = entry.link.dataset.scrollTargetId;
        if (!scrollTargetId) continue;

        const scrollTarget = document.getElementById(scrollTargetId);
        if (!scrollTarget) continue;

        entry.link.addEventListener("click", (event) => {
            event.preventDefault();
            window.history.pushState(null, "", entry.link.hash);
            scrollTarget.scrollIntoView({behavior: "smooth", block: "start"});
        });
    }

    const update = () => {
        scheduled = false;
        const readingLine = window.scrollY + Math.min(160, window.innerHeight * 0.22);
        const revealLine = hero ? hero.offsetTop + hero.offsetHeight : entries[0].section.offsetTop;
        nav.classList.toggle("is-visible", window.scrollY >= revealLine);

        let active = entries[0];
        for (const entry of entries) {
            if (entry.section.offsetTop <= readingLine) active = entry;
        }
        const pageBottom = window.scrollY + window.innerHeight;
        if (pageBottom >= document.documentElement.scrollHeight - 2) {
            active = entries[entries.length - 1];
        }
        for (const entry of entries) {
            if (entry === active) {
                entry.link.setAttribute("aria-current", "location");
            } else {
                entry.link.removeAttribute("aria-current");
            }
        }
    };

    const scheduleUpdate = () => {
        if (scheduled) return;
        scheduled = true;
        window.requestAnimationFrame(update);
    };

    nav.classList.add("is-enhanced");
    window.addEventListener("scroll", scheduleUpdate, {passive: true});
    window.addEventListener("resize", scheduleUpdate);
    window.addEventListener("load", scheduleUpdate, {once: true});
    update();
})();
