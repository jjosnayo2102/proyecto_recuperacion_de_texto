#ifndef PROY2DB2_INVERTEDINDEX3_H
#define PROY2DB2_INVERTEDINDEX3_H

#include <iostream>
#include <string>
#include <vector>
#include <set>
#include <map>
#include <unordered_set>
#include <unordered_map>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <cctype>
#include <cmath>
#include <experimental/filesystem>
#include <queue>
#include <utility>

namespace fs = std::experimental::filesystem;

#define PAGE_SIZE 4096

struct Posting {
    int docId;
    double tf;  // term frequency

    bool operator<(const Posting& other) const {
        return docId < other.docId;
    }

    // Constructor
    // Constructor por defecto
    Posting() : docId(0), tf(0.0) {}

    // Constructor que toma los valores directamente
    Posting(int docId, double tf) : docId(docId), tf(tf) {}
};

struct SearchResult {
    int docId;
    double score;
    std::string original_row;  // Almacena la fila original del CSV

    bool operator<(const SearchResult& other) const {
        return score < other.score;  // Para cola de prioridad en orden descendente
    }
};

class InvertedIndex3 {
private:
    std::unordered_set<std::string> stopwords;
    std::vector<std::string> terms;
    int currentBlock = 0;
    std::string csvFilename;  // Guardar nombre del archivo CSV
    // Estructura para el índice invertido en memoria
    std::unordered_map<std::string, std::vector<Posting>> inMemoryIndex;
    size_t currentMemoryUsage = 0;
    std::unordered_map<int, double> documentNorms;  // Normas de los documentos

    // Funciones auxiliares previas...
    std::string toLowerCase(const std::string& str) {
        std::string result = str;
        std::transform(result.begin(), result.end(), result.begin(), ::tolower);
        return result;
    }

    std::vector<std::string> tokenize(const std::string& str) {
        std::vector<std::string> tokens;
        std::string token;
        std::istringstream tokenStream(str);

        while (std::getline(tokenStream, token, ' ')) {
            if (token.empty()) continue;

            token.erase(
                    std::remove_if(token.begin(), token.end(),
                                   [](char c) { return !std::isalnum(c); }),
                    token.end()
            );

            if (!token.empty()) {
                tokens.push_back(toLowerCase(token));
            }
        }
        return tokens;
    }

    std::string stem(const std::string& word) {
        if (word.length() <= 3) return word;

        std::string stemmed = word;
        std::vector<std::string> suffixes = {"ing", "ed", "es", "s"};

        for (const auto& suffix : suffixes) {
            if (stemmed.length() > suffix.length() &&
                stemmed.substr(stemmed.length() - suffix.length()) == suffix) {
                stemmed = stemmed.substr(0, stemmed.length() - suffix.length());
                break;
            }
        }
        return stemmed;
    }

    void createDirectories() {
        if (!fs::exists("blocks")) {
            fs::create_directories("blocks");
        }
    }

    std::string getBlockPath(int blockNum) {
        return "blocks/block_" + std::to_string(blockNum) + ".idx";
    }

    std::string getFinalIndexPath() {
        return "blocks/final_index.idx";
    }

    double calculateTFIDF(int tf, int N, int df) {
        if (df == 0) return 0.0;
        double idf = log10(static_cast<double>(N) / df);
        return (1 + log10(static_cast<double>(tf))) * idf;
    }

    void calculateDocumentNorm(int docId, const std::unordered_map<std::string, int>& termFreqs, int totalDocs) {
        double norm = 0.0;
        for (const auto& [term, tf] : termFreqs) {
            int df = getDocumentFrequency(term);
            double tfidf = calculateTFIDF(tf, totalDocs, df);
            norm += tfidf * tfidf;
        }
        documentNorms[docId] = sqrt(norm);
    }

    int getDocumentFrequency(const std::string& term) {
        std::ifstream indexFile(getFinalIndexPath(), std::ios::binary);
        if (!indexFile) return 0;

        std::pair<std::string, std::vector<Posting>> termData;
        while (readNextTerm(indexFile, termData)) {
            if (termData.first == term) {
                return termData.second.size();
            }
        }
        return 0;
    }

    std::string getOriginalRow(int docId) {
        std::ifstream csvFile(csvFilename);
        if (!csvFile) return "";

        std::string line;
        int currentId = -1;

        // Skip header
        std::getline(csvFile, line);

        while (std::getline(csvFile, line)) {
            currentId++;
            if (currentId == docId) {
                return line;
            }
        }
        return "";
    }

    size_t estimateMemoryUsage(const std::string& term, const std::vector<Posting>& postings) {
        return sizeof(std::string) + term.capacity() +
               sizeof(std::vector<Posting>) + postings.capacity() * sizeof(Posting);
    }

    void writeBlockToDisk() {
        if (inMemoryIndex.empty()) return;

        std::string blockPath = getBlockPath(currentBlock);
        std::ofstream outFile(blockPath, std::ios::binary);
        if (!outFile) {
            throw std::runtime_error("Cannot create block file: " + blockPath);
        }

        std::vector<std::string> sortedTerms;
        for (const auto& entry : inMemoryIndex) {
            sortedTerms.push_back(entry.first);
        }
        std::sort(sortedTerms.begin(), sortedTerms.end());

        for (const auto& term : sortedTerms) {
            auto& postings = inMemoryIndex[term];
            std::sort(postings.begin(), postings.end());

            size_t termLen = term.length();
            outFile.write(reinterpret_cast<const char*>(&termLen), sizeof(size_t));
            outFile.write(term.c_str(), termLen);

            size_t postingsCount = postings.size();
            outFile.write(reinterpret_cast<const char*>(&postingsCount), sizeof(size_t));
            outFile.write(reinterpret_cast<const char*>(postings.data()),
                          postings.size() * sizeof(Posting));
        }

        outFile.close();
        inMemoryIndex.clear();
        currentMemoryUsage = 0;
        currentBlock++;
    }

