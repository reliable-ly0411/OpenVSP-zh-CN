// This file is released under NOSA 1.3; see the repository LICENSE.
#include "FileUtil.h"
#include <cstring>
#ifdef _WIN32
#include <windows.h>
#endif

namespace baseline {
std::vector<fs::path> get_files_matching_pattern(const std::string&);
const char* source_sha256();
}
namespace patched {
std::vector<fs::path> get_files_matching_pattern(const std::string&);
const char* source_sha256();
}

// Python creates the known fixture files and independently checks their bytes
// afterwards. Both variants compile function bodies extracted from real source.
int main(int argc, char** argv)
{
    if (argc != 3) return 2;
    const bool original = !strcmp(argv[1], "baseline");
    if (!original && strcmp(argv[1], "patched")) return 2;
    std::string directory = ".", pattern = "native-analysis*.tag", target = "native-analysis.1.tag";
    if (!strcmp(argv[2], "directory")) directory = u8"\u76ee\u5f55 100%";
    if (!strcmp(argv[2], "unicode-pattern"))
    {
        pattern = u8"native-\u4e2d\u6587*.tag";
        target = u8"native-\u4e2d\u6587.1.tag";
    }
    const char* sha = original ? baseline::source_sha256() : patched::source_sha256();
    try
    {
        const auto files = original ? baseline::get_files_matching_pattern(directory + "/" + pattern)
                                    : patched::get_files_matching_pattern(directory + "/" + pattern);
        const bool exact = files.size() == 1 && files[0] == fs::u8path(directory) / fs::u8path(target);
        printf("{\"source_sha256\":\"%s\",\"matched\":%zu,\"exact_target\":%s,\"exception\":null}\n",
               sha, files.size(), exact ? "true" : "false");
        return 0;
    }
    catch (const std::system_error& error)
    {
        printf("{\"source_sha256\":\"%s\",\"exception\":\"system_error\",\"error_code\":%d}\n",
               sha, error.code().value());
        fprintf(stderr, "Pattern scan exception: %.2048s\n", error.what());
        return 3;
    }
    catch (const std::exception& error)
    {
        printf("{\"source_sha256\":\"%s\",\"exception\":\"std_exception\"}\n", sha);
        fprintf(stderr, "Pattern scan exception: %.2048s\n", error.what());
        return 3;
    }
}
