import json
from itertools import chain
from collections import defaultdict
from scipy.stats import rankdata


class Ranks():
    def __init__(self):
        ...

    def calculate_average_ranks(self, scores, order):
        if order == "desc":
            sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
            scores_dict = dict(sorted_scores)
            average_ranks = dict(
                zip(scores_dict.keys(), rankdata([-i for i in scores_dict.values()], method='average')))

        elif order == "asc":
            sorted_scores = sorted(scores, key=lambda x: x[1], reverse=False)
            scores_dict = dict(sorted_scores)
            average_ranks = dict(
                zip(scores_dict.keys(), rankdata([i for i in scores_dict.values()], method='average')))

        return average_ranks

    def add_average_ranks_to_statements(self, data, version):
        statement_scores = []
        orig_tar_value = "tar"
        target_tar_value = "tar_rank"
        order = "desc"

        def collect_statement_scores(file_path_and_name, method):
            nonlocal statement_scores
            for statement in method.get("statements", []):
                line = statement.get("line", "")
                tar = statement.get(orig_tar_value, 0.0)
                statement_scores.append((file_path_and_name + "::" + line, tar))

        for file_data in data.get("files", []):
            file_path_and_name = file_data.get('relativePath')
            for class_data in file_data.get("classes", []):
                for method_data in class_data.get("methods", []):
                    collect_statement_scores(file_path_and_name, method_data)

        average_ranks = self.calculate_average_ranks(statement_scores, order)

        for file_data in data.get("files", []):
            file_path_and_name = file_data.get('relativePath')
            for class_data in file_data.get("classes", []):
                for method_data in class_data.get("methods", []):
                    for statement in method_data.get("statements", []):
                        line = statement.get("line", "")
                        statement[target_tar_value] = average_ranks[file_path_and_name + "::" + line]

        return data

    def add_average_ranks_from_reranked_to_statements(self, data, version):
        statement_scores = []
        orig_tar_value = "tar_rank"
        target_tar_value = "promoted_tar_rank"
        order = "asc"

        def collect_statement_scores(file_path_and_name, method):
            nonlocal statement_scores
            for statement in method.get("statements", []):
                line = statement.get("line", "")
                tar = statement.get(target_tar_value, statement.get(orig_tar_value))
                statement_scores.append((file_path_and_name + "::" + line, tar))

        for file_data in data.get("files", []):
            file_path_and_name = file_data.get('relativePath')
            for class_data in file_data.get("classes", []):
                for method_data in class_data.get("methods", []):
                    collect_statement_scores(file_path_and_name, method_data)

        average_ranks = self.calculate_average_ranks(statement_scores, order)

        for file_data in data.get("files", []):
            file_path_and_name = file_data.get('relativePath')
            for class_data in file_data.get("classes", []):
                for method_data in class_data.get("methods", []):
                    for statement in method_data.get("statements", []):
                        line = statement.get("line", "")
                        statement[target_tar_value] = average_ranks[file_path_and_name + "::" + line]

        return data

    def rerank_based_on_predicates(self, data):
        # self.to_json(data)
        for file_data in data['files']:
            for class_data in file_data['classes']:
                for method_data in class_data['methods']:
                    for statement in method_data['statements']:
                        if 'type' in statement:
                            if statement['type'] == 'If':
                                if statement["line"] == "373":
                                    print("shit")
                                body_ranks = [stmt['tar_rank'] for stmt in method_data['statements'] if
                                              stmt['line'] in map(str, statement['body'])]
                                else_ranks = [stmt['tar_rank'] for stmt in method_data['statements'] if
                                              stmt['line'] in map(str, statement['else'])]
                                max_body_rank = min(body_ranks) if len(body_ranks) > 0 else statement['tar_rank']
                                max_else_rank = min(else_ranks) if len(else_ranks) > 0 else statement['tar_rank']
                                new_rank = min(max_body_rank, max_else_rank)
                                if new_rank < statement['tar_rank']:
                                    statement['promoted_tar_rank'] = new_rank - 1
                                    print(statement)
        return self.add_average_ranks_from_reranked_to_statements(data, "rerank")

    def to_json(self, data):
        return json.dumps(data, indent=4)


if __name__ == "__main__":
    # Replace 'your_json_data' with your actual JSON data
    with open("C:\\Users\\user\\Documents\\CharmFL\\test_project\\products\\CharmFL\\results.json", "r") as file:
        json_data = json.load(file)
        ranks = Ranks()
        ranks.add_average_ranks_to_statements(json_data)
        print(json_data)
