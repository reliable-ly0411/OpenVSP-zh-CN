// Simplified-Chinese localization helpers for the OpenVSP GUI.
#ifndef VSPCHINESE__INCLUDED_
#define VSPCHINESE__INCLUDED_

#include <string>

// Translate user-visible GUI text. Unknown technical identifiers are kept.
std::string VSPTranslate( const std::string &text );
std::string VSPTranslate( const char *text );

// Translate every component of an FLTK menu path while preserving '/'.
std::string VSPTranslateMenuPath( const std::string &path );

#endif
