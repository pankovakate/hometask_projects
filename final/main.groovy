import geb.Browser

System.setProperty("webdriver.chrome.driver", "C:\\Users\\Kate_Pankova\\Desktop\\DQE_Mentoring\\Final_Task\\chromedriver.exe")

Browser.drive {

    dlab = { page SSO }
    jupyter = { page Jupyter }
    jupyterNotebook = { page JupyterNotebook }

    to SSO
    dlab.epamSSOButton.click()

    at Jupyter
    waitFor() { jupyter.folder.displayed }
    jupyter.folder.click()

    ArrayList<String> tabs = new ArrayList<String>(driver.getWindowHandles());
    driver.switchTo().window(tabs.get(1));
    driver.get("https://projectby.trainings.dlabanalytics.com/kpankov203/notebooks/DQ_Checks.ipynb")

    at JupyterNotebook

    jupyterNotebook.cellButton.click()
    jupyterNotebook.runAllActionItem.click()

    waitFor() { $("div.output_subarea.output_html.rendered_html.output_result").displayed }

}
