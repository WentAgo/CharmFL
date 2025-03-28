import json
import os
import sys

class Spectra:
    def __init__(self):
        self.spectrum = {}
        self.SEPARATOR_CHARACTER = "::"


    def create_spectrum_from(self, coverage_object, test_object):
        test_result = test_object.get_tests_results()
        coverage_result = coverage_object.get_coverage_with_context()

        number_of_fails = test_object.get_number_of_failed_test_cases()
        number_of_pass = test_object.get_number_of_passed_test_cases()



        for file, cov_elements in coverage_result.items():
            for code_element, covered_tests in cov_elements.items():
                ef, ep = 0, 0
                for test in covered_tests:
                    h = self.heuristic_analyzer(test)
                    #if test in test_result:
                    counted_tests = [t for t in test_result if str(t).endswith(test)]
                    if len(counted_tests) == 1:
                        ef = ef + 1 if test_result[counted_tests[0]] == "FAILED" else ef
                        ep = ep + 1 if test_result[counted_tests[0]] == "PASSED" and h != "put" else ep
                    else:
                        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
                        print(test)
                nf = number_of_fails - ef
                np = number_of_pass - ep
                self.spectrum[str(file)+self.SEPARATOR_CHARACTER+str(code_element)] = {"ef": ef, "ep":ep, "nf":nf,"np":np}

    def heuristic_analyzer(self,test):
        #chains from JSON
        project_path = os.path.abspath("callchains.json")

        with open(project_path) as file:
            # print(f"{os.path.dirname(os.path.abspath(projectdir))}/D4J/{project}" + str(bugid) + "heuristics.txt")
            data = file.read()
            call_chains = json.loads(data)

        chains = call_chains[test]
        # Flatten the list of chains and count their occurrences

        chain_lengths = len(chains)

        # Rule 1: A test with only one chain of any length is a unit test
        if all([len(elem) == 1 for elem in chains]) and 0 < chain_lengths <= 1:
            return "put"

        if all([len(elem) <= 2 for elem in chains]) and chain_lengths > 0:
            return "smt"

        # # Rule 2: If a test has multiple chains but they are consistent in length except for the last method
        # if len(length_counts) > 1:
        #     unique_lengths = sorted(length_counts.keys())
        #     if len(unique_lengths) == 2 and unique_lengths[1] - unique_lengths[0] == 1:
        #         unit_tests.append(test_name)
        #         continue

        if chain_lengths == 1:
            if all([len(elem) <= 3 for elem in chains]):
                # Rule 2: Single chain but not longer than 3
                return "lmc"
            # Rule 3: Single chain from test
            return "smc"

    def get_spectrum(self):
        return self.spectrum

    # def dump_json(self):
    #     output = open('spectrum.json', 'w')
    #     json.dump(self.spectrum, output)

