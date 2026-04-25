from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
from openai import OpenAI
import os

app = Flask(__name__)
app.secret_key = 'replace-this-with-a-strong-secret'

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a soft skills training assistant.

Your job is to simulate realistic workplace conversations to evaluate and improve soft skills like communication, leadership, teamwork, adaptability, and problem-solving.

Start by presenting a realistic workplace scenario only after the user types "start".

After the user responds:
- evaluate their soft skills
- give constructive and supportive feedback
- keep feedback natural and human (do not say "Feedback:")
- keep feedback around 4–5 sentences
- then generate the next realistic scenario

Only give one challenge at a time.
Keep the tone professional, supportive, and focused on learning.
"""

WELCOME_MESSAGE = """
Welcome to Sim Carma!

I’ll help you improve your soft skills through realistic workplace scenarios involving leadership, teamwork, communication, deadlines, and problem-solving.

Type "start" when you're ready for your first scenario.
"""


@app.route('/')
def home():
    return redirect(url_for('index'))


@app.route('/index')
def index():
    # Start fresh session
    session['conversation'] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": WELCOME_MESSAGE}
    ]

    return render_template(
        'chat.html',
        initial_question=WELCOME_MESSAGE,
        now=datetime.now()
    )


@app.route('/get', methods=['POST'])
def chat():
    if 'conversation' not in session:
        session['conversation'] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": WELCOME_MESSAGE}
        ]

    user_msg = request.form['msg']
    session['conversation'].append({
        "role": "user",
        "content": user_msg
    })

    try:
        completion = client.chat.completions.create(
            model="gpt-4.1",
            messages=session['conversation']
        )

        reply = completion.choices[0].message.content

        session['conversation'].append({
            "role": "assistant",
            "content": reply
        })

        session.modified = True

        return reply

    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/restart')
def restart():
    session.pop('conversation', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
