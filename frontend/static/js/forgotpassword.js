document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");
    const usernameInput = document.getElementById("username");
    const emailInput = document.getElementById("email");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const username = usernameInput.value.trim();
        const email = emailInput.value.trim();

        if (!username || !email) {
            showAlert("Please enter both your username and email.");
            return;
        }

        try {
            const url = `${window.location.origin}/api/issue_reset_password`;

            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ username, email }),
            });

            if (!response.ok) {
                const errorResult = await response.json();
                if (response.status === 404 && errorResult.error === "No user found") {
                    showAlert("No user found with the provided username.");
                } else if (response.status === 400 && errorResult.error === "Missing Arguments") {
                    showAlert("Missing required information. Please try again.");
                } else {
                    showAlert("An unexpected error occurred. Please try again.");
                }
                return;
            }

            const result = await response.json();
            if (response.status === 200 && result.conf) {
                showAlert(result.conf);
            }
        } catch (error) {
            console.error("Error issuing password reset:", error);
            showAlert("An error occurred while connecting to the server. Please try again later.");
        }
    });
});

function showAlert(message) {
    const alertBlock = document.getElementById("alert");

    alertBlock.textContent = message;
    alertBlock.style.display = "block";

    setTimeout(() => {
        alertBlock.style.display = "none";
    }, 10000);
}
