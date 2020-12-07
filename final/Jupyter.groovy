import geb.Page

class Jupyter extends Page {

    static at = {
        waitFor(30) { title == "Home Page - Select or create a notebook" }
    }

    static content = {
        folder { $("div.col-md-12 a.item_link span", text: "DQ_Checks.ipynb") }
    }

}