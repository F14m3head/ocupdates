function loadStatusData() {
  fetch('status.json')
    .then(res => res.json())
    .then(data => {
      document.getElementById('lastUpdated').textContent = `Last updated: ${data.updated}`;

      const grid = document.getElementById('statusGrid');
      grid.innerHTML = '';

      data.services.forEach(service => {
        const card = document.createElement('div');
        card.className = `status-card ${service.status}`;
        card.innerHTML = `
          <i class="fas fa-${service.icon}"></i>
          <h3>${service.type}</h3>
          <p>${service.message}</p>
        `;
        grid.appendChild(card);
      });

      const noticeList = document.getElementById('noticeList');
      noticeList.innerHTML = '';
      data.notices.forEach(note => {
        const li = document.createElement('li');
        li.textContent = note;
        noticeList.appendChild(li);
      });
    })
    .catch(err => {
      console.error('Failed to load status data:', err);
      document.getElementById('lastUpdated').textContent = 'Failed to load status data.';
    });
}

loadStatusData();

setInterval(loadStatusData, 30000); // every 30 seconds