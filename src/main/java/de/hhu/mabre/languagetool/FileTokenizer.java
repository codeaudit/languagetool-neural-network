package de.hhu.mabre.languagetool;

import org.languagetool.Language;
import org.languagetool.tokenizers.SentenceTokenizer;
import org.languagetool.tokenizers.Tokenizer;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

import static org.languagetool.Languages.getLanguageForShortCode;

/*
 * Tokenize an input file containing sentences, producing a file containing all tokens separated by spaces.
 */
public class FileTokenizer {
    public static void main(String[] args) {
        if (args.length != 2) {
            System.out.println("Parameters: language-code sentences-file");
            System.exit(-1);
        }

        String languageCode = args[0];
        String sentencesFile = args[1];

        String text = readText(sentencesFile);
        String tokens = String.join(" ", tokenize(languageCode, text));
        createTokensFile(sentencesFile+"-tokens", tokens);
    }

    static String readText(String sentencesFile) {
        System.out.println("Reading " + sentencesFile);
        String text = "";
        try {
            text = String.join("\n", Files.readAllLines(Paths.get(sentencesFile)));
        } catch (IOException e) {
            e.printStackTrace();
        }
        return text;
    }

    private static void createTokensFile(String tokensFile, String tokens) {
        try {
            Files.write(Paths.get(tokensFile), Collections.singletonList(tokens));
            System.out.println("Tokens written to " + tokensFile);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static List<String> tokenize(String languageCode, String text) {
        System.out.println("Tokenizing");
        Tokenizer tokenizer = getTokenizer(languageCode);
        return tokenize(tokenizer, text);
    }

    private static List<String> tokenize(Tokenizer tokenizer, String text) {
        List<String> tokenizedText = tokenizer.tokenize(text);
        return tokenizedText.stream().filter(token -> !token.trim().isEmpty()).collect(Collectors.toList());
    }

    private static Tokenizer getTokenizer(String languageCode) {
        Language language = getLanguageForShortCode(languageCode);
        return language.getWordTokenizer();
    }

    public static List<List<String>> tokenizedSentences(String languageCode, String text) {
        Language language = getLanguageForShortCode(languageCode);
        SentenceTokenizer sentenceTokenizer = language.getSentenceTokenizer();
        List<String> sentences = sentenceTokenizer.tokenize(text);
        Tokenizer tokenizer = getTokenizer(languageCode);
        return sentences.stream().map(sentence -> tokenize(tokenizer, sentence)).collect(Collectors.toList());
    }
}
