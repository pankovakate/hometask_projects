import geb.Page

class JupyterNotebook extends Page {

    static at = {
        waitFor() { title == "DQ_Checks - Jupyter Notebook" }
    }

    static base = {
        $("div.navbar-collapse.collapse")
    }

    static content = {
        cellButton { $("ul.nav.navbar-nav li.dropdown a.dropdown-toggle", text: "Cell") }
        runAllActionItem { $("ul.nav.navbar-nav li.dropdown.open li[id='run_all_cells']") }
    }
}