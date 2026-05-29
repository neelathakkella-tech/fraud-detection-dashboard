from flask import Flask, request, redirect, send_file, session
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import os
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = "fraud_secret_key"

USERNAME = "neela"
PASSWORD = "fraudai2026"

latest_report = {}

@app.route('/', methods=['GET', 'POST'])
def login():

    error = ""

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == USERNAME and password == PASSWORD:
            return redirect('/dashboard')
        else:
            error = "<p style='color:red;'>Invalid Username or Password</p>"

    return f'''
    <html>
    <body style="background:linear-gradient(to right,#141e30,#243b55);font-family:Arial;">
        <div style="width:350px;margin:auto;margin-top:120px;background:white;padding:30px;border-radius:20px;text-align:center;">
            <h1>🔐 Secure Login</h1>

            <form method="POST">
                <input type="text" name="username" placeholder="Username" required style="width:90%;padding:12px;margin-top:20px;"><br><br>
                <input type="password" name="password" placeholder="Password" required style="width:90%;padding:12px;"><br><br>

                <button type="submit" style="width:95%;background:#243b55;color:white;padding:12px;border:none;">
                    Login
                </button>
            </form>

            <br>
            {error}
        </div>
    </body>
    </html>
    '''

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():

    global latest_report

    # ✅ SESSION HISTORY (FIXED)
    if 'history' not in session:
        session['history'] = []

    history = session['history']

    result = ""
    risk_score = 0
    score_color = "#28a745"

    fraud_count = 0
    safe_count = 0

    if request.method == 'POST':

        amount = float(request.form['amount'])
        country = request.form['country']
        time = request.form['time']

        if amount > 50000:
            risk_score += 40

        if country == "yes":
            risk_score += 30

        if time == "yes":
            risk_score += 30

        if risk_score >= 70:
            score_color = "#ff4d4d"
            result_type = "Fraud"
            fraud_count = 1

            result = """
            <div style="background:#ff4d4d;padding:15px;border-radius:10px;color:white;font-size:24px;text-align:center;">
                🔴 FRAUD DETECTED
            </div>
            """
        else:
            result_type = "Safe"
            safe_count = 1

            result = """
            <div style="background:#28a745;padding:15px;border-radius:10px;color:white;font-size:24px;text-align:center;">
                🟢 NORMAL TRANSACTION
            </div>
            """

        latest_report = {
            "amount": amount,
            "country": country,
            "time": time,
            "risk_score": risk_score,
            "result": result_type
        }

        # ✅ ADD TO SESSION HISTORY
        history.append({
            "amount": amount,
            "country": country,
            "time": time,
            "result": result_type
        })

        session['history'] = history

        # chart
        labels = ['Safe', 'Fraud']
        sizes = [safe_count, fraud_count]

        plt.figure(figsize=(4,4))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%')
        plt.title("Transaction Analytics")

        if not os.path.exists("static"):
            os.makedirs("static")

        plt.savefig("static/chart.png")
        plt.close()

    table_rows = ""

    for item in history:
        table_rows += f"""
        <tr>
            <td>{item['amount']}</td>
            <td>{item['country']}</td>
            <td>{item['time']}</td>
            <td>{item['result']}</td>
        </tr>
        """

    return f'''
    <html>
    <body style="background:linear-gradient(to right,#141e30,#243b55);font-family:Arial;">
        <div style="width:700px;margin:auto;margin-top:20px;background:white;padding:30px;border-radius:20px;">

            <h1 style="text-align:center;">💳 AI Fraud Detection Dashboard</h1>

            <a href="/" style="float:right;background:red;color:white;padding:10px;text-decoration:none;border-radius:8px;">
                Logout
            </a>

            <form method="POST">
                <input type="text" name="amount" placeholder="Transaction Amount" required style="width:95%;padding:12px;margin-top:25px;"><br><br>

                <select name="country" style="width:100%;padding:12px;">
                    <option value="no">Foreign Country? No</option>
                    <option value="yes">Foreign Country? Yes</option>
                </select><br><br>

                <select name="time" style="width:100%;padding:12px;">
                    <option value="no">Unusual Time? No</option>
                    <option value="yes">Unusual Time? Yes</option>
                </select><br><br>

                <button type="submit" style="width:100%;background:#243b55;color:white;padding:14px;font-size:18px;">
                    Check Fraud
                </button>
            </form>

            <br>

            <h3>Risk Score: {risk_score}%</h3>

            <div style="width:100%;background:#ddd;border-radius:10px;">
                <div style="width:{risk_score}%;background:{score_color};padding:10px;border-radius:10px;color:white;text-align:center;">
                    {risk_score}%
                </div>
            </div>

            <br>
            {result}

            <br>

            <h2>📊 Analytics</h2>
            <img src="/static/chart.png" width="300">

            <h2>📜 History</h2>

            <table border="1" width="100%" cellpadding="10" style="border-collapse:collapse;text-align:center;">
                <tr style="background:#243b55;color:white;">
                    <th>Amount</th>
                    <th>Country</th>
                    <th>Time</th>
                    <th>Result</th>
                </tr>
                {table_rows}
            </table>

        </div>
    </body>
    </html>
    '''

@app.route('/download')
def download_pdf():

    pdf_file = "fraud_report.pdf"

    c = canvas.Canvas(pdf_file)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(180, 800, "Fraud Detection Report")

    c.setFont("Helvetica", 14)

    c.drawString(100, 740, f"Amount: {latest_report.get('amount')}")
    c.drawString(100, 700, f"Country: {latest_report.get('country')}")
    c.drawString(100, 660, f"Time: {latest_report.get('time')}")
    c.drawString(100, 620, f"Risk: {latest_report.get('risk_score')}%")
    c.drawString(100, 580, f"Result: {latest_report.get('result')}")

    c.save()

    return send_file(pdf_file, as_attachment=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)