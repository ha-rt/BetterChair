document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();

        if (!username || !password) {
            showAlert("Please enter both a username and a password.");
            return;
        }

        try {
            const url = `${window.location.origin}/api/log_in`;

            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ username, password }),
            });

            if (!response.ok) {
                const errorResult = await response.json();
                if (response.status === 403 && errorResult.error === "Incorrect Password") {
                    showAlert("Incorrect password. Please try again.");
                } else if (response.status === 404 && errorResult.error === "No user found") {
                    showAlert("No user found. Please check your username.");
                } else {
                    showAlert("An unexpected error occurred. Please try again.");
                }
                return;
            }

            const result = await response.json();
            if (response.status === 200 && result.token) {
                document.cookie = `authorization=${result.token}; path=/;`;
                showAlert("Login successful! Redirecting...");
                window.location.href = "/";
            }
        } catch (error) {
            console.error("Error logging in:", error);
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
