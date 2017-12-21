import sys
from ast import literal_eval
from typing import Callable, List

import numpy as np
from nltk import edit_distance

from EvalResult import EvalResult
from parallel import parmap
from repl import has_error


def evaluate_ngrams(ngrams: [[str]], subjects: [str],
                    check_function: Callable[[List[str]], bool]) -> EvalResult:
    eval_result = EvalResult()
    substitutions = create_substitution_dict(subjects)
    for ngram in ngrams:
        for substitution in substitutions[ngram[2]]:
            eval_ngram = ngram[:]
            eval_ngram[2] = substitution
            error_detected = check_function(eval_ngram)
            if not error_detected and substitution == ngram[2]:
                eval_result.add_tn()
            elif error_detected and substitution == ngram[2]:
                eval_result.add_fp()
                print("false positive:", eval_ngram)
            elif not error_detected and substitution != ngram[2]:
                eval_result.add_fn()
            elif error_detected and substitution != ngram[2]:
                eval_result.add_tp()
    return eval_result


def get_relevant_ngrams(sentences: str, subjects: [str], n: int=5) -> [[str]]:
    ngrams = []
    half_context_length = int(n / 2)
    tokens = sentences.split(" ")
    for i in range(half_context_length, len(tokens) - half_context_length + 1):
        if tokens[i] in subjects:
            ngrams.append(tokens[i-half_context_length:i+half_context_length+1])
    return ngrams


def similar_words(word: str, words: List[str]):
    if len(word) < 4:
        max_distance = 2
    else:
        max_distance = 3
    return list(filter(lambda w: edit_distance(word, w, substitution_cost=1, transpositions=True) <= max_distance,
                       words))


def create_substitution_dict(subjects: List[str]) -> dict:
    return {subject: similar_words(subject, subjects) for subject in subjects}


def main():
    if len(sys.argv) != 5:
        raise ValueError("Expected dict, finalembedding, W, b")

    dictionary_path = sys.argv[1]
    embedding_path = sys.argv[2]
    W_path = sys.argv[3]
    b_path = sys.argv[4]

    with open(dictionary_path) as dictionary_file:
        dictionary = literal_eval(dictionary_file.read())
    embedding = np.loadtxt(embedding_path)
    W = np.loadtxt(W_path)
    b = np.loadtxt(b_path)

    subjects = ["als", "also", "da", "das", "dass", "de", "den", "denn", "die", "durch", "zur", "ihm", "im", "um", "nach", "noch", "war", "was"]
    print(subjects)

    sentences = "Ich glaube , dass es morgen schneit , denn es ist sehr kalt . Der Spieleabend beginnt um 17 Uhr im Raum 25 . Ich war gestern zuhause . Es ist nach dem Öffnen 3 Tage lang haltbar . Wie war dein Urlaub ? Und wie war der Film ? Wir sind da im Urlaub ."
    ngrams = get_relevant_ngrams(sentences, subjects)

    eval_results = parmap(lambda t: evaluate_ngrams(ngrams, subjects, lambda ngram: has_error(dictionary, embedding, W, b, ngram, subjects, error_threshold=t, suggestion_threshold=t)),
                          [.1, .2, .3, .4, .5, .6, .7, .8, .9])
    print(eval_results)


if __name__ == '__main__':
    main()
