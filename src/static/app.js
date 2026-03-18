document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Check if all required elements exist
  if (!activitiesList || !activitySelect || !signupForm || !messageDiv) {
    console.error("Required DOM elements not found");
    return;
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list and dropdown
      displayActivities(activities);
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  function displayActivities(activities) {
    if (activities.length === 0) {
      activitiesList.innerHTML = '<p>No activities available at this time.</p>';
      return;
    }

    activitiesList.innerHTML = '';
    activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

    activities.forEach(activity => {
      // Create activity card
      const card = document.createElement('div');
      card.className = 'activity-card';
      
      const participantsList = activity.participants && activity.participants.length > 0
        ? `<ul class="participants-list">
            ${activity.participants.map(p => `<li>${p} <button class="delete-participant" data-activity-id="${activity.id}" data-participant="${encodeURIComponent(p)}" title="Remove participant">✕</button></li>`).join('')}
           </ul>`
        : `<p class="no-participants">No participants yet. Be the first to sign up!</p>`;

      card.innerHTML = `
        <h4>${activity.name}</h4>
        <p><strong>Description:</strong> ${activity.description}</p>
        <p><strong>Schedule:</strong> ${activity.schedule}</p>
        <div class="participants-section">
          <h5>📋 Participants:</h5>
          ${participantsList}
        </div>
      `;

      activitiesList.appendChild(card);

      // Add event listeners for delete buttons
      const deleteButtons = card.querySelectorAll('.delete-participant');
      deleteButtons.forEach(button => {
        button.addEventListener('click', async (event) => {
          event.preventDefault();
          const activityId = button.getAttribute('data-activity-id');
          const participant = decodeURIComponent(button.getAttribute('data-participant'));

          if (!confirm(`Are you sure you want to remove ${participant} from this activity?`)) {
            return;
          }

          try {
            const response = await fetch(
              `/activities/${encodeURIComponent(activityId)}/unregister?email=${encodeURIComponent(participant)}`,
              {
                method: "DELETE",
              }
            );

            const result = await response.json();

            if (response.ok) {
              messageDiv.textContent = result.message || `Removed ${participant} from activity`;
              messageDiv.className = "success";
              await fetchActivities(); // Refresh the activities list
            } else {
              messageDiv.textContent = result.detail || "Failed to remove participant";
              messageDiv.className = "error";
            }

            messageDiv.classList.remove("hidden");

            // Hide message after 5 seconds
            setTimeout(() => {
              messageDiv.classList.add("hidden");
            }, 5000);
          } catch (error) {
            messageDiv.textContent = "Failed to remove participant. Please try again.";
            messageDiv.className = "error";
            messageDiv.classList.remove("hidden");
            console.error("Error removing participant:", error);
          }
        });
      });

      // Add to select dropdown
      const option = document.createElement('option');
      option.value = activity.id;
      option.textContent = activity.name;
      activitySelect.appendChild(option);
    });
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    if (!email || !activity) {
      messageDiv.textContent = "Please fill in all fields";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      // Always refresh the activities list to show updated participants
      await fetchActivities();
      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
