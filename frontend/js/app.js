document.getElementById("runBtn").addEventListener("click", async () => {
  await runFarm();
  alert("Cykl wykonany");
});

document.getElementById("statusBtn").addEventListener("click", async () => {
  const res = await getStatus();
  renderStatus(res.data);
});