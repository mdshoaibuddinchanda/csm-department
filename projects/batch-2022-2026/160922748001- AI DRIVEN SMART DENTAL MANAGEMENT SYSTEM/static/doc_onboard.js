document.getElementById("onboard-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const days = Array.from(document.querySelectorAll(".days input:checked"))
    .map(cb => parseInt(cb.value));

  const payload = {
    name: document.getElementById("name").value,
    email: document.getElementById("email").value,
    clinic_email: document.getElementById("clinic_email").value,
    doctor_whatsapp_number: document.getElementById("doctor_whatsapp_number").value,
    clinic_phone_number: document.getElementById("clinic_phone_number").value,
    working_days: days,
    work_start_time: document.getElementById("start_time").value,
    work_end_time: document.getElementById("end_time").value,
    avg_consult_minutes: parseInt(document.getElementById("avg_minutes").value),
    buffer_minutes: parseInt(document.getElementById("buffer_minutes").value),
  };

  const messageDiv = document.getElementById("message");
  messageDiv.innerHTML = "";

  try {
    const res = await fetch("/doctors/onboard", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    console.log("ONBOARD RESPONSE:", data);


    if (!res.ok) {
      messageDiv.innerHTML = `<div class="error">${data.detail}</div>`;
      return;
    }

   messageDiv.innerHTML = `
  <div class="success">
    ✅ Doctor onboarded successfully.<br/>
    Booking URL: <b>https://appointment-booking-agent-b06e.onrender.com/book/${data.slug}</b><br/><br/>
    <button id="connect-calendar-btn">
      🔗 Connect Google Calendar
    </button>
  </div>
`;

const btn = document.getElementById("connect-calendar-btn");
btn.onclick = () => {
  window.location.href = data.connect_calendar_url;
};

  } catch (err) {
    messageDiv.innerHTML = `<div class="error">Server error</div>`;
  }
});
