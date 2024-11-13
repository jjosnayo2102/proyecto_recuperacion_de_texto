//version1
//#include <iostream>
//#include "InvertedIndex.h"
//
//int main() {
//    try {
//        InvertedIndex index;
//        const int TOTAL_DOCS = 50;  // O el número que uses
//        const int TOP_K = 5;         // Número de resultados a mostrar
//
//        // Procesar CSV y crear índice
//        index.processCSV("spotify_songs.csv", TOTAL_DOCS);
//        std::cout<<"\nSe procesó el csv.\n";
//        std::cout<<"\nIniciando búsqueda...\n";
//        // Realizar búsqueda
//        std::string query = "love";
//        auto results = index.search(query, TOP_K, TOTAL_DOCS);
//
//        // Mostrar resultados
//        std::cout << "\nResultados para la búsqueda '" << query << "':\n\n";
//
//        for (int i = 0; i < results.size(); i++) {
//            std::cout << "Resultado " << (i + 1) << ":\n";
//            std::cout << "Score: " << results[i].score << "\n";
//            std::cout << "DocID: " << results[i].docId << "\n";
//            std::cout << "Documento: " << results[i].original_row << "\n\n";
//        }
//
//    } catch (const std::exception& e) {
//        std::cerr << "Error: " << e.what() << std::endl;
//        return 1;
//    }
//
//    return 0;
//}

//=================================================version2=========================================
//#include <iostream>
//#include "InvertedIndex2.h"
//
//int main() {
//    try {
//        std::cout << "Iniciando programa..." << std::endl;
//
//        InvertedIndex2 index;
//        const int TOTAL_DOCS = 50;
//        const int TOP_K = 5;
//
//        std::cout << "Procesando archivo CSV..." << std::endl;
//
//        try {
//            index.processCSV("spotify_songs.csv", TOTAL_DOCS);
//            std::cout << "CSV procesado exitosamente." << std::endl;
//        } catch (const std::exception& e) {
//            std::cerr << "Error procesando CSV: " << e.what() << std::endl;
//            return 1;
//        }
//
//        std::cout << "Realizando búsqueda..." << std::endl;
//
//        try {
//            std::string query = "thunder love";
//            auto results = index.search(query, TOP_K, TOTAL_DOCS);
//
//            std::cout << "Resultados para la búsqueda '" << query << "':" << std::endl;
//
//            for (size_t i = 0; i < results.size(); i++) {
//                std::cout << "Resultado " << (i + 1) << ":" << std::endl;
//                std::cout << "Score: " << results[i].score << std::endl;
//                std::cout << "DocID: " << results[i].docId << std::endl;
//                std::cout << "Documento: " << results[i].original_row << std::endl << std::endl;
//            }
//        } catch (const std::exception& e) {
//            std::cerr << "Error en la búsqueda: " << e.what() << std::endl;
//            return 1;
//        }
//
//    } catch (const std::exception& e) {
//        std::cerr << "Error general: " << e.what() << std::endl;
//        return 1;
//    }
//
//    return 0;
//}

//============================================version3===============================================
#include <iostream>
#include "InvertedIndex3.h"

int main() {
    try {
        InvertedIndex3 index;
        const int TOTAL_DOCS = 10000;  // Número de documentos a procesar
        const int TOP_K = 5;         // Número de resultados a mostrar

        // Procesar el archivo CSV y crear el índice
        index.processCSV("spotify_songs.csv", TOTAL_DOCS);
        std::cout << "\nSe procesó el CSV.\n";
        std::cout << "\nIniciando búsqueda...\n";

        // Realizar búsqueda
        std::string query = "sweet child";  // Consulta en lenguaje natural
        auto results = index.search(query, TOP_K, TOTAL_DOCS);

        // Mostrar los resultados
        std::cout << "\nResultados para la búsqueda '" << query << "':\n\n";
        for (int i = 0; i < results.size(); i++) {
            std::cout << "Resultado " << (i + 1) << ":\n";
            std::cout << "Score: " << results[i].score << "\n";
            std::cout << "DocID: " << results[i].docId << "\n";
            std::cout << "Documento: " << results[i].original_row << "\n\n";
        }

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}