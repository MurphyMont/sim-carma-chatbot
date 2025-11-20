from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
from openai import OpenAI
import os

app = Flask(__name__)
app.secret_key = 'replace-this-with-a-strong-secret'

# Create OpenAI client (reads OPENAI_API_KEY from environment)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a soft skills training assistant. Your job is to simulate realistic workplace conversations to evaluate and improve soft skills like communication, leadership, teamwork, adaptability, and problem-solving.

Start by presenting a realistic scenario. After the user responds, evaluate their soft skills, give constructive feedback, and generate the next scenario. Keep the tone supportive and focused on learning, also give about 5 senteces for the feedback not too detailed , and dont say something like Feedback is , that sounds too robotic. One challenge at a time.
"""

@app.route('/')
def home():
    return redirect(url_for('index'))


@app.route('/index')
def index():
    # Start new session-based conversation
    session['conversation'] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "assistant",
            "content": (
                "Welcome to Sim Carma! Let's start your soft skills training.\n\n"
                "Scenario 1:\nYou're leading a team and one member is consistently "
                "missing deadlines. How would you handle it?"
            )
        }
    ]
    return render_template(
        'chat.html',
        initial_question=session['conversation'][-1]['content'],
        now=datetime.now()
    )

@app.route('/get', methods=['POST'])
def chat():
    # Make sure conversation exists
    if 'conversation' not in session:
        session['conversation'] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    user_msg = request.form['msg']
    session['conversation'].append({"role": "user", "content": user_msg})

    # ✅ New style call with the v1 client
    completion = client.chat.completions.create(
        model="gpt-4.1",
        messages=session['conversation']
    )

    reply = completion.choices[0].message.content
    session['conversation'].append({"role": "assistant", "content": reply})

    return reply

@app.route('/restart')
def restart():
    # Reset conversation
    session['conversation'] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "assistant",
            "content": (
                "Welcome back to Sim Carma! Let's begin again.\n\n"
                "Scenario 1:\nYou're leading a team and one member is consistently "
                "missing deadlines. How would you handle it?"
            )
        }
    ]
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
