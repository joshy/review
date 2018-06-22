$(function () {
    if ('treeMap' === $('body').data('page')) {
    }

});


function treeMapModuleLoaded() {
    com.macrofocus.treemap.TreeMap.setLicenseKey("Kevin Streiter",
        "TG2GS-W57BU-4CLVB-866AK-QQFBT-DGV3W");
    treeMap = new com.macrofocus.treemap.TreeMap("treeMap");
    treeMap.loadJsonString("{\"data\": [" +
        "{\"Name\": \"Hello\", \"Value\": 12, \"Strength\": 3.0}, " +
        "{\"Name\": \"from\", \"Value\": 11, \"Strength\": 4.0}, " +
        "{\"Name\": \"the\", \"Value\": 9, \"Strength\": 5.0}, " +
        "{\"Name\": \"TreeMap\", \"Value\": 8, \"Strength\": 6.0}, " +
        "{\"Name\": \"World!\", \"Value\": 7, \"Strength\": 7.0}" +
        "]}");

}

function treeMapModelLoaded() {
    treeMap.setToolTipByNames("Name", "Industry", "Value", "Strength");
    var treeMapModel = treeMap.getModel();
    var treeMapSettings = treeMapModel.getSettings();
    var fieldSettings = treeMapSettings.getDefaultFieldSettings();
    fieldSettings.setAlgorithm(com.macrofocus.treemap.AlgorithmFactory.SQUARIFIED);
}


