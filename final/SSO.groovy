import geb.Page

class SSO extends Page {

    static url = "https://projectby.trainings.dlabanalytics.com/kpankov203/"

    static at = {
        waitFor(30) { title == "Log in to dlab" }
    }

    static content = {
        epamSSOButton { $("a#zocial-epam-idp.zocial.saml") }
    }

}