// Execute the production GroupLayout constructors with label-recording doubles.
// The generated definitions are read from GroupLayout.cpp and the three actual
// dynamic call sites. This is a focused test, not native FLTK/GUI acceptance.
#include "VSPChinese.h"
#include <cassert>
#include <iostream>
#include <string>
#include <vector>
using std::string;
using Fl_Color = unsigned int;
const int FL_HELVETICA_BOLD = 1, FL_DARK_BLUE = 2, FL_ALIGN_NOWRAP = 3;
const int FL_BORDER_BOX = 4, FL_FOREGROUND_COLOR = 5, FL_BACKGROUND2_COLOR = 6;
const int FL_BACKGROUND_COLOR = 7, FL_BLACK = 8, FL_THIN_UP_BOX = 9;
namespace Fl
{
void get_color(Fl_Color color, unsigned char& r, unsigned char& g, unsigned char& b)
{
    r = g = b = color == FL_DARK_BLUE ? 0 : 255;
}
}
struct Widget
{
    int x, y, w, h;
    string label;
    Fl_Color background = 0;
    bool output = false;
    Widget(int xx, int yy, int ww, int hh, const char* text = nullptr)
        : x(xx), y(yy), w(ww), h(hh), label(text ? text : "") {}
    virtual ~Widget() {}
    void copy_label(const char* text) { label = text ? text : ""; }
    void labelfont(int) {}
    void labelsize(int) {}
    void labelcolor(int) {}
    void align(int) {}
    void box(int) {}
    void color(Fl_Color value) { background = value; }
    void set_output() { output = true; }
};
struct Fl_Button : Widget { using Widget::Widget; };
struct Fl_Box : Widget { using Widget::Widget; };
struct Group
{
    std::vector<Widget*> children;
    void add(Widget* widget) { children.push_back(widget); }
    ~Group() { for (auto child : children) delete child; }
};
struct TriggerButton
{
    Fl_Button* widget = nullptr;
    void Init(void*, Fl_Button* button) { widget = button; }
};
struct GroupLayout
{
    Group group;
    Group* m_Group = &group;
    void* m_Screen = this;
    int m_X = 0, m_Y = 0, m_ButtonWidth = 200, m_StdHeight = 20, m_DividerHeight = 15;
    int FitWidth(int used, int width) { return width - used; }
    void DebugLabelSize(Widget*) {}
    void AddX(int width) { m_X += width; }
    void AddY(int height) { m_Y += height; }
    void NewLineX() { m_X = 0; }
#include "layout_label_declarations.inc"
};
#include "layout_label_definitions.inc"

int main()
{
    const std::vector<string> names = {
        "Fuselage", "Wing", "Export", "Cancel", "Center", "CG", "Pod_3",
        "主翼", "用户模型_7", "Wing&Body_1", "Wing &amp; Body", "Wing / Fuselage: Export_100%",
        "@b@.Wing|Left:Right", "C:\\Wing\\Export", "%s %n 100%", "", "  Wing  "
    };
    int failures = 0;
    const auto check = [&failures](bool ok, const char* reason) {
        if (!ok) { std::cerr << reason << '\n'; ++failures; }
    };
    for (const auto& name : names)
    {
        for (const string& prefix : {string(""), string("(+) "), string("@2> ")})
        {
            GroupLayout layout;
            TriggerButton button;
            const string value = prefix + name;
            component_label(layout, button, value);
            if (!button.widget || button.widget->label != value)
            {
                std::cerr << "Component label changed: " << value << '\n';
                ++failures;
            }
            check(layout.group.children.size() == 1, "Widget count changed");
            check(layout.m_X == 0 && layout.m_Y == layout.m_StdHeight, "Button placement changed");
            check(button.widget->w == 200 && button.widget->h == 20, "Button dimensions changed");
        }
        GroupLayout layout;
        Fl_Box* box = user_group_label(layout, name);
        if (box->label != name)
        {
            std::cerr << "User group changed: " << name << '\n';
            ++failures;
        }
        check(layout.group.children.size() == 1, "Widget count changed");
        check(layout.m_X == 0 && layout.m_Y == layout.m_DividerHeight, "Divider placement changed");
        check(box->w == 200 && box->h == 15, "Divider dimensions changed");
        GroupLayout extra_layout;
        excrescence_label(extra_layout, name);
        Widget* extra = extra_layout.group.children.back();
        if (extra->label != name)
        {
            std::cerr << "Excrescence label changed: " << name << '\n';
            ++failures;
        }
        check(extra->output == kLabelOutputOnly, "Excrescence output flag changed");
        check(extra->w == 145 && extra_layout.m_X == 145 && extra_layout.m_Y == 0,
              "Excrescence label placement changed");
    }
    // Static captions must still be translated, without translating user data.
    GroupLayout layout;
    TriggerButton static_button;
    layout.AddButton(static_button, "Fuselage", 17);
    if (static_button.widget->label != "机身") ++failures;
    if (layout.AddDividerBox("Wing", 17)->label != "机翼") ++failures;
    check(static_button.widget->w == 183, "Static used-width handling changed");
    layout.AddLabel("Wing", 71, 77);
    Widget* static_label = layout.group.children.back();
    check(static_label->label == "机翼", "Static AddLabel translation disabled");
    check(static_label->output == kLabelOutputOnly && static_label->background == 77 && static_label->w == 71,
          "Static label properties changed");
    if (failures) return 1;
    std::cout << "Production button/divider/label paths preserve 85 opaque labels; static translation and layout pass\n";
}
