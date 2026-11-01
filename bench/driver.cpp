#include "search.hpp"

#include <chrono>
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <string>

using Search = std::size_t (*)(std::string_view, std::string_view);
volatile std::size_t consumed = 0;

std::string load(const char* path) {
    std::ifstream file(path, std::ios::binary);
    if (!file) throw std::runtime_error("cannot open input file");
    std::string bytes((std::istreambuf_iterator<char>(file)), {});
    if (file.bad()) throw std::runtime_error("cannot read input file");
    return bytes;
}

double batch_time(Search search, std::string_view text, std::string_view pattern, std::size_t batch) {
    std::size_t checksum = 0;
    const auto start = std::chrono::steady_clock::now();
    for (std::size_t i = 0; i < batch; ++i) checksum += search(text, pattern);
    const auto end = std::chrono::steady_clock::now();
    consumed = checksum;
    if (checksum != text.find(pattern) * batch) throw std::runtime_error("batch checksum differs from oracle");
    return std::chrono::duration<double, std::nano>(end - start).count();
}

int main(int argc, char** argv) {
    try {
        if (argc != 5) throw std::runtime_error("usage: benchmark TEXT PATTERN REPETITIONS ORDER_SEED");
        const int repetitions = std::stoi(argv[3]);
        const int seed = std::stoi(argv[4]);
        if (repetitions < 1 || repetitions > 100 || seed < 0) throw std::runtime_error("invalid repetitions or seed");
        const auto text = load(argv[1]), pattern = load(argv[2]);
        const auto expected = text.find(pattern);
        Search searches[] = {naive_search, kmp_search};
        const char* names[] = {"naive", "kmp"};
        SearchCounts counts[2];
        if (counted_naive_search(text, pattern, counts[0]) != expected ||
            counted_kmp_search(text, pattern, counts[1]) != expected)
            throw std::runtime_error("counted answer differs from oracle");
        for (auto search : searches)
            if (search(text, pattern) != expected) throw std::runtime_error("answer differs from oracle");

        std::cout << "phase,algorithm,repetition,order,batch,elapsed_ns,result,preprocessing_comparisons,search_comparisons,correct\n";
        auto record = [&](const char* phase, int a, int rep, int order, std::size_t batch) {
            const double elapsed = batch_time(searches[a], text, pattern, batch);
            // validation stays outside the timing window
            if (searches[a](text, pattern) != expected) throw std::runtime_error("post-timing answer differs from oracle");
            std::cout << phase << ',' << names[a] << ',' << rep << ',' << order << ',' << batch << ','
                      << elapsed << ',';
            if (expected == std::string::npos) std::cout << "npos";
            else std::cout << expected;
            std::cout << ',' << counts[a].preprocessing << ',' << counts[a].search << ",true\n";
            return elapsed;
        };
        std::size_t batches[] = {1, 1};
        for (int a = 0; a < 2; ++a) {
            for (int w = 0; w < 3; ++w) record("warmup", a, w, a, 1);
            for (int pilot = 0;; ++pilot) {
                const auto elapsed = record("pilot", a, pilot, a, batches[a]);
                if (elapsed >= 1e6 || batches[a] == 65536) break;
                batches[a] *= 2;
            }
        }
        for (int rep = 0; rep < repetitions; ++rep) {
            for (int order = 0; order < 2; ++order) {
                const int a = (rep + seed + order) % 2;
                record("timing", a, rep, order, batches[a]);
            }
        }
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
