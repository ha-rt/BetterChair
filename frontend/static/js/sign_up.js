document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");
    const usernameInput = document.getElementById("username");
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");
    const confirmPasswordInput = document.getElementById("confirmpassword");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const username = usernameInput.value.trim();
        const email = emailInput.value.trim();
        const password = passwordInput.value.trim();
        const confirmPassword = confirmPasswordInput.value.trim();

        if (!username || !email || !password || !confirmPassword) {
            showAlert("Please fill in all fields.");
            return;
        }

        if (!validateEmail(email)) {
            showAlert("Please enter a valid email address.");
            return;
        }

        if (password !== confirmPassword) {
            showAlert("Passwords do not match. Please try again.");
            return;
        }

        try {
            const url = `${window.location.origin}/api/sign_up`;

            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ username, email, password }),
            });

            const result = await response.json();

            if (!response.ok) {
                if (response.status === 400) {
                    if (result.error === "Invalid Email") {
                        showAlert("The email address you entered is invalid.");
                    } else if (result.error === "Bad Username") {
                        showAlert("The username contains invalid characters or is not allowed.");
                    } else {
                        showAlert(result.error || "Bad Request: Missing or invalid arguments.");
                    }
                } else if (response.status === 409) {
                    showAlert("The username is already in use. Please choose a different one.");
                } else if (response.status === 500) {
                    showAlert("Server Error: Unable to process your request. Please try again later.");
                } else {
                    showAlert(result.error || "An unexpected error occurred. Please try again.");
                }
                return;
            }

            if (response.status === 200 && result.token) {
                showAlert("Sign-up successful! Redirecting to login page...");
                setTimeout(() => {
                    window.location.href = "/login";
                }, 3000);
            }
        } catch (error) {
            console.error("Error signing up:", error);
            showAlert("An error occurred while connecting to the server. Please try again later.");
        }
    });
});

function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}


function showAlert(message) {
    const alertBlock = document.getElementById("alert");

    alertBlock.textContent = message;
    alertBlock.style.display = "block";

    setTimeout(() => {
        alertBlock.style.display = "none";
    }, 10000);
}
