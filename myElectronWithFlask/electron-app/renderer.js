document.getElementById('fetch').addEventListener('click', async () => {
    const data = await window.api.fetchData();
    document.getElementById('output').textContent = JSON.stringify(data, null, 2);
  });