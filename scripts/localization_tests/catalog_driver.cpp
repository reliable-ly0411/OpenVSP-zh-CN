#include "VSPChinese.h"
#include <iostream>
#include <string>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif

// NUL framing preserves multiline messages, tabs, CRLF, and printf templates.
int main( int argc, char **argv )
{
#ifdef _WIN32
    _setmode( _fileno( stdin ), _O_BINARY );
    _setmode( _fileno( stdout ), _O_BINARY );
#endif
    const std::string mode = argc > 1 ? argv[1] : "translate";
    if ( mode != "translate" && mode != "menu" && mode != "header" )
    {
        return 2;
    }
    std::string text;
    while ( std::getline( std::cin, text, '\0' ) )
    {
        const std::string result = mode == "menu" ? VSPTranslateMenuPath( text ) :
                                   mode == "header" ? VSPTranslateBrowserHeader( text ) :
                                   VSPTranslate( text );
        std::cout << result << '\0';
    }
    return std::cin.bad() || std::cout.bad() ? 1 : 0;
}
