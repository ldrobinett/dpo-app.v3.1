const storeMenuButton = document.querySelector(".workspace-toggle");
const storeNavigation = document.getElementById("store-navigation");

function setStoreMenu(open) {
    storeNavigation.classList.toggle("is-open", open);
    storeMenuButton.setAttribute("aria-expanded", String(open));
}

storeMenuButton.addEventListener("click", () => {
    setStoreMenu(storeMenuButton.getAttribute("aria-expanded") !== "true");
});

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && storeMenuButton.getAttribute("aria-expanded") === "true") {
        setStoreMenu(false);
        storeMenuButton.focus();
    }
});
