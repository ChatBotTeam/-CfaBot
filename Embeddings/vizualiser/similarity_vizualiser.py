import json
import spacy
import os
import os.path
import Embeddings.models
from Embeddings.vizualiser.dto import Problem
from Embeddings.vizualiser.dto import ComparedToken
from Embeddings.vizualiser.dto import NlpComparison


class SimiliarityVizualiser:
    def __init__(self, results_directory):
        self.nlp_models_ = {}
        self.results_directory_ = results_directory

    def load_category(self, fullname, model, category, result):
        for question_id, problem in result[category].items():
            if not question_id in self.all_problems_:
                self.all_problems_[question_id] = Problem(question_id, fullname, model, category, problem)
            else:
                self.all_problems_[question_id].add_file(fullname, model, problem)

    def load_all_problems(self):
        categories = set()
        for filename in os.listdir(self.results_directory_):
            full_path = os.path.join(self.results_directory_, filename)
            if not os.path.isfile(full_path) or not full_path.endswith('.json'):
                continue
            result = json.load(open(full_path, 'r'))
            model = os.path.basename(result['model'])
            provider_mode = result['provider_mode']
            file_without_ext = os.path.splitext(filename)[0]
            fullname = "%s-%s-%s" % (file_without_ext, model, provider_mode)
            self.all_files_.append(fullname)
            for key in result:
                if key == 'overall' or key == 'model' or key == 'provider_mode' or key == 'success_rate':
                    continue
                if not key in categories:
                    categories.add(key)
                self.load_category(fullname, model, key, result)
        return categories

    def load(self):
        self.all_problems_ = {}
        self.all_files_ = []
        self.all_categories_ = []
        categories = self.load_all_problems()
        for category in categories:
            self.all_categories_.append(category)
        self.all_files_.sort(key=len)
        self.all_categories_.sort()
        return self.all_files_, self.all_categories_

    def select_problems(self, filename, category):
        selected_problems = []
        for problem in self.all_problems_.values():
            if problem.has_file(filename) and problem.category_ == category:
                selected_problems.append(problem)
        return selected_problems

    def get_problem_by_id(self, id):
        if id in self.all_problems_:
            return self.all_problems_[id]
        return None

    def get_nlp(self, model_name):
        if model_name != 'en' and model_name != 'en_core_web_lg':
            model_name = os.path.join(os.path.dirname(Embeddings.models.__file__), os.path.basename(model_name))
        if model_name not in self.nlp_models_:
            self.nlp_models_[model_name] = spacy.load(model_name, disable=['tagger', 'parser', 'ner', 'textcat'])
        return self.nlp_models_[model_name]

    def get_similarity(self, token1, token2):
        try:
            return token1.similarity(token2)
        except:
            return 0.0

    def get_sentence_compared_tokens(self, sentence1_nlp, sentence2_nlp):
        sentence_compared_tokens = []
        for token1 in sentence1_nlp:
            token1_scores = []
            for token2 in sentence2_nlp:
                token1_scores.append(self.get_similarity(token1, token2))
            sentence_compared_tokens.append(ComparedToken(token1, token1_scores))
        return sentence_compared_tokens

    def get_comparison(self, problem_id, question_index, choice_index, comparison_index, filename):
        problem = self.get_problem_by_id(problem_id)
        comparisons = problem.get_comparisons(filename)
        if question_index > len(comparisons) - 1 or \
           choice_index > len(comparisons[question_index]) - 1 or \
           comparison_index > len(comparisons[question_index][choice_index]) - 1:
            return None
        return comparisons[question_index][choice_index][comparison_index]

    def get_nlp_comparison(self, comparison, model):
        nlp = self.get_nlp(model)
        if comparison is None:
            return NlpComparison([], [])
        q_sentence_nlp = nlp(comparison.q_definition_)
        c_sentence_nlp = nlp(comparison.c_definition_)
        q_sentence_compared_tokens = self.get_sentence_compared_tokens(q_sentence_nlp, c_sentence_nlp)
        c_sentence_compared_tokens = self.get_sentence_compared_tokens(c_sentence_nlp, q_sentence_nlp)
        return NlpComparison(q_sentence_compared_tokens, c_sentence_compared_tokens)
