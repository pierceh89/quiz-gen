from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import os

client = MongoClient('127.0.0.1', 27017)
db = client.dbquiz

app = Flask(__name__)
SUB_AUTH = os.environ.get('AUTH')


@app.route('/gen', methods=['GET'])
def generator():
    return render_template('quiz_generator.html')


@app.route('/gen', methods=['POST'])
def generate_quiz():
    given_auth = request.form['auth']
    if given_auth == '' or given_auth != SUB_AUTH:
        return jsonify({
            'result': 'fail',
            'msg': '올바른 비밀번호를 입력해주세요'
        })
    title = request.form['title']
    script = request.form['quizScript']
    answers = request.form.getlist('answers[]')
    db.quizset.insert({
        'title': title,
        'script': script,
        'answers': answers
    })
    return jsonify({'result': 'success'})


@app.route('/submit', methods=['POST'])
def scoring_submission():
    submitter = request.form['name']
    title = request.form['title']
    submits = request.form.getlist('answers[]')
    answers = db.quizset.find_one({'title': title})['answers']
    zipped = list(zip(submits, answers))
    scores = []
    for pair in zipped:
        scores.append(pair[0].strip() == pair[1].strip())
    count_true = 0
    for score in scores:
        if score:
            count_true += 1

    result = {
        'submitter': submitter,
        'title': title,
        'pairs': zipped,
        'score': count_true,
        'fullScore': len(answers)
    }
    db.submission.insert_one(result)
    del result['_id']
    del result['pairs']
    return jsonify({
        'result': 'success',
        'detail': result
    })


@app.route('/quiz-list')
def get_quiz_list():
    quiz_list = list(db.quizset.find({}, {'_id': False, 'answers': False}))
    return jsonify({
        'result': 'success',
        'quiz': quiz_list
    })


@app.route('/sub')
def submissions():
    return render_template('submissions.html')


@app.route('/sub-list', methods=['POST'])
def get_submissions():
    given_auth = request.form.get('auth')
    if given_auth == '' or given_auth != SUB_AUTH:
        return jsonify({
            'result': 'fail',
            'msg': '올바른 비밀번호를 입력해주세요'
        })

    subs = list(db.submission.find({}, {'_id': False}))
    ret = {}
    for sub in subs:
        title = sub['title']
        if title in ret:
            ret[title].append(sub)
        else:
            ret[title] = [sub]
    return jsonify({
        'result': 'success',
        'submission': ret
    })


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    if SUB_AUTH is None:
        raise RuntimeError('AUTH env must be provided')
    app.run('0.0.0.0', port=5000, debug=True)
