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

// Translate a static label in a compact table header without changing its general translation.
std::string VSPTranslateCompactTableHeader( const std::string &text );

// Translate static labels in narrow airfoil/wing-section controls.
std::string VSPTranslateCompactWingLabel( const std::string &text );

// Translate every component of an FLTK menu path while preserving '/'.
std::string VSPTranslateMenuPath( const std::string &path );

// Translate only application-owned FLTK browser headings. Never use on data rows.
// Column separators and the recognized @b@./@b@c@. formatting are preserved.
std::string VSPTranslateBrowserHeader( const std::string &header );

// Translate the on-screen copy of a Planar Slice report, never its exported bytes.
std::string VSPTranslatePlanarSliceReport( const std::string &report );

// Translate only the on-screen copy of a Component Geometry TXT report.
std::string VSPTranslateCompGeomReport( const std::string &report );

#endif
