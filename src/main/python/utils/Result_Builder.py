import json
import ast


class Result_Builder():
    def __init__(self):
        self.path_to_root = ""
        self.line_scores = {}
        self.method_scores = {}
        self.class_scores = {}
        self.results_dictionary = {"files": []}
        self.FILE_NAME_INDEX = 0
        self.NAME_INDEX = 1
        self.START_LINE_INDEX = 2
        self.END_LINE_INDEX = 3
        self.NOT_FOUND_CONTEXT_INDEX = -1
        self.SEPARATOR_CHARACTER = "::"
        self.control_flow_dict = {}

    def set_path_to_root(self, path_to_root):
        self.path_to_root = path_to_root
        return self

    def set_line_scores(self, line_score_dictionary):
        self.line_scores = line_score_dictionary
        return self


    def set_method_scores(self, method_score_dictionary):
        self.method_scores = method_score_dictionary
        return self

    def set_class_scores(self, class_score_dictionary):
        self.class_scores = class_score_dictionary
        return self

    def set_control_flow(self):
        list_of_file_paths = []
        for file_name_and_line in self.line_scores.keys():
            file_path = str(file_name_and_line).split("::")[0]
            if file_path not in list_of_file_paths:
                list_of_file_paths.append(file_path)
        for file_name in list_of_file_paths:
            with open(file_name, encoding="utf8") as f:
                file_data = f.read()
                self.control_flow_dict[file_name] = self.__search_control_flow_nodes(file_data)

        return self

    def produce_results(self):
        LINE_NUMBER_INDEX = 1
        for key, line_scores in self.line_scores.items():
            print(key, line_scores)
            file_name = str(key).split(self.SEPARATOR_CHARACTER)[self.FILE_NAME_INDEX]
            #with open(file_name, encoding="utf8") as f:
                #file_data = f.read()
                #self.control_flow_dict = self.__search_control_flow_nodes(file_data)
            absolute_path_to_root, relative_path = self.__separate_absolute_and_relative_path(file_name)
            line_num = str(key).split(self.SEPARATOR_CHARACTER)[LINE_NUMBER_INDEX]
            class_name, class_start_line_num, class_tar, class_och, class_wong2, class_dstar = self.__get_lines_context_info(
                self.class_scores, file_name, line_num)
            method_name, method_start_line_num, method_tar, method_och, method_wong2, method_dstar = self.__get_lines_context_info(
                self.method_scores, file_name, line_num)
            context_scores_and_info = {"absolute_path_to_root": absolute_path_to_root,
                                       "relative_path": relative_path,
                                       "line_num": line_num,
                                       "class_name": class_name, "class_start_line_num": class_start_line_num,
                                       "class_tar": class_tar,
                                       "class_och": class_och, "class_wong2": class_wong2,
                                       "class_dstar": class_dstar,
                                       "method_name": method_name, "method_start_line_num": method_start_line_num,
                                       "method_tar": method_tar, "method_och": method_och,
                                       "method_wong2": method_wong2,
                                       "method_dstar": method_dstar}
            self.__put_line_scores_to_place(context_scores_and_info, line_scores)
        return self

    def toJSON(self):
        return json.dumps(self.results_dictionary, indent=4)

    def get_score_results(self):
        return self.results_dictionary

    def __search_control_flow_nodes(self, code):
        # Parse the source code into an AST
        tree = ast.parse(code)

        # Dictionary to store control flow nodes and their bodies with line numbers
        control_flow_dict = {}

        # Visitor class to traverse the AST and search for control flow nodes
        class ControlFlowNodeVisitor(ast.NodeVisitor):
            def visit_If(self, node):
                body_statements = [statement.lineno for statement in node.body]

                if len(node.orelse) > 0:
                    if not isinstance(node.orelse[0], ast.If):
                        last_else_statements = [statement.lineno for statement in node.orelse]
                    else:
                        last_else_statements = self.__get_last_else_statements(node.orelse[0])
                else:
                    last_else_statements = []

                control_flow_dict[node.lineno] = {
                    'type': 'If',
                    'body': body_statements,
                    'else': last_else_statements
                }
                self.generic_visit(node)

            def visit_For(self, node):
                body_statements = [statement.lineno for statement in node.body]
                control_flow_dict[node.lineno] = {
                    'type': 'For',
                    'body': body_statements
                }
                self.generic_visit(node)

            def visit_While(self, node):
                body_statements = [statement.lineno for statement in node.body]
                control_flow_dict[node.lineno] = {
                    'type': 'While',
                    'body': body_statements
                }
                self.generic_visit(node)

            def visit_Try(self, node):
                body_statements = [statement.lineno for statement in node.body]
                control_flow_dict[node.lineno] = {
                    'type': 'Try',
                    'body': body_statements
                }
                self.generic_visit(node)

            def visit_ExceptHandler(self, node):
                body_statements = [statement.lineno for statement in node.body]
                control_flow_dict[node.lineno] = {
                    'type': 'Except',
                    'body': body_statements
                }
                self.generic_visit(node)

            def visit_With(self, node):
                body_statements = [statement.lineno for statement in node.body]
                control_flow_dict[node.lineno] = {
                    'type': 'With',
                    'body': body_statements
                }
                self.generic_visit(node)

            def visit_FunctionDef(self, node):
                self.generic_visit(node)

            def visit_ClassDef(self, node):
                self.generic_visit(node)

            def __get_last_else_statements(self, node):
                if isinstance(node, ast.If):
                    if node.orelse:
                        if isinstance(node.orelse[0], ast.If):
                            return self.__get_last_else_statements(node.orelse[0])
                        else:
                            return self.__get_last_else_statements(node.orelse)
                    else:
                        return []
                else:
                    return [statement.lineno for statement in node]

        # Create an instance of the visitor and visit the AST
        visitor = ControlFlowNodeVisitor()
        visitor.visit(tree)

        return control_flow_dict

    def __get_last_else_statements(self, node):
        if isinstance(node, ast.If):
            if node.orelse:
                if isinstance(node.orelse[0], ast.If):
                    return self.__get_last_else_statements(node.orelse[0])
                else:
                    return self.__get_last_else_statements(node.orelse)
            else:
                return []
        else:
            return [statement.lineno for statement in node]

    def __separate_absolute_and_relative_path(self, fullpath):
        absolute_path = fullpath[:len(self.path_to_root) + 1]
        relative_path = fullpath[len(absolute_path):]
        return absolute_path, relative_path

    def __put_line_scores_to_place(self, context_scores_and_info, line_scores):
        relative_path_index = self.__get_index_of_context_containing_property(self.results_dictionary["files"],
                                                                              "relativePath",
                                                                              context_scores_and_info["relative_path"])
        if relative_path_index == self.NOT_FOUND_CONTEXT_INDEX:
            self.__append_file_to_results_dict(context_scores_and_info, line_scores)
        else:
            class_index = self.__get_index_of_context_containing_property(
                self.results_dictionary["files"][relative_path_index]["classes"], "line",
                context_scores_and_info[
                    "class_start_line_num"])
            if class_index == self.NOT_FOUND_CONTEXT_INDEX:
                self.results_dictionary["files"][relative_path_index]["classes"].append(
                    self.__get_class_scores_dictionary(context_scores_and_info, line_scores))
            else:
                method_index = self.__get_index_of_context_containing_property(
                    self.results_dictionary["files"][relative_path_index]["classes"][class_index]["methods"], "line",
                    context_scores_and_info[
                        "method_start_line_num"])
                if method_index == self.NOT_FOUND_CONTEXT_INDEX:
                    self.results_dictionary["files"][relative_path_index]["classes"][class_index]["methods"].append(
                        self.__get_method_scores_dictionary(context_scores_and_info, line_scores))
                else:
                    self.results_dictionary["files"][relative_path_index]["classes"][class_index][
                        "methods"][method_index]["statements"].append(
                        self.__get_line_scores_dictionary(context_scores_and_info, line_scores))

    def __append_file_to_results_dict(self, context_scores_and_info, line_scores):
        self.results_dictionary["files"].append(
            {"pathToRoot": context_scores_and_info["absolute_path_to_root"],
             "relativePath": context_scores_and_info["relative_path"],
             "classes": [self.__get_class_scores_dictionary(context_scores_and_info, line_scores)]}
        )

    def __get_path_scores_dictionary(self, context_scores_and_info, line_scores):
        return {"pathToRoot": context_scores_and_info["absolute_path_to_root"],
                "relativePath": context_scores_and_info["relative_path"],
                "classes": [self.__get_class_scores_dictionary(context_scores_and_info, line_scores)]}

    def __get_class_scores_dictionary(self, context_scores_and_info, line_scores):
        return {"name": context_scores_and_info["class_name"],
                "line": context_scores_and_info["class_start_line_num"],
                "tar": context_scores_and_info["class_tar"], "och": context_scores_and_info["class_och"],
                "wong2": context_scores_and_info["class_wong2"], "dstar": context_scores_and_info["class_dstar"],
                "methods": [self.__get_method_scores_dictionary(context_scores_and_info, line_scores)
                            ]}

    def __get_method_scores_dictionary(self, context_scores_and_info, line_scores):
        return {"name": context_scores_and_info["method_name"],
                "line": context_scores_and_info["method_start_line_num"],
                "tar": context_scores_and_info["method_tar"],
                "och": context_scores_and_info["method_och"],
                "wong2": context_scores_and_info["method_wong2"],
                "dstar": context_scores_and_info["method_dstar"],
                "statements": [self.__get_line_scores_dictionary(context_scores_and_info, line_scores)
                               ]}

    def __get_line_scores_dictionary(self, context_scores_and_info, line_scores):
        file_name = context_scores_and_info['absolute_path_to_root'] + context_scores_and_info['relative_path']
        if int(context_scores_and_info["line_num"]) in self.control_flow_dict[file_name].keys():
            return {"line": context_scores_and_info["line_num"], "tar": line_scores["tar"],
                    "och": line_scores["och"],
                    "wong2": line_scores["wong2"],
                    "dstar": line_scores["dstar"],
                    "faulty": "false",
                    "type": self.control_flow_dict[file_name][int(context_scores_and_info["line_num"])]["type"],
                    "body": self.control_flow_dict[file_name][int(context_scores_and_info["line_num"])]["body"],
                    "else": self.control_flow_dict[file_name][int(context_scores_and_info["line_num"])]["else"] if "else" in self.control_flow_dict[file_name][int(context_scores_and_info["line_num"])].keys() else ""
                    }
        else:
            return {"line": context_scores_and_info["line_num"], "tar": line_scores["tar"],
                    "och": line_scores["och"],
                    "wong2": line_scores["wong2"],
                    "dstar": line_scores["dstar"],
                    "faulty": "false"
                    }

    def __get_index_of_context_containing_property(self, list_in_dict, property_name, context_value):
        for idx, element in enumerate(list_in_dict):
            if list_in_dict[idx][str(property_name)] == context_value:
                return idx
        return self.NOT_FOUND_CONTEXT_INDEX

    def __get_lines_context_info(self, context_scores, file_name, line_number):
        for key, value in context_scores.items():
            context_file_name = str(key).split(self.SEPARATOR_CHARACTER)[self.FILE_NAME_INDEX]
            context_name = str(key).split(self.SEPARATOR_CHARACTER)[self.NAME_INDEX]
            context_start_line_number = str(key).split(self.SEPARATOR_CHARACTER)[self.START_LINE_INDEX]
            context_end_line_number = str(key).split(self.SEPARATOR_CHARACTER)[self.END_LINE_INDEX]
            tar_score = context_scores[key]["tar"]
            och_score = context_scores[key]["och"]
            wong2_score = context_scores[key]["wong2"]
            dstar_score = context_scores[key]["dstar"]

            if context_file_name == file_name and int(context_start_line_number) < int(line_number) <= int(
                    context_end_line_number):
                return context_name, context_start_line_number, tar_score, och_score, wong2_score, dstar_score

        context_name = ""
        context_start_line_number = 0
        tar_score = 0
        och_score = 0
        wong2_score = 0
        dstar_score = 0
        return context_name, context_start_line_number, tar_score, och_score, wong2_score, dstar_score
