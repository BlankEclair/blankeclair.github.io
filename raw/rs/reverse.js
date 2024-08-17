"use strict";

const ALL_SOURCES = JSON.parse(document.querySelector('script[type="application/json"]').innerText);

let input = document.querySelector("#url");
let table = document.querySelector("table");

function updateSources() {
    let url = encodeURIComponent(input.value);
    table.querySelectorAll(".source-line").forEach((i) => i.remove());

    for (let [type, sources] of Object.entries(ALL_SOURCES)) {
        let tr = document.createElement("tr");
        tr.classList.add("source-line");

        let td = document.createElement("td");
        td.innerText = type;
        tr.append(td);

        td = document.createElement("td");
        let i = 0;
        for (let [sourceName, sourceInfo] of Object.entries(sources)) {
            td.append(i ? ", " : " ");
            let a = document.createElement("a");
            a.href = url ? sourceInfo.url.replace("%s", url) : sourceInfo.home;
            a.innerText = sourceName
            td.append(a);

            i++;
        }
        tr.append(td);

        table.append(tr);
    }
}
input.addEventListener("input", updateSources, {passive: true});
updateSources();

document.body.classList.remove("no-script");
