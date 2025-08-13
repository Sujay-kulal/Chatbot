class ChatBot {
    constructor() {
      this.messages = []
      this.isLoading = false
      this.initializeElements()
      this.setupEventListeners()
      this.addInitialMessage()
    }
  
    initializeElements() {
      this.messagesContainer = document.getElementById("messages")
      this.chatForm = document.getElementById("chat-form")
      this.messageInput = document.getElementById("message-input")
      this.sendButton = document.getElementById("send-button")
    }
  
    setupEventListeners() {
      this.chatForm.addEventListener("submit", (e) => this.handleSubmit(e))
      this.messageInput.addEventListener("input", () => this.adjustTextareaHeight())
      this.messageInput.addEventListener("keydown", (e) => this.handleKeyDown(e))
    }
  
    addInitialMessage() {
      const welcomeMessage = {
        id: "1",
        content: `<strong>Hi! I’m the MITK AI Assistant.</strong><br>
                  Ask me anything about MIT Kundapura: admissions, fees, departments, hostels, placements, library, and more.<br><br>
                  <strong>Quick topics:</strong>
                  <ul>
                      <li>Admissions, fees, scholarships</li>
                      <li>Library hours and borrowing rules</li>
                      <li>Departments and HoDs (e.g., CS HoD)</li>
                      <li>Hostel rules and canteen timings</li>
                      <li>Transport, placements, academic calendar</li>
                  </ul>
                  What would you like to know?`,
        sender: "bot",
        timestamp: this.formatTime(),
      }
  
      this.addMessage(welcomeMessage, true)
    }
  
    formatTime(date = new Date()) {
      const h = date.getHours()
      const m = String(date.getMinutes()).padStart(2, "0")
      const ampm = h >= 12 ? "PM" : "AM"
      const hr12 = h % 12 || 12
      return `${hr12}:${m} ${ampm}`
    }
  
    addMessage(message, showSuggestedTopics = false) {
      this.messages.push(message)
  
      const messageElement = document.createElement("div")
      messageElement.className = `message ${message.sender}`
  
      messageElement.innerHTML = `
              <div class="message-avatar">
                  <img src="${message.sender === "user" ? "user.png" : "bot.png"}" alt="${message.sender}">
              </div>
              <div class="message-content">
                  <div>${message.content}</div>
                  <div class="message-time">${message.timestamp}</div>
                  ${showSuggestedTopics ? this.createSuggestedTopics() : ""}
              </div>
          `
  
      this.messagesContainer.appendChild(messageElement)
      this.scrollToBottom()
    }
  
    createSuggestedTopics() {
      const topics = [
        { label: "Admissions", value: "admissions", emoji: "🎓" },
        { label: "Library", value: "library", emoji: "📚" },
        { label: "CS HoD", value: "hod_cs", emoji: "👨‍🏫" },
        { label: "Hostel", value: "hostel", emoji: "🏠" },
        { label: "Placements", value: "placements", emoji: "💼" },
      ]
  
      const topicsHtml = topics
        .map(
          (topic) =>
            `<button class="topic-button" title="${topic.label}" onclick="chatBot.handleSuggestedTopic('${topic.value}')">
                  ${topic.emoji} ${topic.label}
              </button>`,
        )
        .join("")
  
      return `<div class="suggested-topics">${topicsHtml}</div>`
    }
  
        handleSuggestedTopic(topic) {
      const topicLabels = {
        admissions: "Admissions",
        library: "Library",
        hod_cs: "CS HoD",
        hostel: "Hostel",
        placements: "Placements",
      }

      // Convert topic keys to natural language queries
      const topicQueries = {
        admissions: "admissions",
        library: "library",
        hod_cs: "cs hod",
        hostel: "hostel",
        placements: "placements",
      }

      const userMessage = {
        id: Date.now().toString(),
        content: topicLabels[topic] || topic,
        sender: "user",
        timestamp: this.formatTime(),
      }

      this.addMessage(userMessage)
      this.processMessage(topicQueries[topic] || topic)
    }
  
    adjustTextareaHeight() {
      this.messageInput.style.height = "auto"
      this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 160) + "px"
    }
  
    handleKeyDown(e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault()
        this.handleSubmit(e)
      }
    }
  
    async handleSubmit(e) {
      e.preventDefault()
  
      const messageText = this.messageInput.value.trim()
      if (!messageText || this.isLoading) return
  
      const userMessage = {
        id: Date.now().toString(),
        content: messageText,
        sender: "user",
        timestamp: this.formatTime(),
      }
  
      this.addMessage(userMessage)
      this.messageInput.value = ""
      this.messageInput.style.height = "auto"
  
      await this.processMessage(messageText)
    }
  
    async processMessage(messageText) {
      this.setLoading(true)
  
      try {
        const response = await fetch("/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: messageText,
          }),
        })
  
        const data = await response.json()
  
        let contentHtml = this.formatBotResponse(data.response)
        if (data.matched) {
          contentHtml += this.createSuggestedTopics()
        }

        const botMessage = {
          id: (Date.now() + 1).toString(),
          content: contentHtml,
          sender: "bot",
          timestamp: this.formatTime(),
        }
  
        this.addMessage(botMessage)
      } catch (error) {
        const errorMessage = {
          id: (Date.now() + 1).toString(),
          content: "Sorry, I encountered an error. Please try again.",
          sender: "bot",
          timestamp: this.formatTime(),
        }
        this.addMessage(errorMessage)
      } finally {
        this.setLoading(false)
      }
    }
  
    formatBotResponse(response) {
      // Bold
      const bolded = response.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      const lines = bolded.split("\n")
      const bulletRegex = /^\s*(?:[-*•–]|\d+\.)\s+/

      let html = ""
      let inList = false

      for (const rawLine of lines) {
        const line = rawLine.trimEnd()
        if (bulletRegex.test(line)) {
          if (!inList) {
            html += "<ul>"
            inList = true
          }
          const itemText = line.replace(bulletRegex, "")
          html += `<li>${itemText}</li>`
        } else {
          if (inList) {
            html += "</ul>"
            inList = false
          }
          if (line.trim() === "") {
            html += "<br>"
          } else {
            html += `<div>${line}</div>`
          }
        }
      }
      if (inList) html += "</ul>"
      return html
    }
  
    setLoading(loading) {
      this.isLoading = loading
      this.sendButton.disabled = loading
  
      if (loading) {
        const loadingElement = document.createElement("div")
        loadingElement.className = "message bot"
        loadingElement.id = "loading-message"
        loadingElement.innerHTML = `
                  <div class="message-avatar">
                      <img src="bot.png" alt="bot">
                  </div>
                  <div class="message-content">
                      <div class="loading">
                          <div class="loading-dot"></div>
                          <div class="loading-dot"></div>
                          <div class="loading-dot"></div>
                      </div>
                  </div>
              `
        this.messagesContainer.appendChild(loadingElement)
        this.scrollToBottom()
      } else {
        const loadingElement = document.getElementById("loading-message")
        if (loadingElement) {
          loadingElement.remove()
        }
      }
    }
  
    scrollToBottom() {
      this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight
    }
  }
  
  // Initialize the chatbot when the page loads
  let chatBot
  document.addEventListener("DOMContentLoaded", () => {
    chatBot = new ChatBot()
  })
  
