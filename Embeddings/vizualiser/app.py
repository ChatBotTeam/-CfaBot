#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Ne pas se soucier de ces imports
from flask import Flask, render_template, request, jsonify
import uuid
from Embeddings.vizualiser import SimiliarityVizualiser
import Results
import os.path


app = Flask(__name__)
app.secret_key = str(uuid.uuid4())


@app.route('/', methods=['GET'])
def render_index():
    files, categories = vizualiser.load()
    selected_problems = vizualiser.select_problems(files[0], categories[0])
    return render_template('index.html', files=files, categories=categories, problems=selected_problems)


@app.route('/refresh-questions', methods=['POST'])
def refresh_questions():
    file1 = request.form['file1']
    category = request.form['category']
    selected_problems = vizualiser.select_problems(file1, category)
    return render_template('questions.html', problems=selected_problems)


@app.route('/refresh-problem', methods=['POST'])
def refresh_problem():
    problem = vizualiser.get_problem_by_id(request.form['problem_id'])
    file1 = request.form['file1']
    file2 = request.form['file2']
    files = list(enumerate([file1, file2]))
    file1_result = problem.get_file_result(file1)
    file2_result = problem.get_file_result(file2)
    return jsonify({
        'html': render_template('problem.html', problem=problem, files=files),
        'model1': file1_result.model_,
        'model2': file2_result.model_
    })


@app.route('/refresh-problem-details', methods=['POST'])
def refresh_problem_details():
    problem = vizualiser.get_problem_by_id(request.form['problem_id'])
    file1 = request.form['file1']
    file2 = request.form['file2']
    file1_result = problem.get_file_result(file1)
    file2_result = problem.get_file_result(file2)
    return render_template('details.html', problem=problem, file1_result=file1_result, file2_result=file2_result)


@app.route('/refresh-problem-choices', methods=['POST'])
def refresh_problem_choices():
    problem = vizualiser.get_problem_by_id(request.form['problem_id'])
    choices = problem.get_choices()
    return render_template('choices.html', choices=choices)


@app.route('/refresh-comparison', methods=['POST'])
def refresh_comparison():
    problem_id = request.form['problem_id']
    model = request.form['model']
    filename = request.form['filename']
    question_index = int(request.form['question_index'])
    choice_index = int(request.form['choice_index'])
    comparison_index = int(request.form['comparison_index'])
    comparison = vizualiser.get_comparison(problem_id, question_index, choice_index, comparison_index, filename)
    nlp_comparison = vizualiser.get_nlp_comparison(comparison, model)
    return jsonify({
        'html': render_template('comparison.html', nlp_comparison=nlp_comparison),
        'q_source': comparison.q_source_,
        'c_source': comparison.c_source_
    })


if __name__ == '__main__':
    vizualiser = SimiliarityVizualiser(os.path.dirname(Results.__file__))
    app.run(debug=True)
