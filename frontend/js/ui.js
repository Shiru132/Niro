function renderStatus(data) {
  const output = document.getElementById("output");

  if (!data) {
    output.innerHTML = "Brak danych";
    return;
  }

  let html = "<h3>Status farmy</h3>";

  for (const pos in data) {
    const field = data[pos];
    html += `<div>Pozycja ${pos}: ${JSON.stringify(field)}</div>`;
  }
  document.getElementById("gardenBtn").addEventListener("click", async () => {
  const pid = document.getElementById("pidSelect").value;

  await runGarden(pid);

  alert("Wysłano akcję sadzenia");
});

  output.innerHTML = html;
}