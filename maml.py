import time
import threading

import flask
import requests
from bs4 import BeautifulSoup

class Student:
    def __init__(self, name, cls, school, m1, m2, m3, m4, m5):
        self.name = name
        self.cls = cls
        self.school = school
        self.scores = [m1, m2, m3, m4, m5]
        self.arml = " "
        for i, score in enumerate(self.scores):
            if score == '':
                score = 0
            else:
                score = int(score)
            self.scores[i] = score

    @property
    def total(self):
        return sum(self.scores)

class Global:
    students = []

def get_ranks() :
    soup = BeautifulSoup(requests.get("http://www.maml.net/indv.htm").text, features="html5lib")

    table = soup.find("tbody")

    data = []

    rows = table.find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        cols = [ele.text.strip() for ele in cols]
        data.append(cols)
        
    data = data[1:] # remove header

    Global.students = []

    
    for line in data:
        Global.students.append(Student(*line[1:9]))

    team = Global.students[:30]
    team += [student for student in Global.students[30:]
             if int(student.cls) < 12][:8]
    for student in Global.students:
        if student in team[:15]:
            student.arml = "M"
        elif student in team[:30]:
            student.arml = "E"
        elif student in team:
            student.arml = "A"

    mssm = [student for student in Global.students if student.school == "MSSM"]
    
    for student in Global.students:
        try:
            student.mssm = mssm.index(student)+1
        except ValueError:
            student.mssm = ""
    

    time.sleep(60*60)
    
updater = threading.Thread(target=get_ranks)

app = flask.Flask(__name__)

@app.route("/maml")
def scores():
    response = """
<!DOCTYPE html>
<html>
<head>
<style>
body {
    font-family: monospace;
}
.arml-M {
    background-color: chartreuse;
}
.arml-E {
    background-color: cyan;
}
.arml-A {
    background-color: lightcoral;
</style>
</head>
<body>
<table>
<tr>
<th>Rank</th>
<th>ARML</th>
<th>Name</th>
<th>Class</th>
<th>Total</th>
<th>M1</th>
<th>M2</th>
<th>M3</th>
<th>M4</th>
<th>M5</th>
<th>MSSM</th>
</tr>
"""
    for i, student in enumerate(Global.students):
        response += ("<tr class='arml-{}'>" + "<td>{}</td>" * 4
                      + "<td><b>{}</b></td>" + "<td>{}</td>" * 6 + "</tr>"
                     ).format(
            (student.arml if student.arml != " " else "none"),
            i+1, student.arml, student.name, student.cls, student.total,
            *student.scores, student.mssm)
    response += """
</table>
</body>
</html>
"""
    return response

updater.start()

app.run("0.0.0.0", port=8080)