    void writeTermToFinalIndex(std::ofstream& file, const std::string& term,
                               const std::vector<std::pair<int, Posting>>& postings) {
        // Escribir término
        size_t termLen = term.length();
        file.write(reinterpret_cast<const char*>(&termLen), sizeof(size_t));
        file.write(term.c_str(), termLen);

        // Escribir postings
        std::vector<Posting> mergedPostings;
        for (const auto& posting : postings) {
            mergedPostings.push_back(posting.second);
        }

        // Ordenar y eliminar duplicados
        std::sort(mergedPostings.begin(), mergedPostings.end());
        mergedPostings.erase(
                std::unique(mergedPostings.begin(), mergedPostings.end(),
                            [](const Posting& a, const Posting& b) { return a.docId == b.docId; }),
                mergedPostings.end()
        );

        size_t postingsCount = mergedPostings.size();
        file.write(reinterpret_cast<const char*>(&postingsCount), sizeof(size_t));
        file.write(reinterpret_cast<const char*>(mergedPostings.data()),
                   mergedPostings.size() * sizeof(Posting));
    }

    void mergeBlocks() {
        std::vector<std::ifstream> blocks;
        std::map<std::string, std::vector<std::pair<int, Posting>>> termBuffer;

        for (int i = 0; i < currentBlock; i++) {
            blocks.emplace_back("block_" + std::to_string(i) + ".idx", std::ios::binary);
        }

        std::vector<std::pair<std::string, std::vector<Posting>>> currentTerms(blocks.size());

        for (size_t i = 0; i < blocks.size(); i++) {
            if (readNextTerm(blocks[i], currentTerms[i])) {
                if (!currentTerms[i].first.empty()) {
                    termBuffer[currentTerms[i].first].push_back({i, currentTerms[i].second[0]});
                }
            }
        }

        std::ofstream finalIndex("final_index.idx", std::ios::binary);

        while (!termBuffer.empty()) {
            auto currentTerm = termBuffer.begin()->first;
            auto& postings = termBuffer.begin()->second;

            writeTermToFinalIndex(finalIndex, currentTerm, postings);

            termBuffer.erase(termBuffer.begin());
        }

        for (auto& block : blocks) {
            block.close();
        }
    }

    bool readNextTerm(std::ifstream& block, std::pair<std::string, std::vector<Posting>>& termData) {
        size_t termLen;
        block.read(reinterpret_cast<char*>(&termLen), sizeof(size_t));

        if (block.eof()) return false;

        termData.first.resize(termLen);
        block.read(&termData.first[0], termLen);

        size_t postingsCount;
        block.read(reinterpret_cast<char*>(&postingsCount), sizeof(size_t));
        termData.second.resize(postingsCount);

        block.read(reinterpret_cast<char*>(&termData.second[0]),
                   postingsCount * sizeof(Posting));

        return true;
    }

public:
    InvertedIndex3() {
        createDirectories();
    }

    void processCSV(const std::string& filename, int totalDocs) {
        csvFilename = filename;
        std::ifstream file(filename);
        if (!file) {
            throw std::runtime_error("No se pudo abrir el archivo CSV.");
        }

        std::string line;
        int docId = 0;
        // Skip header line
        std::getline(file, line);

        while (std::getline(file, line) && docId < totalDocs) {
            std::vector<std::string> tokens = tokenize(line);
            std::unordered_map<std::string, int> termFreqs;

            for (const auto& token : tokens) {
                if (stopwords.find(token) == stopwords.end()) {
                    std::string stemmedToken = stem(token);
                    termFreqs[stemmedToken]++;
                }
            }

            // Save postings for each term in this document
            for (const auto& [term, tf] : termFreqs) {
                Posting posting{docId, static_cast<double>(tf)};
                inMemoryIndex[term].push_back(posting);
            }

            docId++;

            // Write the block to disk if memory usage exceeds a threshold
            if (currentMemoryUsage > PAGE_SIZE) {
                writeBlockToDisk();
            }
        }

        file.close();
    }

    std::vector<SearchResult> search(const std::string& query, int topK, int totalDocs) {
        std::vector<std::string> queryTerms = tokenize(query);
        std::unordered_map<std::string, int> queryTermFreqs;

        for (const auto& term : queryTerms) {
            if (stopwords.find(term) == stopwords.end()) {
                std::string stemmedTerm = stem(term);
                queryTermFreqs[stemmedTerm]++;
            }
        }

        // Search for the query terms in the index and calculate scores
        std::unordered_map<int, double> docScores;

        for (const auto& [term, tf] : queryTermFreqs) {
            auto it = inMemoryIndex.find(term);
            if (it == inMemoryIndex.end()) continue;

            const auto& postings = it->second;
            int df = postings.size();

            for (const auto& posting : postings) {
                double score = calculateTFIDF(posting.tf, totalDocs, df);
                docScores[posting.docId] += score;
            }
        }

        // Rank documents based on scores
        std::priority_queue<SearchResult> rankedResults;

        for (const auto& [docId, score] : docScores) {
            std::string originalRow = getOriginalRow(docId);
            SearchResult result = {docId, score, originalRow};
            rankedResults.push(result);
        }

        std::vector<SearchResult> topResults;
        for (int i = 0; i < topK && !rankedResults.empty(); i++) {
            topResults.push_back(rankedResults.top());
            rankedResults.pop();
        }

        return topResults;
    }
};

#endif