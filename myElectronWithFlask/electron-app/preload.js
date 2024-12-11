const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  fetchData: async () => {
    const response = await fetch('http://127.0.0.1:5000/data');
    return response.json();
  },
});