// Simplified-Chinese localization helpers for the OpenVSP GUI.
#ifndef VSPCHINESE__INCLUDED_
#define VSPCHINESE__INCLUDED_

#include <string>

// Translate user-visible GUI text. Unknown technical identifiers are kept.
std::string VSPTranslate( const std::string &text );
std::string VSPTranslate( const char *text );

// Use exact UI messages only when the string may contain user or filesystem data.
// Unknown messages remain byte-for-byte unchanged; never translate embedded values.
std::string VSPTranslateMessage( const std::string &text );

// Translate a known label, then append an opaque user value without interpreting it.
std::string VSPTranslateLabelAndValue( const std::string &label, const std::string &value );

// Translate every component of an FLTK menu path while preserving '/'.
std::string VSPTranslateMenuPath( const std::string &path );

#endif
