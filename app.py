from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import logging

logging.basicConfig(filename='log/app.log', level=logging.INFO)

app = Flask(__name__)
app.secret_key = 'choohanisgod'
@app.route('/ai', methods=["GET", "POST"])
def ai():
    if("currentUnA" not in session):
        session["currentUnA"] = [{}]
    if request.method == "POST":

        qna = {}
        connection = sqlite3.connect("/var/www/FlaskApp/FlaskApp/Database/data.db")
        db = connection.cursor()
        db.execute("SELECT User FROM responses")
        users = db.fetchall()
        db.execute("SELECT AI FROM responses")
        ai = db.fetchall()
        db.execute("SELECT Bad FROM responses")
        bad = db.fetchall()
        connection.commit()
        connection.close()

        for i in range(len(users)):
            qna[users[i][0]] = [ai[i][0], bad[i][0]]


        userText = request.form.get("content")
        punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
        clearUT = ""
        for char in userText:
            if char not in punctuations:
                clearUT = clearUT + char
        words = clearUT.split()
        answer = ""
        percent = 0.0
        br = 0
        total = 0.0
        for word in words:
            total += 1.0
        for question in qna:
            matches = 0.0
            questionWords = question.split()
            for questionWord in questionWords:
                for word in words:
                    if(questionWord.lower() == word.lower()):
                        matches += 1.0
            currentPercent = float(matches) / float(total) * 100.0
            currentbr = int(qna[question][1])
            if (currentPercent > percent and currentbr <= br):
                answer = question
                percent = currentPercent
                br = currentbr
                session["currentMatchText"] = answer
        if (percent != 0.0):
            aianswer = qna[answer][0]
            if(clearUT.lower() != answer.lower()):
                connection = sqlite3.connect("/var/www/FlaskApp/FlaskApp/Database/data.db")
                db = connection.cursor()
                repeat = False
                
                for i in range(len(users)):
                    if(users[i][0].lower() == clearUT.lower()):
                        repeat = True

                if(repeat == False):
                    commands = (clearUT, aianswer)
                    db.execute("INSERT INTO responses (User, AI) VALUES (?, ?)", commands)
                connection.commit()
                connection.close()
        else:
            aianswer = "Sorry, I dont know what do you mean!"
            session["currentMatchText"] = ""
        
        session["currentUnA"].append({ userText : aianswer })
        session["currentUserText"] = clearUT
        session["currentAIText"] = aianswer
        currentUnA = session["currentUnA"]
        return render_template("chat.html", currentUnA=currentUnA, run=True, userText=userText, aianswer=aianswer)
    else:
        currentUnA = session["currentUnA"]
        return render_template("chat.html",currentUnA=currentUnA, run=False)
@app.route('/submit', methods=["GET", "POST"])
def submitai():
    if request.method == "POST":
        if request.form.get("need"):
            qna = {}
            connection = sqlite3.connect("/var/www/FlaskApp/FlaskApp/Database/data.db")
            db = connection.cursor()
            db.execute("SELECT User FROM responses")
            users = db.fetchall()
            db.execute("SELECT AI FROM responses")
            ai = db.fetchall()
            db.execute("SELECT Bad FROM responses")
            bad = db.fetchall()
            connection.commit()
            connection.close()

            for i in range(len(users)):
                qna[users[i][0]] = [ai[i][0], bad[i][0]]


            userText = request.form.get("improvecontent")
            punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
            clearUT = userText
            
            currentMatchText = session["currentMatchText"]
            currentUserText = session["currentUserText"]
            currentAIText = session["currentAIText"]
            
            if currentMatchText == "":
                connection = sqlite3.connect("/var/www/FlaskApp/FlaskApp/Database/data.db")
                db = connection.cursor()
                command = (currentUserText, clearUT)
                db.execute("INSERT INTO responses (User, AI) VALUES (?, ?);", command)
                connection.commit()
                connection.close()
            elif currentUserText.lower() != currentMatchText.lower():
                connection = sqlite3.connect("/var/www/FlaskApp/FlaskApp/Database/data.db")
                db = connection.cursor()
                db.execute("SELECT Bad FROM responses WHERE User = ?", (currentMatchText,))
                utbad = db.fetchall()
                currentutbadreview = utbad[0][0]
                badreview = int(currentutbadreview)
                commands = (badreview + 1, currentMatchText)
                db.execute("UPDATE responses SET Bad = ? WHERE User = ?", commands)
                commands = (userText, currentUserText)
                db.execute("UPDATE responses SET AI = ? WHERE User = ?", commands)
                connection.commit()
                connection.close()
            else:
                connection = sqlite3.connect("/var/www/FlaskApp/FlaskApp/Database/data.db")
                db = connection.cursor()
                commands = (userText, currentUserText)
                db.execute("UPDATE responses SET AI = ? WHERE User = ?", commands)
                commands = (0, currentMatchText)
                db.execute("UPDATE responses SET Bad = ? WHERE User = ?", commands)
                connection.commit()
                connection.close()

    return redirect(url_for('ai'))

if __name__ == "__main__":
    app.run()