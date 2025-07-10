document.addEventListener("DOMContentLoaded", () => {
  const body = document.body;
  const toggleBtn = document.getElementById("toggleDarkMode");
  const icon = toggleBtn.querySelector("i");

  // Load saved theme or default to dark
  const savedTheme = localStorage.getItem("theme") || "dark";
  body.setAttribute("data-theme", savedTheme);

  // Set correct icon on load
  if (savedTheme === "dark") {
    icon.classList.remove("fa-moon");
    icon.classList.add("fa-sun");
  } else {
    icon.classList.remove("fa-sun");
    icon.classList.add("fa-moon");
  }

  // Toggle theme and icon
  toggleBtn.addEventListener("click", () => {
    const currentTheme = body.getAttribute("data-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    body.setAttribute("data-theme", newTheme);
    localStorage.setItem("theme", newTheme);

    if (newTheme === "dark") {
      icon.classList.remove("fa-moon");
      icon.classList.add("fa-sun");
    } else {
      icon.classList.remove("fa-sun");
      icon.classList.add("fa-moon");
    }
  });
});

/* status */
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

