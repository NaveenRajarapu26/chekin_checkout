from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///checklog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class CheckLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.String(50), nullable=True)  # Only used for check-out

@app.route("/")
def home():
    return render_template("problem.html")

@app.route("/check", methods=["POST"])
def check():
    name = request.form.get("name")
    action = request.form.get("action")
    current_time = datetime.now()

    if action == "checkin":
        # Just log the check-in
        new_log = CheckLog(name=name, action=action, timestamp=current_time)
        db.session.add(new_log)
        db.session.commit()
        return f"{name} has checked in at {current_time.strftime('%Y-%m-%d %H:%M:%S')}"

    elif action == "checkout":
        # Find latest check-in for the same name
        last_checkin = CheckLog.query.filter_by(name=name, action="checkin").order_by(CheckLog.timestamp.desc()).first()
        if last_checkin:
            duration = current_time - last_checkin.timestamp
            readable_duration = str(duration).split('.')[0]  # strip microseconds

            # Log the check-out
            new_log = CheckLog(name=name, action=action, timestamp=current_time, duration=readable_duration)
            db.session.add(new_log)
            db.session.commit()

            return f"{name} has checked out at {current_time.strftime('%Y-%m-%d %H:%M:%S')} (Duration: {readable_duration})"
        else:
            return f"No check-in found for {name}. Please check in first."

@app.route("/history")
def history():
    logs = CheckLog.query.order_by(CheckLog.id.desc()).all()
    return render_template("history.html", logs=logs)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
