window.addEventListener("DOMContentLoaded", () => {
    const chatInput = document.getElementById("chat-input");
    const sendButton = document.getElementById("send-button");

    function appendMessage(message, sender) {
        const chatContainer = document.getElementById("chat-container");
        if (!chatContainer) {
            console.error("chat-container not found in DOM.");
            return;
        }
        const msg = document.createElement("div");
        msg.className = `message ${sender}`;
        msg.textContent = message;
        chatContainer.appendChild(msg);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    async function getPrediction(symbol) {
        try {
            const response = await fetch(`/api/predict/${symbol}`);
            const data = await response.json();

            if (data.error) {
                return `❌ Error: ${data.error}`;
            }

            const { predicted, actual, signal } = data.last_20_day_prediction;

            return `📊 Prediction for ${symbol}:\nPredicted Close: $${predicted}\nActual: $${actual}\nSignal: ${signal}`;
            } catch (error) {
                return "❌ Could not fetch prediction. Check your backend.";
        }
    }

    async function handleUserInput() {
        const userInput = chatInput.value.trim();
        if (userInput === "") return;

        appendMessage(userInput, "user");
        chatInput.value = "";

        const lowerInput = userInput.toLowerCase();
        const match = lowerInput.match(/predict\s+(AAPL|TSLA|GOOG)/i);

        let botResponse = "";

        if (lowerInput === "predict stock") {
            botResponse = "🧠 Which stock? Please type: predict AAPL, predict TSLA, or predict GOOG.";
        } else if (match) {
            const symbol = match[1].toUpperCase();
            botResponse = await getPrediction(symbol);
        } else {
            botResponse = "🤖 I didn’t understand. Try: predict AAPL, predict TSLA, or predict GOOG.";
        }

        appendMessage(botResponse, "bot");
    }

    chatInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") handleUserInput();
    });

    sendButton.addEventListener("click", function () {
        handleUserInput();
    });
});
