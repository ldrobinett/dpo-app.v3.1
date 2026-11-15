const scenarioPairs = [...document.querySelectorAll("[data-scenario-pair]")]
    .map(pair => [...pair.querySelectorAll("input")]);

function highlightTargetChanges() {
    for (const [current, target] of scenarioPairs) {
        const changed = current.value !== "" && target.value !== "" && Number(current.value) !== Number(target.value);
        target.classList.toggle("scenario-changed", changed);
    }
}

document.querySelector("[data-scenario-form]").addEventListener("input", highlightTargetChanges);
document.querySelector("[data-copy-current]").addEventListener("click", () => {
    for (const [current, target] of scenarioPairs) target.value = current.value;
    highlightTargetChanges();
});
highlightTargetChanges();
