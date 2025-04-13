const sendButton = document.getElementById("send-btn");
const userInput = document.getElementById("user-input");
const chatMessages = document.querySelector(".chat-messages");

function showLoading() {
  const loadingDiv = document.createElement("div");
  loadingDiv.classList.add("message", "bot-message", "loading");
  loadingDiv.textContent = "I'm thinking, please wait a moment...";
  loadingDiv.style.color = "gray";
  chatMessages.appendChild(loadingDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideLoading() {
  const loadingDiv = document.querySelector(".loading");
  if (loadingDiv) {
    chatMessages.removeChild(loadingDiv);
  }
}

function addMessage(content, sender) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message");

    if (sender === "user") {
        messageDiv.classList.add("user-message");
        messageDiv.innerText = content;
    } else if (sender === "bot") {
        messageDiv.classList.add("bot-message");
    
        // Dùng marked để hiển thị Markdown
        const html = marked.parse(content);
        messageDiv.innerHTML = html;
    }

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

}


function sendMessage() {
  const userMessage = userInput.value.trim();

  if (userMessage === "") return;

  addMessage(userMessage, "user");

  showLoading();

  sendButton.disabled = true;
  userInput.disabled = true;

  fetch("http://127.0.0.1:5000/chatbot", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message: userMessage }),
  })
    .then((response) => response.json())
    .then((data) => {
      
      hideLoading();

      addMessage(data.reply, "bot");
    })
    .catch((error) => {
      console.error("Error:", error);

      hideLoading();
      addMessage("Có lỗi xãy ra rồi, vui lòng thử lại 😭", "bot");
    })
    .finally(() => {
      sendButton.disabled = false;
      userInput.disabled = false;
    });

  userInput.value = "";
}

sendButton.addEventListener("click", sendMessage);

userInput.addEventListener("keypress", (event) => {
  if (event.key === "Enter") {
    sendMessage();
  }
});