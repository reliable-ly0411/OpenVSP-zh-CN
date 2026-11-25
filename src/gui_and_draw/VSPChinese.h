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

// Translate only the built-in Split/Stitch export failure reasons at the alert boundary.
std::string VSPTranslateSplitStitchReason( const std::string &reason );

// Translate the fixed VSPAERO geometry overlap warning prefix, preserving the raw names.
std::string VSPTranslateGeometrySetOverlapWarning( const std::string &message, bool is_overlap_warning );

// Translate fixed Results Viewer type names, not the result key, type schema, or value.
std::string VSPTranslateResultType( const std::string &type );

// Translate fixed Trimmed Surfaces progress text without changing counters or arbitrary logs.
std::string VSPTranslateTrimmedSurfaceLog( const std::string &text );
std::string VSPTranslateFeaConsoleLog( const std::string &text );
std::string VSPTranslateCfdMeshConsoleLog( const std::string &text );

// Translate a known label, then append an opaque user value without interpreting it.
std::string VSPTranslateSubsurfaceType( const std::string &type_name );
std::string VSPTranslateLabelAndValue( const std::string &label, const std::string &value );

// Translate a static label in a compact table header without changing its general translation.
std::string VSPTranslateCompactTableHeader( const std::string &text );

// Translate static labels in narrow airfoil/wing-section controls.
std::string VSPTranslateCompactWingLabel( const std::string &text );

// Translate a known built-in rendering preset only. Never pass an authored name.
std::string VSPTranslateMaterialPreset( const std::string &name );

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
