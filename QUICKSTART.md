# 🚀 Quick Start Guide

Get your portfolio chatbot running in 5 minutes!

## Step 1: Install Dependencies ⚡

```bash
pip install -r requirements.txt
```

## Step 2: Add Your Content 📝

Add documents about yourself to the `about_me` folder:

```
about_me/
├── bio.txt           # Your bio and background
├── experience.md     # Work experience
├── skills.txt        # Technical skills
├── cv.pdf           # Your resume/CV
└── projects.md      # Your projects
```

**Example content:**
```markdown
# About Me
I'm a software engineer with 5 years of experience...

## Skills
- Python
- JavaScript
- Machine Learning

## Experience
Senior Developer at TechCorp (2020-2024)
- Built scalable web applications
- Led team of 5 developers
```

## Step 3: Test the Chatbot 🤖

### Option A: Command Line (Quick Test)

```bash
python portfolio_bot.py
```

Then type questions like:
- "Hello"
- "What is your experience?"
- "What skills do you have?"

### Option B: Web Interface (Full Experience)

1. Start the server:
```bash
python api_server.py
```

2. Open `index.html` in your browser

3. Click the chat button and start talking! 💬

## Common First Questions ❓

Try these to test your bot:
- "Hello, who are you?"
- "Tell me about your experience"
- "What technologies do you know?"
- "What projects have you worked on?"
- "Are you available for work?"

## Troubleshooting 🔧

**Problem: "No documents found"**
- Solution: Add .txt, .md, .pdf, or .docx files to `about_me/` folder

**Problem: "API key error"**
- Solution: Update the `api_key` variable in `portfolio_bot.py`

**Problem: Web interface can't connect**
- Solution: Make sure `python api_server.py` is running

## Next Steps 🎯

1. ✅ Customize the system prompt in `portfolio_bot.py`
2. ✅ Update the HTML colors/design in `index.html`
3. ✅ Add more documents to improve responses
4. ✅ Deploy to the cloud (optional)

## Need Help? 💡

Check the full `README.md` for detailed documentation!

---

**Happy chatting!** 🎉
