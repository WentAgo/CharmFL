import json
from itertools import chain
from collections import defaultdict

class Ranks():
    def __init__(self):
        ...
    def calculate_average_ranks(self, scores):
        flattened_scores = list(chain.from_iterable(scores))
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)

        ranks = defaultdict(list)
        for rank, (key, _) in enumerate(sorted_scores, start=1):
            ranks[key].append(rank)

        average_ranks = {key: sum(rank_list) / len(rank_list) for key, rank_list in ranks.items()}
        return average_ranks

    def add_average_ranks_to_statements(self, data):
        statement_scores = []

        def collect_statement_scores(method):
            nonlocal statement_scores
            for statement in method.get("statements", []):
                line = statement.get("line", "")
                tar = statement.get("tar", 0.0)
                statement_scores.append((line, tar))

        for file_data in data.get("files", []):
            for class_data in file_data.get("classes", []):
                for method_data in class_data.get("methods", []):
                    collect_statement_scores(method_data)

        average_ranks = self.calculate_average_ranks(statement_scores)

        for file_data in data.get("files", []):
            for class_data in file_data.get("classes", []):
                for method_data in class_data.get("methods", []):
                    for statement in method_data.get("statements", []):
                        line = statement.get("line", "")
                        statement["tar_rank"] = average_ranks[line]

        return data

    def rerank_based_on_predicates(self, data):
        self.to_json(data)
        for file_data in data['files']:
            for class_data in file_data['classes']:
                for method_data in class_data['methods']:
                    for statement in method_data['statements']:
                        if 'type' in statement:
                            if statement['type'] == 'If':
                                body_ranks = [stmt['tar_rank'] for stmt in method_data['statements'] if
                                              stmt['line'] in map(str, statement['body'])]
                                else_ranks = [stmt['tar_rank'] for stmt in method_data['statements'] if
                                              stmt['line'] in map(str, statement['else'])]
                                max_body_rank = min(body_ranks) if body_ranks else 0
                                max_else_rank = min(else_ranks) if else_ranks else 0
                                new_rank = min(max_body_rank, max_else_rank)
                                if new_rank < statement['tar_rank']:
                                    statement['promoted_tar_rank'] = new_rank-1
        return data

    def to_json(self,data):
        return json.dumps(data, indent=4)

if __name__ == "__main__":
    # Replace 'your_json_data' with your actual JSON data
    with open("C:\\Users\\user\\Documents\\CharmFL\\test_project\\products\\CharmFL\\results.json", "r") as file:
        json_data = json.load(file)
        ranks = Ranks()
        ranks.add_average_ranks_to_statements(json_data)
        print(json_data)